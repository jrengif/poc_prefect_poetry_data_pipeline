#!/usr/bin/env python
"""
Initialize star-schema tables in a Postgres database.

Intended to be run once when the Postgres container starts,
before loading any CSV data.
"""

import os
import sys

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


def get_connection():
    """
    Connect to Postgres using environment variables.

    Priority:
    1. PGHOST / PGPORT / PGDATABASE / PGUSER / PGPASSWORD  (e.g. from docker-compose service)
    2. POSTGRES_HOST / POSTGRES_PORT / POSTGRES_DB
       ETL_DB_USER / ETL_DB_PASSWORD  (from your .env)
    3. POSTGRES_USER / POSTGRES_PASSWORD as a final fallback
    """

    host = (
        os.getenv("PGHOST")
        or os.getenv("POSTGRES_HOST")
        or "localhost"
    )

    port = (
        os.getenv("PGPORT")
        or os.getenv("POSTGRES_PORT")
        or "5432"
    )

    dbname = (
        os.getenv("PGDATABASE")
        or os.getenv("POSTGRES_DB")
        or "postgres"
    )

    # Prefer ETL user (limited permissions) if available
    user = (
        os.getenv("PGUSER")
        or os.getenv("ETL_DB_USER")
        or os.getenv("POSTGRES_USER")
        or "postgres"
    )

    password = (
        os.getenv("PGPASSWORD")
        or os.getenv("ETL_DB_PASSWORD")
        or os.getenv("POSTGRES_PASSWORD")
        or ""
    )

    db_params = {
        "host": host,
        "port": port,
        "dbname": dbname,
        "user": user,
        "password": password,
    }

    print(
        f"Connecting to Postgres as '{user}' on "
        f"{host}:{port} / db='{dbname}'"
    )
    conn = psycopg2.connect(**db_params)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    return conn


DDL_STATEMENTS = [

    # 1. Dimension tables (no FKs, or FKs only to earlier dims)

    # dim_industry
    """
    CREATE TABLE IF NOT EXISTS dim_industry (
        industry_key      BIGSERIAL PRIMARY KEY,
        industry_name     TEXT NOT NULL
    );
    """,

    # dim_person
    """
    CREATE TABLE IF NOT EXISTS dim_person (
        person_key        BIGSERIAL PRIMARY KEY,
        profile_url       TEXT NOT NULL UNIQUE,
        first_name        TEXT,
        last_name         TEXT,
        profile_image_url TEXT,
        twitter_handle    TEXT,
        github_handle     TEXT
    );
    """,

    # dim_location
    """
    CREATE TABLE IF NOT EXISTS dim_location (
        location_key  BIGSERIAL PRIMARY KEY,
        raw_location  TEXT NOT NULL,
        city          TEXT,
        region        TEXT,
        country       TEXT
    );
    """,

    # dim_job_role
    """
    CREATE TABLE IF NOT EXISTS dim_job_role (
        job_role_key BIGSERIAL PRIMARY KEY,
        job_title    TEXT NOT NULL,
        headline     TEXT
    );
    """,

    # dim_email
    """
    CREATE TABLE IF NOT EXISTS dim_email (
        email_key     BIGSERIAL PRIMARY KEY,
        email_address TEXT NOT NULL,
        email_type    TEXT,
        is_valid      BOOLEAN,
        is_current    BOOLEAN
    );
    """,

    # dim_company (depends on dim_industry)
    """
    CREATE TABLE IF NOT EXISTS dim_company (
        company_key          BIGSERIAL PRIMARY KEY,
        company_name         TEXT NOT NULL,
        company_linkedin_url TEXT,
        company_domain       TEXT,
        industry_key         BIGINT REFERENCES dim_industry(industry_key)
    );
    """,

    # dim_date (calendar dimension – you’ll populate it separately)
    """
    CREATE TABLE IF NOT EXISTS dim_date (
        date_key     INTEGER PRIMARY KEY,   -- e.g. 20251119
        full_date    DATE    NOT NULL,
        year         SMALLINT NOT NULL,
        month        SMALLINT NOT NULL,
        day          SMALLINT NOT NULL,
        weekday_name TEXT    NOT NULL
    );
    """,

    # 2. Fact table

    """
    CREATE TABLE IF NOT EXISTS fact_profile_snapshot (
        profile_snapshot_key BIGSERIAL PRIMARY KEY,

        person_key           BIGINT   NOT NULL REFERENCES dim_person(person_key),
        company_key          BIGINT            REFERENCES dim_company(company_key),
        job_role_key         BIGINT            REFERENCES dim_job_role(job_role_key),
        location_key         BIGINT            REFERENCES dim_location(location_key),
        industry_key         BIGINT            REFERENCES dim_industry(industry_key),
        snapshot_date_key    INTEGER  NOT NULL REFERENCES dim_date(date_key),

        has_work_email       BOOLEAN  NOT NULL DEFAULT FALSE,
        work_email_count     INTEGER  NOT NULL DEFAULT 0,
        has_twitter          BOOLEAN  NOT NULL DEFAULT FALSE,
        has_github           BOOLEAN  NOT NULL DEFAULT FALSE
    );
    """,

    # 3. Helpful indexes on foreign keys for joins

    "CREATE INDEX IF NOT EXISTS idx_fact_person        ON fact_profile_snapshot(person_key);",
    "CREATE INDEX IF NOT EXISTS idx_fact_company       ON fact_profile_snapshot(company_key);",
    "CREATE INDEX IF NOT EXISTS idx_fact_job_role      ON fact_profile_snapshot(job_role_key);",
    "CREATE INDEX IF NOT EXISTS idx_fact_location      ON fact_profile_snapshot(location_key);",
    "CREATE INDEX IF NOT EXISTS idx_fact_industry      ON fact_profile_snapshot(industry_key);",
    "CREATE INDEX IF NOT EXISTS idx_fact_snapshot_date ON fact_profile_snapshot(snapshot_date_key);",
]


def run_ddl(conn):
    with conn.cursor() as cur:
        for ddl in DDL_STATEMENTS:
            ddl_clean = " ".join(ddl.split())
            print(f"Running DDL: {ddl_clean[:80]}...")
            cur.execute(ddl)
    print("All tables and indexes created (or already existed).")


def main():
    try:
        conn = get_connection()
    except Exception as e:
        print("❌ Could not connect to Postgres:", e)
        sys.exit(1)

    try:
        run_ddl(conn)
    except Exception as e:
        print("❌ Error while running DDL:", e)
        sys.exit(2)
    finally:
        conn.close()
        print("Connection closed.")


if __name__ == "__main__":
    main()
