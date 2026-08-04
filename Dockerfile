# ---------------------------------------------------------
# Base image
# Official Apache Airflow image with Python 3.11
# ---------------------------------------------------------
FROM apache/airflow:3.2.2-python3.11

# ---------------------------------------------------------
# Switch to root to create project directories
# ---------------------------------------------------------
USER root

# Create the project directory and grant ownership
# to the airflow user.
RUN mkdir -p /opt/airflow/hr-platform && \
    chown -R airflow:root /opt/airflow/hr-platform

# ---------------------------------------------------------
# Switch back to the non-root airflow user
# ---------------------------------------------------------
USER airflow

# Set the project working directory
WORKDIR /opt/airflow/hr-platform

# ---------------------------------------------------------
# Install Python dependencies
# ---------------------------------------------------------
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# ---------------------------------------------------------
# Copy custom Python modules used by Airflow DAGs
# ---------------------------------------------------------
COPY ./added_package ./added_package

# ---------------------------------------------------------
# Copy the DBT project
# This project will be executed from Airflow DAGs
# ---------------------------------------------------------
COPY ./DBT/dbt_hr ./dbt

# ---------------------------------------------------------
# Make the project modules importable from anywhere
# ---------------------------------------------------------
ENV PYTHONPATH=/opt/airflow/hr-platform

# ---------------------------------------------------------
# Return to the default Airflow working directory
# DAGs are synchronized separately using git-sync
# ---------------------------------------------------------
WORKDIR /opt/airflow