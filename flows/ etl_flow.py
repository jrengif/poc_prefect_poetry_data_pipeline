from prefect import flow

@flow(name="etl_prefect_flow")
def etl_prefect_flow():
    print("Hello from the new flow!")

if __name__ == "__main__":
    etl_prefect_flow.deploy(
        name="my-flow",
        work_pool_name="default-process-pool",
        build=False,
        push=False,
    )