from datetime import datetime
from airflow import DAG
from airflow.providers.standard.operators.bash import BashOperator 

# Define the absolute path to your dbt project directory
DBT_PROJECT_DIR = "/opt/airflow/hr-platform/dbt"

with DAG(
    dag_id="Transformation",
    catchup=False,
    start_date=datetime(2026, 1, 1), 
    schedule=None,                 
) as dag:
    
    Run_Seeds = BashOperator(
        task_id="Run_Seeds",
        cwd=DBT_PROJECT_DIR,        
        bash_command="dbt seed --target prod"
    )

    Run_Silver_Models = BashOperator(
        task_id="Run_Silver_Models",
        cwd=DBT_PROJECT_DIR,
        bash_command="dbt run --select silver intermediate --target prod"
    )

    Run_Quarantine_Models = BashOperator(
        task_id="Run_Quarantine_Models",
        cwd=DBT_PROJECT_DIR,
        bash_command="dbt run --select quarntine --target prod" 
    )

    Run_Post_Silver_Test = BashOperator(
        task_id="Run_Post_Silver_Tests",
        cwd=DBT_PROJECT_DIR,
        bash_command="dbt test --select path:tests/post_silver_tests --target prod"
    )

    Run_Gold_Models = BashOperator(
        task_id="Run_Gold_Models",
        cwd=DBT_PROJECT_DIR,
        bash_command="dbt run --select gold --target prod"
    )

    Run_Post_Gold_Tests = BashOperator(
        task_id="Run_Post_Gold_Tests",
        cwd=DBT_PROJECT_DIR,
        bash_command="dbt test --select path:tests/post_gold_tests --target prod"
    )

    Run_Metrics = BashOperator(
        task_id="Run_Metrics",
        cwd=DBT_PROJECT_DIR,
        bash_command="dbt run --select metrics --target prod"
    )

    Run_Seeds >> Run_Silver_Models >> Run_Quarantine_Models >> Run_Post_Silver_Test >> Run_Gold_Models >> Run_Post_Gold_Tests >> Run_Metrics
