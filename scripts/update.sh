#!/usr/bin/env bash
# Update to the ERPNEXT_VERSION in .env. Always takes a backup first.
set -euo pipefail
cd "$(dirname "$0")/.."
set -a; . ./.env; set +a

./scripts/backup.sh
docker compose build --pull
docker compose up -d
docker compose exec -T backend bench --site "${SITE_NAME}" migrate
echo "Updated. If something is wrong: restore the backup and set the previous ERPNEXT_VERSION."
