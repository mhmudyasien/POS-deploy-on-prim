#!/usr/bin/env bash
# Usage: scripts/restore.sh backups/2026-10-24_0200
set -euo pipefail
cd "$(dirname "$0")/.."
set -a; . ./.env; set +a

dir="${1:?Usage: restore.sh <backup-dir>}"
db=$(ls "$dir"/*-database.sql.gz)
priv=$(ls "$dir"/*-private-files.tar)
pub=$(ls "$dir"/*-files.tar | grep -v private-files)

read -r -p "This OVERWRITES site ${SITE_NAME}. Type YES to continue: " ok
[ "$ok" = "YES" ] || exit 1

docker compose exec -T backend bash -c "rm -rf /tmp/rs && mkdir /tmp/rs"
docker compose cp "$db" backend:/tmp/rs/
docker compose cp "$priv" backend:/tmp/rs/
docker compose cp "$pub" backend:/tmp/rs/
docker compose exec -T backend bench --site "${SITE_NAME}" --force restore \
  "/tmp/rs/$(basename "$db")" \
  --with-private-files "/tmp/rs/$(basename "$priv")" \
  --with-public-files "/tmp/rs/$(basename "$pub")" \
  --mariadb-root-password "${DB_ROOT_PASSWORD}"
docker compose exec -T backend bench --site "${SITE_NAME}" migrate
echo "Restore done."
