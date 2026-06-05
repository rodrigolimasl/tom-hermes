---
name: hermes-agent-backup-review
description: >-
  Review, validate, and maintain backup scripts that mirror Hermes Agent
  operational state (config, skills, memories, SOUL, scripts, hooks, plans)
  to external storage (GitHub, S3, etc.). Covers scope auditing, bug detection,
  and best-practice checklist.
category: devops
trigger: reviewing backup scripts for Hermes Agent state, auditing backup scope, maintaining operational backup workflows
---

# Hermes Agent Backup Review

Review, validate, and maintain backup scripts (`backup-*.sh`) that mirror
Hermes Agent operational state to external storage (GitHub, S3, etc.).

## Trigger Conditions

- User presents a backup script for review or asks "is this backup complete?"
- User wants to set up backup for a new Hermes instance
- User asks about what should/shouldn't be included in state backup
- User wants to restore from backup and needs scope analysis

## Review Process

### 1. Read the script and verify structure

```bash
bash -n script_path          # syntax validation
ls -la script_path           # permissions (must be executable)
```

### 2. Verify backup scope completeness

**MUST include:**

| Item | Source Path | Notes |
|------|-------------|-------|
| config.yaml | `$HERMES_HOME/config.yaml` | MUST sanitize secrets (api_key, token, secret, password, credential, auth fields → empty) |
| SOUL.md | `$HERMES_HOME/SOUL.md` | Check variants: SOUL, SOUL.md, soul.md |
| skills/ | `$HERMES_HOME/skills/` | Recursive `cp -a` |
| scripts/ | `$HERMES_HOME/scripts/` | Recursive `cp -a` (includes self) |
| hooks/ | `$HERMES_HOME/hooks/` | Custom hooks |
| plans/ | `$HERMES_HOME/plans/` | Saved plans |
| cron/ | `$HERMES_HOME/cron/` | Filter: `.json`, `.yaml`, `.yml`, `.md` only |
| memories/ | `$HERMES_HOME/memories/` | Filter: `**/*.md` only (USER.md, MEMORY.md) |
| README.md | generated | Manifest with timestamp and scope |

**MUST NOT include:**

| Item | Reason |
|------|--------|
| .env | Security — contains all credentials/tokens |
| state.db | Security + corruption (can contain leaked credentials from old conversations) + grows unbounded |
| kanban.db | Volatile state (only include if user actively uses Kanban — see below) |
| sessions/, .cache/, cache/, audio_cache/, image_cache/ | Regenerable state |
| gateway.lock, gateway.pid, gateway_state.json | Runtime artifacts |
| *.lock files | Runtime artifacts |
| channel_directory.json | Regenerates on reconnect |

### 3. Check for common bugs

#### Workdir ownership drift (CRITICAL)

**Bug pattern:** The script first runs as `root` (e.g., interactive terminal with sudo), then subsequent runs are as `hermes`. Any persistent path (like `$HERMES_HOME/backups/`) inherits the first run's ownership. Subsequent runs hit `Permission denied` on git operations and log writes.

**Fix: ALWAYS use `/tmp/` for WORKDIR and LOG paths:**
```bash
WORKDIR="/tmp/tom-hermes-backup"
LOG="/tmp/backup-${AGENT}.log"
LOCKDIR="/tmp/backup-${AGENT}.lock"
```

`/tmp/` is always owned by the current process user and gets cleaned on reboot — exactly what you want for ephemeral backup worktrees.

#### Token extraction quoting bug

**Bug pattern:** Combining `tr -d` for stripping quotes AND whitespace in one call creates bash escaping hell:

```bash
# BROKEN — nested quotes conflict with command substitution
GITHUB_TOKEN=*** -E '^GITHUB_TOKEN=*** file | tr -d "\"'[:space:]')"
```

**Correct pattern — three separate `tr -d` calls:**

```bash
GITHUB_TOKEN=*** -E '^GITHUB_TOKEN=*** "$HERMES_HOME/.env" 2>/dev/null | head -1 | cut -d= -f2- | tr -d '"' | tr -d "'" | tr -d '[:space:]')"
```

Each `tr -d` handles one concern. No escaping ambiguity.

#### Trap conflict (CRITICAL)

**Bug pattern:**
```bash
trap 'cleanup...' EXIT       # line A
trap 'error_handler...' ERR  # line B — if same signal, overwrites!
```

If both `trap` statements target the same signal, the second overwrites the first. The real bug we've seen: ERR trap has `exit 1` which triggers EXIT, BUT if EXIT was already overwritten by a subsequent line, cleanup never runs.

**Correct pattern:**
```bash
trap 'rm -f "$ASKPASS"; rmdir "$LOCKDIR" 2>/dev/null || true' EXIT
trap 'echo "FAILED"; log "ERROR"; exit 1' ERR
```

EXIT runs on any exit (success or ERR). ERR runs only on failure and triggers EXIT via `exit 1`. Always verify both traps exist after writing.

#### Config sanitization regex

The sed command for sanitizing `config.yaml` must handle:
- Case-insensitive field name matching (`api_key`, `Api_Key`, `API_KEY`)
- Values with quotes, spaces, special characters
- MUST NOT sanitize non-sensitive fields like `timezone`, `model`, `backend`

**Good pattern:**
```bash
sed -E 's/^([[:space:]]*[^:#]*(api_key|token|secret|password|credential|auth)[^:]*:[[:space:]]*).+$/\1""/I' \
    config.yaml > workdir/config.yaml
```

The `I` flag = case-insensitive. `\1""` = keep field name, replace value with empty.

#### Lock mechanism

```bash
if ! mkdir "$LOCKDIR" 2>/dev/null; then log "já rodando, saindo"; exit 0; fi
```

`mkdir` is atomic for locking — better than `touch` file.

#### Silent-on-success pattern

For `no_agent=true` cron jobs:
- Success = empty stdout + exit code 0 → cron stays silent
- Failure = stdout message + non-zero exit → cron sends alert
- Use `log()` to write to `.log` file (not stdout) for audit trail

### 4. Verify exclusions are enforced

```bash
find "$WORKDIR" -mindepth 1 -maxdepth 1 ! -name .git -exec rm -rf {} +
```

This ensures only explicitly copied items survive.

### 5. Git operations

⚠️ **Crítico:** NUNCA use `HEAD` genérico — causes detached HEAD e push failures.
See `references/git-operations-lessons.md` for detailed pitfalls.

- Clone if new: `git clone -q "https://github.com/${REPO_SLUG}.git" "$WORKDIR"`
- Sync if existing: `git fetch -q origin && git checkout -q -B main origin/main`
  - ❌ NUNCA use `git reset --hard origin/HEAD` (causa detached HEAD → push fails)
  - ✅ Use `git checkout -B main origin/main` (branch explícito)
- Skip commit if no diff: `git diff --cached --quiet`
- Commit message: `backup: Hermes ${AGENT} YYYY-MM-DD HH:MM Timezone`
- Pull antes do push: `git pull --rebase -q origin main`
- Push: `git push -f -q origin main` (force push para repositórios unilaterais de backup)
- Prefer Python para lógica Git complexa: `subprocess.run(..., env=env_dict)` evita escaping hell
- Wrapper bash fino: `set -euo pipefail; exec python3 /opt/data/scripts/backup-tom.py "$@"`

### 6. Document cron jobs

If the instance has active cron jobs, create `/opt/data/cron/cron-jobs.md`
documenting each job so definitions survive a full restore.
See `references/cron-documentation-pattern.md` for the format.

## Pitfalls

1. **Never backup state.db** — even for "complete recovery". It contains conversation history (security risk), grows unbounded, and SQLite requires 3 files (.db + .shm + .wal) for consistency. Backup of config + skills + memories is sufficient for identity restoration.

2. **Sanitization must be verified after backup** — check a known secret field in the backed-up `config.yaml` is actually empty.

3. **Askpass file MUST be world-inaccessible** — `chmod 700` is non-negotiable. The trap MUST clean it on both success AND failure paths.

4. **Kanban.db only if user actively uses Kanban** — include via `sqlite3 kanban.db ".backup file"` not `cp`.

5. **`no_agent=true` is mandatory** for backup cron jobs — no reason to burn LLM tokens on a deterministic script.

## Verification Checklist

After reviewing/applying fixes:
- [ ] `bash -n script_path` passes
- [ ] Script is executable (`chmod +x`)
- [ ] All 9 must-include items covered
- [ ] All must-exclude items properly excluded
- [ ] Both EXIT and ERR traps present and not conflicting
- [ ] Config sanitization regex correct
- [ ] Lock mechanism uses `mkdir`
- [ ] Silent-on-success pattern correct
- [ ] Cron job documentation exists (if jobs active)

## Deliverable Format

When presenting review results to user, use:
1. ✅ What's correct (brief)
2. ⚠️ Potential issues (with severity)
3. 🔧 Concrete fixes proposed
4. 📊 Scope summary table
5. 🏁 Final verdict: "pronto" or "needs changes"