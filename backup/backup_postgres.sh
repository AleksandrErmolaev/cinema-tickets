#!/bin/bash
BACKUP_DIR="/backups/postgres"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

for DB in users_db booking_db payment_db movies; do
    PGPASSWORD=password pg_dump -h postgres-auth -U user $DB > $BACKUP_DIR/${DB}_$DATE.sql
done

tar -czf $BACKUP_DIR/all_backup_$DATE.tar.gz $BACKUP_DIR/*.sql
find $BACKUP_DIR -type f -name "*.sql" -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete