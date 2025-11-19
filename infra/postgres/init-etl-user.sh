#!/bin/bash
set -e

# This script is run automatically by the official Postgres image
# on first container initialization (when the data dir is empty).

echo "Creating ETL role and database..."

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    DO
    \$do\$
    BEGIN
        IF NOT EXISTS (
            SELECT FROM pg_catalog.pg_roles WHERE rolname = '${ETL_DB_USER}'
        ) THEN
            CREATE ROLE ${ETL_DB_USER} LOGIN PASSWORD '${ETL_DB_PASSWORD}';
        END IF;
    END
    \$do\$;

    DO
    \$do\$
    BEGIN
        IF NOT EXISTS (
            SELECT FROM pg_database WHERE datname = '${ETL_DB_NAME}'
        ) THEN
            CREATE DATABASE ${ETL_DB_NAME}
                OWNER ${ETL_DB_USER};
        END IF;
    END
    \$do\$;
EOSQL

echo "ETL role and database created (or already present)."
