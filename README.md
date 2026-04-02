h1. Healthcare Appointment Data Engineering

This document describes how to run, validate, and debug the project step by step.

h2. 1. Run the project

h3. Step 1: Install dependencies

<pre>
pip install -r requirements.txt
</pre>

h3. Step 2: Start Docker containers

<pre>
docker compose up -d
docker compose ps -a
</pre>

h3. Step 3: Verify ClickHouse connection

<pre>
docker exec -it clickhouse clickhouse-client --query "SELECT 1"
</pre>

h3. Step 4: Initialize PostgreSQL schema, seed data, and register Debezium connector

<pre>
python main.py
</pre>

h3. Step 5: Generate CDC events

<pre>
python -m app.stream_generator
</pre>

h3. Step 6: Run CDC consumer in another terminal

<pre>
python healthcare_streaming_consumer.py
</pre>


h2. 2. Component validation

h3. 2.1 Validate app config inside container

<pre>
docker compose exec app python -c "from app.config import *; print(PG_HOST, PG_PORT, PG_ADMIN_DB, PG_APP_DB, KAFKA_BOOTSTRAP_SERVERS, DEBEZIUM_CONNECT_URL)"
</pre>

*Expected output:*

<pre>
postgres 5432 postgres healthcare_booking_realtime broker:29092 http://debezium:8083
</pre>

h3. 2.2 Validate PostgreSQL database creation

Create database:

<pre>
docker compose exec app python -c "from app.create_schema import create_database; create_database()"
</pre>

Check created databases:

<pre>
docker compose exec postgres psql -U postgres -d postgres -c "\l"
</pre>

Test app connection to PostgreSQL:

<pre>
docker compose exec app python -c "from app.db import get_app_connection; conn=get_app_connection(); print('app db ok'); conn.close()"
</pre>

h3. 2.3 Validate PostgreSQL schema and seed data

Create schema:

<pre>
docker compose exec app python -c "from app.create_schema import create_schema; create_schema()"
</pre>

Check created tables:

<pre>
docker compose exec postgres psql -U postgres -d healthcare_booking_realtime -c "\dt"
</pre>

Seed master data:

<pre>
docker compose exec app python -c "from app.seed_master_data import seed_all; seed_all()"
</pre>

Check seeded data:

<pre>
docker compose exec app python -c "from app.db import fetch_all; print(fetch_all('SELECT * FROM doctor LIMIT 5;'))"
</pre>

h3. 2.4 Validate Debezium connector

Wait for Debezium service:

<pre>
docker compose exec app python -c "from app.register_connector import wait_for_debezium; wait_for_debezium()"
</pre>

Register connector:

<pre>
docker compose exec app python -c "from app.register_connector import register_connector; register_connector()"
</pre>

Check connector list:

<pre>
curl http://localhost:8093/connectors
</pre>

*Expected output:*

<pre>
["healthcare-postgres-connector"]
</pre>

Check connector status:

<pre>
curl http://localhost:8093/connectors/healthcare-postgres-connector/status
</pre>

Check connector config:

<pre>
curl http://localhost:8093/connectors/healthcare-postgres-connector/config
</pre>

h3. 2.5 Validate Kafka topics

<pre>
docker compose exec broker bash -lc "kafka-topics --bootstrap-server broker:29092 --list"
</pre>

Expected CDC topics should appear after the connector captures table changes, for example:

<pre>
healthcare.public.doctor
</pre>

h3. 2.6 Validate ClickHouse warehouse

Initialize ClickHouse warehouse:

<pre>
docker compose exec app python -c "from app.init_clickhouse import init_clickhouse; init_clickhouse()"
</pre>

Check ClickHouse objects:

<pre>
docker compose exec clickhouse clickhouse-client --query "SHOW DATABASES"
docker compose exec clickhouse clickhouse-client --query "SHOW TABLES FROM healthcare_dw"
docker compose exec clickhouse clickhouse-client --query "DESCRIBE TABLE healthcare_dw.dim_doctor"
</pre>


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
docker compose exec app python -c "from app.db import execute_query; execute_query(\"UPDATE doctor SET doctor_name='Nguyen Van B', updated_at=NOW() WHERE doctor_id=1001;\"); print('updated doctor')"
</pre>

Expected result:
* New CDC event appears in Kafka consumer
* Debezium connector remains in RUNNING state

h3. 4.3 Insert new PostgreSQL data

In another terminal:

<pre>
docker compose exec app python -c "from app.db import execute_query; execute_query(\"INSERT INTO doctor (doctor_id, doctor_code, doctor_name, specialty, employment_status, created_at, updated_at) VALUES (2003, 'DOC2003', 'Le Van C', 'Neurology', 'ACTIVE', NOW(), NOW());\"); print('inserted doctor')"
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