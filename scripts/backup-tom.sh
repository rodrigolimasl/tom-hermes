#!/usr/bin/env bash
# backup-tom.sh — wrapper para backup-tom.py
set -euo pipefail
exec python3 /opt/data/scripts/backup-tom.py "$@"
