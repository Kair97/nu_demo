#!/bin/sh
set -eu

mkdir -p /backups

while true; do
    ts=$(date +%Y%m%d_%H%M%S)
    echo "[backup] $ts starting"

    pg_dump -Fc "$PGDATABASE" > "/backups/${PGDATABASE}_${ts}.dump" \
        && echo "[backup] db dump ok" \
        || echo "[backup] pg_dump FAILED"

    tar -C /var/lib/odoo/.local/share/Odoo -czf "/backups/filestore_${PGDATABASE}_${ts}.tar.gz" "filestore/${PGDATABASE}" 2>/dev/null \
        && echo "[backup] filestore tar ok" \
        || echo "[backup] filestore tar skipped (no filestore yet?)"

    find /backups -name "${PGDATABASE}_*.dump" -mtime +14 -delete
    find /backups -name "filestore_${PGDATABASE}_*.tar.gz" -mtime +14 -delete

    echo "[backup] $ts done, sleeping 24h"
    sleep 86400
done
