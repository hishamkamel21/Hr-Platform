FROM apache/airflow:3.2.2-python3.11

USER root

RUN mkdir -p /opt/airflow/hr-platform && chown -R airflow:root /opt/airflow/hr-platform

USER airflow

WORKDIR /opt/airflow/hr-platform

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ./added_package ./added_package

COPY ./DBT/dbt_hr ./dbt

ENV PYTHONPATH=/opt/airflow/hr-platform

WORKDIR /opt/airflow 



