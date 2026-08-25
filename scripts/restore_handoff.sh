#!/usr/bin/env bash
# Restore a handoff snapshot (database + attachments) into a fresh nu_demo stack.
#
#   ./scripts/restore_handoff.sh backups/handoff_nu_demo_<ts>.dump \
#                                backups/handoff_filestore_nu_demo_<ts>.tar.gz
#
# Run it from the project root, with the stack already up (docker compose up -d).

set -euo pipefail

# Git Bash / MSYS on Windows rewrites anything that looks like a unix path
# ("/tmp/restore.dump") into a Windows path before handing it to docker, so the
# command lands inside the container pointing at C:/Users/... and silently finds
# nothing. Turn that translation off for this whole script.
export MSYS_NO_PATHCONV=1
export MSYS2_ARG_CONV_EXCL='*'

DUMP="${1:-}"
FILESTORE="${2:-}"

if [ -z "$DUMP" ] || [ -z "$FILESTORE" ]; then
    echo "Usage: $0 <db .dump> <filestore .tar.gz>" >&2
    echo "Example:" >&2
    echo "  $0 backups/handoff_nu_demo_20260825_083551.dump \\" >&2
    echo "     backups/handoff_filestore_nu_demo_20260825_083551.tar.gz" >&2
    exit 1
fi

for f in "$DUMP" "$FILESTORE"; do
    [ -f "$f" ] || { echo "ERROR: no such file: $f" >&2; exit 1; }
done

[ -f .env ] || { echo "ERROR: .env missing. Copy .env.example to .env first." >&2; exit 1; }
# shellcheck disable=SC1091
set -a; . ./.env; set +a
DB="${POSTGRES_DB_NAME:-nu_demo}"
PGUSER_="${POSTGRES_USER:-odoo}"

echo "==> Checking the stack is running"
docker compose ps --status running --services | grep -qx db   || { echo "ERROR: 'db' not running. Run: docker compose up -d" >&2; exit 1; }
docker compose ps --status running --services | grep -qx odoo || { echo "ERROR: 'odoo' not running. Run: docker compose up -d" >&2; exit 1; }

echo "==> Stopping Odoo so nothing holds a connection to '$DB'"
docker compose stop odoo >/dev/null

echo "==> Copying snapshot into the containers"
docker compose cp "$DUMP" db:/tmp/restore.dump
docker compose cp "$FILESTORE" odoo:/tmp/restore_filestore.tar.gz

# Prove the file really landed inside the container before touching the database,
# so a path problem can never be mistaken for a successful restore.
docker compose exec -T db test -s /tmp/restore.dump \
    || { echo "ERROR: dump did not reach the db container. Aborting before dropping anything." >&2; exit 1; }

echo "==> Dropping and recreating '$DB'"
docker compose exec -T db psql -U "$PGUSER_" -d postgres -v ON_ERROR_STOP=1 -c \
    "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '$DB' AND pid <> pg_backend_pid();" >/dev/null
docker compose exec -T db psql -U "$PGUSER_" -d postgres -v ON_ERROR_STOP=1 -c "DROP DATABASE IF EXISTS \"$DB\";" >/dev/null
docker compose exec -T db psql -U "$PGUSER_" -d postgres -v ON_ERROR_STOP=1 -c "CREATE DATABASE \"$DB\" OWNER \"$PGUSER_\";" >/dev/null

echo "==> Restoring the database (this takes a minute)"
docker compose exec -T db pg_restore -U "$PGUSER_" -d "$DB" --no-owner --no-privileges /tmp/restore.dump

echo "==> Verifying the restore actually landed"
TABLES=$(docker compose exec -T db psql -U "$PGUSER_" -d "$DB" -t -A \
    -c "select count(*) from information_schema.tables where table_schema='public';" | tr -d '\r')
if [ "${TABLES:-0}" -lt 100 ]; then
    echo "ERROR: only ${TABLES} tables restored -- something went wrong." >&2
    exit 1
fi
echo "    $TABLES tables restored"

echo "==> Restoring attachments (filestore)"
docker compose start odoo >/dev/null
sleep 3
docker compose exec -T odoo sh -c \
    "mkdir -p /var/lib/odoo/.local/share/Odoo && tar -xzf /tmp/restore_filestore.tar.gz -C /var/lib/odoo/.local/share/Odoo"

echo "==> Restarting Odoo"
docker compose restart odoo >/dev/null
sleep 8

echo
echo "Done. Open http://localhost:8069"
echo "  admin / NuDemo2026!             (full administrator)"
echo "  staff@nu.edu.kz / NuDemo2026!   (ordinary employee, for showing role differences)"
