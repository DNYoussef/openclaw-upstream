#!/usr/bin/env bash
# SQLite database backup script (M7 security audit fix)
# Run daily via Task Scheduler or cron
# Uses sqlite3 .backup for hot-safe copies

set -euo pipefail

BACKUP_DIR="$HOME/.claude/backups/db"
DATE=$(date +%Y%m%d)
KEEP_DAYS=14

mkdir -p "$BACKUP_DIR"

DBS=(
  "$HOME/.claude/outreach/outreach.db"
  "$HOME/.claude/memory-mcp-data/agent_kv.db"
  "D:/Projects/guardspine-landing/data/guardspine.db"
)

for db in "${DBS[@]}"; do
  if [ -f "$db" ]; then
    name=$(basename "$db" .db)
    dest="$BACKUP_DIR/${name}_${DATE}.db"
    # Use sqlite3 .backup for consistency (no partial writes)
    if command -v sqlite3 &>/dev/null; then
      sqlite3 "$db" ".backup '$dest'"
    else
      cp "$db" "$dest"
    fi
    echo "[backup] $name -> $dest"
  else
    echo "[skip] $db not found"
  fi
done

# Prune old backups
find "$BACKUP_DIR" -name "*.db" -mtime +$KEEP_DAYS -delete 2>/dev/null || true
echo "[done] Backups in $BACKUP_DIR, pruning after ${KEEP_DAYS} days"
