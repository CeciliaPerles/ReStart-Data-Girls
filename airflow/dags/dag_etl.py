from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

with DAG(
    dag_id="etl_pipeline",
    start_date=datetime(2025, 8, 10),
    schedule="0 6 * * *",
    catchup=False,
) as dag:

    run_etl = BashOperator(
        task_id="run_main",
        bash_command="cd /opt/airflow/project && python main.py"
    )