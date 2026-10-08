#!/bin/sh
set -eu

DEPLOY_DIR=/opt/practicarta/deploy
BACKUP_DIR=/opt/practicarta-backups
mkdir -p "$BACKUP_DIR"
cd "$DEPLOY_DIR"

set -a
. ./.env.prod
set +a

timestamp=$(date +%Y%m%d-%H%M%S)
database_file="$BACKUP_DIR/practicarta-$timestamp.sql"

docker compose --env-file .env.prod -f docker-compose.prod.yml exec -T db \
    pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" > "$database_file"
gzip "$database_file"

docker run --rm \
    -v practicarta_media_data:/media:ro \
    -v "$BACKUP_DIR:/backup" \
    alpine tar -czf "/backup/practicarta-media-$timestamp.tar.gz" -C /media .

find "$BACKUP_DIR" -type f -name 'practicarta-*.sql.gz' -mtime +7 -delete
find "$BACKUP_DIR" -type f -name 'practicarta-media-*.tar.gz' -mtime +7 -delete
