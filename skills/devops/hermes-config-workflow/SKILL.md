---
name: hermes-config-workflow
description: "Safe workflow for configuring Hermes Agent: consult docs, propose, wait for approval, execute via CLI. Prevents unauthorized changes, config corruption, and environment mismatch."
version: 1.0.0
---

# Hermes Config Workflow

The Hermes Agent is a production system. Config changes can break sessions, lose tools, or expose credentials. This skill codifies the safe workflow the user (Rodrigo) requires for ANY configuration task involving Hermes.

## Trigger

Load this skill whenever the task involves changing any of:
- `~/.hermes/config.yaml` or `~/.hermes/.env`
- STT, TTS, model, provider, toolsets, gateway, memory, skills, profiles
- Any feature enabled/disabled in the Hermes runtime

## Core Rules

### 1. Consult docs FIRST — before ANY action

Always load the bundled `hermes-agent` skill via `skill_view(name='hermes-agent')` BEFORE reading config, proposing changes, or running commands. The bundled skill has the authoritative CLI reference, config sections, provider list, and troubleshooting guide. Never guess syntax.

Also check the live config: read `config.yaml` at the session's `$HERMES_HOME/config.yaml` (echo `hermes config path` to find it — DO NOT assume `~/.hermes/` since `HERMES_HOME` may be overridden).

### 2. Propose BEFORE executing

Present the user with:
- What config key(s) will change
- Current value → proposed value
- Expected effect
- Any gotchas (restart needed, session reset, dependency installs)

**Wait for explicit approval.** Do not execute the command until the user says go.

### 3. Use CLI, never edit config.yaml directly

The agent tool `patch` / `write_file` is BLOCKED for Hermes config files. Always use:

```bash
/opt/hermes/.venv/bin/hermes config set <section.key> <value>
```

or the interactive wizard (`hermes config edit`). This is by design — the agent cannot directly modify sensitive config.

### 4. Environment quirks

- `hermes` CLI may NOT be in `$PATH` (session runs via gateway, not CLI). Use `/opt/hermes/.venv/bin/hermes` as fallback.
- `$HERMES_HOME` may differ from `$HOME/.hermes`. Use `hermes config path` to resolve.
- The venv at `/opt/hermes/.venv/` does NOT have `pip`. Use `/opt/hermes/.venv/bin/python3 -m pip` or `uv pip` if available.
- `faster-whisper` must be installed in the Hermes venv, not system Python, because the gateway runs inside it.

## Common Patterns

```bash
# Find config
/opt/hermes/.venv/bin/hermes config path

# Set STT
/opt/hermes/.venv/bin/hermes config set stt.enabled true
/opt/hermes/.venv/bin/hermes config set stt.provider local

# Set TTS voice
/opt/hermes/.venv/bin/hermes config set tts.edge.voice pt-BR-AntonioNeural

# Check health
/opt/hermes/.venv/bin/hermes doctor

# Install packages in Hermes venv
/opt/hermes/.venv/bin/python3 -m pip install <package>
```

## Anti-patterns (do NOT do these)

- ❌ Edit `config.yaml` with `patch` / `write_file` — blocked by safety guard
- ❌ Assume `hermes` is in PATH — use full path
- ❌ Install packages in system Python — the gateway runs in Hermes venv
- ❌ Skip documentation consultation — the bundled skill has the commands
- ❌ Auto-execute without user approval — propose first

## Post-change

After applying config changes, remind user about activation:
- Gateway running → `/restart` in gateway session
- CLI running → exit and relaunch
- Tool changes → `/reset` to start new session with updated toolset
