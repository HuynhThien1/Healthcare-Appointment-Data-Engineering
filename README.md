# Healthcare Appointment Data Engineering

This project demonstrates a real-time data engineering pipeline for a healthcare booking system using PostgreSQL, Debezium, Kafka, Spark Structured Streaming, and ClickHouse.

<!-- Banner -->
<p align="center">
  <a href="https://hcmut.edu.vn/" title="Trường Đại học Bách khoa - ĐHQG-HCM" style="border: none;">
    <img
      src="https://upload.wikimedia.org/wikipedia/commons/thumb/f/f0/HCMCUT.svg/500px-HCMCUT.svg.png"
      alt="Trường Đại học Bách khoa - ĐHQG-HCM | Ho Chi Minh City University of Technology"
      width="220"
    />
  </a>
</p>

## THÀNH VIÊN NHÓM

| STT |   MSSV                          |       Họ và Tên                                            | 
| --- | :------:                          | --------------:                                            | 
| 1   | 2570760 |  Huỳnh Công Thiện                 | 
| 2   | 2570804 | Dương Hoàng Yến            | 
| 3   | 2570771 | Lê Đức Nghĩa            | 


## GIỚI THIỆU MÔN HỌC

-   **Tên môn học:** Data Engineering 
-   **Mã môn học:** Data Engineering (CO3059)
-   **Giảng viên**:  Phan Trong Nhan

## 1. Run the project

### Step 1: Start Docker containers

<pre> docker compose up -d --build docker compose ps -a </pre>

### Step 2: Initialize PostgreSQL

Create database (Postgres database)

<pre> docker compose exec app python -c "from app.create_schema import create_database; create_database()" </pre>

Check databases is created or not?

<pre> docker compose exec postgres psql -U postgres -d postgres -c "\l" </pre>

### Step 4: Create schema and seed data

Create schema

<pre> docker compose exec backend python -c "from app.create_schema import create_schema; create_schema()" </pre>

Check tables create or not?

<pre> docker compose exec postgres psql -U postgres -d healthcare_booking_realtime -c "\dt" </pre>

Seed data into the table

<pre> docker compose exec app python -c "from app.seeds.seed_total import seed_all; seed_all()" </pre>

## 2. CDC Pipeline Setup

### Step 1: Debezium setup

<pre> docker compose exec app python -c "from app.register_connector import wait_for_debezium; wait_for_debezium()" </pre>


<pre> docker compose exec app python -c "from app.register_connector import register_connector; register_connector()" </pre>

### Step 2: Validate Kafka

<pre> docker compose exec broker bash -lc "kafka-topics --bootstrap-server broker:29092 --list" </pre>

### Step 3: Consume CDC events

<pre>
docker compose exec backend python -c "from app.seed_master_data import seed_all; seed_all()"
</pre>

## 3. Initialize ClickHouse

<pre>
docker compose exec backend python -c "from app.db import fetch_all; print(fetch_all('SELECT * FROM doctor LIMIT 5;'))"
</pre>

## 4. Generate CDC Events

<pre>
docker compose exec broker bash -lc "kafka-console-consumer --bootstrap-server broker:29092 --topic healthcare.public.doctor --from-beginning"
</pre>


## 5. Run Spark Streaming

### Run Spark Job 1
<pre>docker compose exec spark-master sh -lc '
mkdir -p /tmp/pylibs /opt/spark/work-dir/.ivy2 && \
pip install --target=/tmp/pylibs python-dotenv && \
export PYTHONPATH=/tmp/pylibs:/app && \
/opt/spark/bin/spark-submit \
--master spark://spark-master:7077 \
--total-executor-cores 4 \
--executor-cores 2 \
--executor-memory 1g \
--conf spark.jars.ivy=/opt/spark/work-dir/.ivy2 \
--conf spark.executorEnv.PYTHONPATH=/tmp/pylibs:/app \
--packages \
org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,\
com.clickhouse:clickhouse-jdbc:0.6.0,\
org.apache.httpcomponents.client5:httpclient5:5.2.1,\
org.apache.httpcomponents.core5:httpcore5:5.2.1 \
/app/spark_jobs/stream_all_cdc_to_staging.py
'
</pre>

### Run Spark Job 2
<pre> 
docker compose exec spark-master sh -lc '
export SYSTEM_START_TIME="$(date -u +"%Y-%m-%d %H:%M:%S")" && \
echo "SYSTEM_START_TIME=$SYSTEM_START_TIME" && \
mkdir -p /tmp/pylibs /opt/spark/work-dir/.ivy2 && \
pip install --target=/tmp/pylibs python-dotenv && \
export PYTHONPATH=/tmp/pylibs:/app && \
/opt/spark/bin/spark-submit \
--master spark://spark-master:7077 \
--total-executor-cores 2 \
--executor-cores 1 \
--executor-memory 1g \
--conf spark.jars.ivy=/opt/spark/work-dir/.ivy2 \
--conf spark.executorEnv.PYTHONPATH=/tmp/pylibs:/app \
--conf spark.executorEnv.SYSTEM_START_TIME="$SYSTEM_START_TIME" \
--packages \
org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,\
com.clickhouse:clickhouse-jdbc:0.6.0,\
org.apache.httpcomponents.client5:httpclient5:5.2.1,\
org.apache.httpcomponents.core5:httpcore5:5.2.1 \
/app/spark_jobs/stream_notification_from_transaction.py
'
</pre>


## 6. Run Notification Service
<pre>docker compose exec backend sh -lc '
pip install kafka-python clickhouse-driver psycopg2-binary python-dotenv && \
cd /app && \
PYTHONPATH=/app python -m app.notification_service
'</pre>





 

