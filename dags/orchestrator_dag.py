from airflow.sdk import dag 
from airflow.providers.standard.operators.trigger_dagrun import TriggerDagRunOperator 

@dag(dag_id="orchestrator_dag")
def orchestrator_dag():

    trigger_extrcat_and_load_dag = TriggerDagRunOperator(
        task_id = "trigger_extrcat_and_load_dag",
        trigger_dag_id="Extract_And_Load",
        wait_for_completion=True
    )

    trigger_transformation_dag = TriggerDagRunOperator(
        task_id = "trigger_transformation_dag",
        trigger_dag_id="Transformation"
    )

    trigger_extrcat_and_load_dag >> trigger_transformation_dag 

orchestrator_dag() 
