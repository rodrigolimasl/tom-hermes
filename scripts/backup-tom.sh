#!/usr/bin/env bash
# backup-tom.sh — espelho seletivo do estado operacional do Hermes "Tom" -> repo privado no GitHub.
# Roda DENTRO do contêiner Hermes (cron no_agent) sobre /opt/data (HERMES_HOME).
# Sucesso = stdout vazio (cron silencioso). Falha = stdout + exit!=0 (cron alerta).
set -euo pipefail

HERMES_HOME="${HERMES_HOME:-/opt/data}"
REPO_SLUG="rodrigolimasl/tom-hermes"
WORKDIR="$HERMES_HOME/backups/tom-hermes"
LOG="$HERMES_HOME/backups/backup-tom.log"
AGENT="Tom"
LOCKDIR="/tmp/backup-${AGENT}.lock"

mkdir -p "$HERMES_HOME/backups"
log(){ echo "$(date '+%F %T') $*" >> "$LOG"; }

if ! mkdir "$LOCKDIR" 2>/dev/null; then log "já rodando, saindo"; exit 0; fi
ASKPASS=""
trap 'rm -f "$ASKPASS" 2>/dev/null; rmdir "$LOCKDIR" 2>/dev/null || true' EXIT
trap 'echo "[$AGENT] backup FALHOU (veja $LOG)"; log "FALHOU"' ERR

GITHUB_TOKEN="$(grep -E '^GITHUB_TOKEN=' "$HERMES_HOME/.env" 2>/dev/null | head -1 | cut -d= -f2- | tr -d "\"'[:space:]")"
[ -n "${GITHUB_TOKEN:-}" ] || { echo "[$AGENT] ERRO: GITHUB_TOKEN ausente"; log "ERRO: token ausente"; exit 1; }

ASKPASS="$(mktemp)"
printf '#!/usr/bin/env bash\ncase "$1" in *Username*) echo x-access-token;; *Password*) echo "%s";; esac\n' "$GITHUB_TOKEN" > "$ASKPASS"
chmod 700 "$ASKPASS"; export GIT_ASKPASS="$ASKPASS" GIT_TERMINAL_PROMPT=0

if [ -d "$WORKDIR/.git" ]; then
  git -C "$WORKDIR" fetch -q origin && git -C "$WORKDIR" reset -q --hard origin/HEAD 2>/dev/null || true
else
  git clone -q "https://github.com/${REPO_SLUG}.git" "$WORKDIR"
fi

find "$WORKDIR" -mindepth 1 -maxdepth 1 ! -name .git -exec rm -rf {} +

[ -f "$HERMES_HOME/config.yaml" ] && \
  sed -E 's/^([[:space:]]*[^:#]*(api_key|token|secret|password|credential|auth)[^:]*:[[:space:]]*).+$/\1""/I' \
      "$HERMES_HOME/config.yaml" > "$WORKDIR/config.yaml"

for s in SOUL SOUL.md soul.md; do [ -f "$HERMES_HOME/$s" ] && cp "$HERMES_HOME/$s" "$WORKDIR/"; done

[ -d "$HERMES_HOME/skills" ]  && cp -a "$HERMES_HOME/skills"  "$WORKDIR/"
[ -d "$HERMES_HOME/scripts" ] && cp -a "$HERMES_HOME/scripts" "$WORKDIR/"

[ -d "$HERMES_HOME/cron" ] && ( cd "$HERMES_HOME" && \
  find cron -type f \( -name '*.json' -o -name '*.yaml' -o -name '*.yml' -o -name '*.md' \) -exec cp --parents {} "$WORKDIR/" \; )

[ -d "$HERMES_HOME/memories" ] && ( cd "$HERMES_HOME" && \
  find memories -type f -name '*.md' -exec cp --parents {} "$WORKDIR/" \; )

cat > "$WORKDIR/README.md" <<EOF
# Backup operacional — Hermes ($AGENT)
Espelho seletivo do estado operacional do Hermes. NAO e backup do sistema inteiro.
- Ultimo backup: $(date '+%Y-%m-%d %H:%M %Z')
- Incluido: config.yaml (sanitizado), SOUL, skills/, scripts/, cron/ (defs), memories/**/*.md
- Excluido: .env, tokens, credenciais, sessoes, logs, caches, locks, state DB, temporarios
EOF

cd "$WORKDIR"
git add -A
if git diff --cached --quiet; then log "sem mudancas"; exit 0; fi
git -c user.name="hermes-backup" -c user.email="backup@tom" \
    commit -qm "backup: Hermes $AGENT $(date '+%Y-%m-%d %H:%M') Manaus"
git push -q origin HEAD
log "backup enviado para $REPO_SLUG"
exit 0
