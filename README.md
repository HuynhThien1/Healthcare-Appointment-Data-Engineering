# Healthcare Appointment Data Engineering

This project demonstrates a real-time data engineering pipeline for a healthcare booking system using PostgreSQL, Debezium, Kafka, Spark Structured Streaming, and ClickHouse.

## 1. Run the project

### Step 1: Start Docker containers

<pre> docker compose up -d --build docker compose ps -a </pre>

### Step 2: Validate app configuration

<pre> docker compose exec app python -c "from app.config import *; print(PG_HOST, PG_PORT, PG_ADMIN_DB, PG_APP_DB, KAFKA_BOOTSTRAP_SERVERS, DEBEZIUM_CONNECT_URL)" </pre>

### Step 3: Initialize PostgreSQL

Create database

<pre> docker compose exec app python -c "from app.create_schema import create_database; create_database()" </pre>

Check databases

<pre> docker compose exec postgres psql -U postgres -d postgres -c "\l" </pre>

Test connection

<pre> docker compose exec app python -c "from app.db import get_app_connection; conn=get_app_connection(); print('app db ok'); conn.close()" </pre>

### Step 4: Create schema and seed data

Create schema

<pre> docker compose exec app python -c "from app.create_schema import create_schema; create_schema()" </pre>

Check tables

<pre> docker compose exec postgres psql -U postgres -d healthcare_booking_realtime -c "\dt" </pre>

Seed data

<pre> docker compose exec app python -c "from app.seeds.seed_total import seed_all; seed_all()" </pre>

Check data

<pre> docker compose exec app python -c "from app.db import fetch_all; print(fetch_all('SELECT * FROM doctor LIMIT 5;'))" </pre>

## 2. CDC Pipeline Setup

### Step 1: Validate Debezium

Wait for Debezium

<pre> docker compose exec app python -c "from app.register_connector import wait_for_debezium; wait_for_debezium()" </pre>

<pre>
docker compose exec backend python -c "from app.db import get_app_connection; conn=get_app_connection(); print('app db ok'); conn.close()"
</pre>

<pre> docker compose exec app python -c "from app.register_connector import register_connector; register_connector()" </pre>

Check connector

<pre>
docker compose exec backend python -c "from app.create_schema import create_schema; create_schema()"
</pre>

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

<pre> docker compose exec app python -c "from app.init_clickhouse import init_clickhouse; init_clickhouse()" </pre>

Check ClickHouse

<pre>
docker compose exec backend python -c "from app.register_connector import wait_for_debezium; wait_for_debezium()"
</pre>

## 4. Run Spark Streaming

<pre>
docker compose exec backend python -c "from app.register_connector import register_connector; register_connector()"
</pre>

<pre> docker compose exec spark-master sh -lc ' mkdir -p /tmp/pylibs /opt/spark/work-dir/.ivy2 && \ pip install --target=/tmp/pylibs python-dotenv && \ PYTHONPATH=/tmp/pylibs:/app \ /opt/spark/bin/spark-submit \ --master spark://spark-master:7077 \ --conf spark.jars.ivy=/opt/spark/work-dir/.ivy2 \ --conf spark.executorEnv.PYTHONPATH=/tmp/pylibs:/app \ --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,com.clickhouse:clickhouse-jdbc:0.6.0 \ /app/spark_jobs/stream_all_cdc_to_staging.py ' </pre>

## 5. Generate CDC Events

Option 1

<pre> python -m app.stream_generator </pre>

Option 2

Update

<pre> docker compose exec app python -c "from app.db import execute_query; execute_query(\"UPDATE doctor SET doctor_name='Nguyen Van B', updated_at=NOW() WHERE doctor_id=1001;\"); print('updated doctor')" </pre>

Insert

<pre> docker compose exec app python -c "from app.db import execute_query; execute_query(\"INSERT INTO doctor (doctor_id, doctor_code, doctor_name, specialty, employment_status, created_at, updated_at) VALUES (2003, 'DOC2003', 'Le Van C', 'Neurology', 'ACTIVE', NOW(), NOW());\"); print('inserted doctor')" </pre>

## 6. End-to-End Validation

Expected flow

Insert data into PostgreSQL
Debezium captures CDC
Event pushed to Kafka
Spark consumes event
Data written to ClickHouse

Verify result

<pre> docker compose exec clickhouse clickhouse-client --query "SELECT * FROM healthcare_dw.dim_doctor ORDER BY doctor_id" </pre>

<pre>
docker compose exec backend python -c "from app.init_clickhouse import init_clickhouse; init_clickhouse()"
</pre>

No Kafka event → check Debezium + WAL
Spark empty batch → check Kafka topic
ClickHouse insert fail → check schema + JDBC
App cannot connect DB → check PG_HOST, network

## 8. Notes


h2. 3. Spark streaming job

h3. Step 1: Remove old checkpoint

<pre>
docker compose exec spark-master sh -lc 'rm -rf /tmp/checkpoints/stream_doctor_to_dw'
</pre>

h3. Step 2: Submit Spark job

<pre>
docker compose exec spark-master sh -lc '
mkdir -p /tmp/pylibs /opt/spark/work-dir/.ivy2 && \
pip install --target=/tmp/pylibs python-dotenv && \
PYTHONPATH=/tmp/pylibs:/app \
/opt/spark/bin/spark-submit \
  --master spark://spark-master:7077 \
  --conf spark.jars.ivy=/opt/spark/work-dir/.ivy2 \
  --conf spark.executorEnv.PYTHONPATH=/tmp/pylibs:/app \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,com.clickhouse:clickhouse-jdbc:0.6.0 \
  /app/spark_jobs/stream_doctor_to_dw.py
'
</pre>


h2. 4. End-to-end CDC test

h3. 4.1 Consume CDC events from Kafka

Run consumer command:

<pre>
docker compose exec broker bash -lc "kafka-console-consumer --bootstrap-server broker:29092 --topic healthcare.public.doctor --from-beginning"
</pre>

h3. 4.2 Update existing PostgreSQL data

In another terminal:

<pre>
docker compose exec backend python -c "from app.db import execute_query; execute_query(\"UPDATE doctor SET doctor_name='Nguyen Van B', updated_at=NOW() WHERE doctor_id=1001;\"); print('updated doctor')"
</pre>

Expected result:
* New CDC event appears in Kafka consumer
* Debezium connector remains in RUNNING state

h3. 4.3 Insert new PostgreSQL data

In another terminal:

<pre>
docker compose exec backend python -c "from app.db import execute_query; execute_query(\"INSERT INTO doctor (doctor_id, doctor_code, doctor_name, specialty, employment_status, created_at, updated_at) VALUES (2003, 'DOC2003', 'Le Van C', 'Neurology', 'ACTIVE', NOW(), NOW());\"); print('inserted doctor')"
</pre>

Expected result:
* New CDC event appears in Kafka
* Spark job reads the event
* New row is written into ClickHouse table

h3. 4.4 Verify ClickHouse output

<pre>
docker compose exec clickhouse clickhouse-client --query "SELECT * FROM healthcare_dw.dim_doctor ORDER BY doctor_id"
</pre>


h2. 5. Full reset / debug flow

Use this flow when the system is broken and needs a clean restart.

h3. Step 1: Restart all containers

<pre>
docker compose down -v
docker compose up -d --build
docker compose ps -a
</pre>

h3. Step 2: Re-run validation sequence

# 1. Check app config
# 2. Create database
# 3. Create schema
# 4. Seed data
# 5. Wait for Debezium
# 6. Register connector
# 7. Check Kafka topics
# 8. Initialize ClickHouse
# 9. Start Spark job
# 10. Run insert / update test

h2. 6. Success criteria

The setup is considered successful when:

* PostgreSQL database and tables are created successfully
* Seed data is inserted successfully
* Debezium connector is registered and status is RUNNING
* Kafka CDC topics are created
* CDC events can be consumed from Kafka
* ClickHouse warehouse and tables are created
* Spark job runs without error
* New PostgreSQL inserts/updates are reflected in ClickHouse
