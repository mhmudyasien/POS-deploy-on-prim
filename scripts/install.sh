#!/usr/bin/env bash
# First-time install. Safe to re-run: it skips what already exists.
set -euo pipefail
cd "$(dirname "$0")/.."

command -v docker >/dev/null || { echo "Docker is required"; exit 1; }

if [ ! -f .env ]; then
  cp .env.example .env
  sed -i "s/^DB_ROOT_PASSWORD=.*/DB_ROOT_PASSWORD=$(openssl rand -hex 16)/" .env
  sed -i "s/^ADMIN_PASSWORD=.*/ADMIN_PASSWORD=$(openssl rand -hex 12)/" .env
  echo "Created .env with random passwords. Keep it safe."
fi
set -a; . ./.env; set +a

docker compose up -d --build

echo "Waiting for backend..."
until docker compose exec -T backend bench --version >/dev/null 2>&1; do sleep 3; done

if docker compose exec -T backend test -f "sites/${SITE_NAME}/site_config.json"; then
  echo "Site ${SITE_NAME} already exists, skipping creation."
else
  # Remove any half-created folder left by a failed earlier run
  docker compose exec -T backend rm -rf "sites/${SITE_NAME}"
  docker compose exec -T backend bench new-site "${SITE_NAME}" \
    --db-host db --db-port 3306 \
    --mariadb-root-password "${DB_ROOT_PASSWORD}" \
    --admin-password "${ADMIN_PASSWORD}" \
    --mariadb-user-host-login-scope='%' \
    --install-app erpnext --install-app zatca_core
  docker compose exec -T backend bench --site "${SITE_NAME}" enable-scheduler
fi

echo
echo "Ready: http://localhost:${HTTP_PORT}  (user: Administrator, password in .env)"
