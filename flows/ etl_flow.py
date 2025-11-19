from prefect import flow

@flow(name="etl_postgres_flow")
def etl_postgres_flow():
    ...