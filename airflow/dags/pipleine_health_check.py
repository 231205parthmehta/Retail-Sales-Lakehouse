from datetime import datetime

from airflow.sdk import dag, task

@dag(
    dag_id = "retail_pipleline_health_check",
    schedule=None,
    start_date = datetime(2026, 1, 1),
    catchup=False,
    tags=["retail", "health-check"],
    description="Validates that the retail data platform airflow environment is operational.",

)
def retial_pipleline_health_check():

    @task
    def check_environment():
        print("Retail Sales Lakehouse pipeline is operational.")
        print("Airflow DAG execution succeeded.")

        return "SUCCESS"

    @task
    def validate_pipeline_metadata(status: str):
        if status != "SUCCESS":
            raise ValueError("Pipeline Health Check Failed")

        print("Pipleline metadata validation passed.")

    environment_status = check_environment()

    validate_pipeline_metadata(environment_status)

retial_pipleline_health_check()