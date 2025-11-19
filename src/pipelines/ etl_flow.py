from prefect import flow, task
import psycopg2  # or sqlalchemy, etc.

@task
def extract():
    # dummy example — replace with your real source
    return [{"id": 1, "value": 10}, {"id": 2, "value": 20}]

@task
def transform(rows):
    # simple example transformation
    return [r | {"value_x2": r["value"] * 2} for r in rows]

@task
def load(rows):
    # here you’d connect to your Postgres ETL user using .env vars
    # and insert/update data
    # (left as pseudo-code so you can adapt to your setup)
    print(f"Loading {len(rows)} rows into Postgres...")

@flow(name="etl_postgres_flow")
def etl_postgres_flow():
    raw = extract()
    clean = transform(raw)
    load(clean)


if __name__ == "__main__":
    etl_postgres_flow()
