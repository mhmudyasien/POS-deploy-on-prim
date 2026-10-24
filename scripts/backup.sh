#!/usr/bin/env bash
# Daily backup. Cron example:  0 2 * * * /opt/deploy-onprem/scripts/backup.sh
set -euo pipefail
cd "$(dirname "$0")/.."
set -a; . ./.env; set +a

dest="backups/$(date +%F_%H%M)"
mkdir -p "$dest"

docker compose exec -T backend bash -c \
  "rm -rf /tmp/bk && mkdir /tmp/bk && bench --site ${SITE_NAME} backup --with-files --backup-path /tmp/bk"
docker compose cp backend:/tmp/bk/. "$dest"

# Keep only the last N days locally
find backups -mindepth 1 -maxdepth 1 -type d -mtime +"${BACKUP_KEEP_DAYS:-14}" -exec rm -rf {} +

# Optional off-site copy (HQ server over SSH)
if [ -n "${BACKUP_REMOTE:-}" ]; then
  rsync -a backups/ "${BACKUP_REMOTE}"
fi
echo "Backup saved to $dest"
