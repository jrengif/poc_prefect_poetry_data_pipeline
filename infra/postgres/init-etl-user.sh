#!/bin/bash
set -e

echo "Creating ETL role and granting access..."

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    -- 1) Create ETL role if missing
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

    -- 2) Ensure database exists (if it didn't, owner will be ETL user)
    DO
    \$do\$
    BEGIN
        IF NOT EXISTS (
            SELECT FROM pg_database WHERE datname = '${POSTGRES_DB}'
        ) THEN
            CREATE DATABASE ${POSTGRES_DB}
                OWNER ${ETL_DB_USER};
        END IF;
    END
    \$do\$;
EOSQL

# 3) Now connect to the target DB and grant privileges
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    GRANT CONNECT ON DATABASE ${POSTGRES_DB} TO ${ETL_DB_USER};

    GRANT USAGE ON SCHEMA public TO ${ETL_DB_USER};
    GRANT CREATE ON SCHEMA public TO ${ETL_DB_USER};

    GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO ${ETL_DB_USER};
    ALTER DEFAULT PRIVILEGES IN SCHEMA public
        GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO ${ETL_DB_USER};
EOSQL

echo "ETL role and privileges configured."
