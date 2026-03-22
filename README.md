h1. Healthcare Appointment Data Engineering

Below are the step-by-step instructions to run this repository.

h2. Run the project

h3. Step 1: Install dependencies

<pre>
pip install -r requirements.txt
</pre>

h3. Step 2: Start Docker containers

<pre>
docker compose up -d
</pre>

h3. Step 3: Initialize database, create schema, seed data, and register connector

<pre>
python main.py
</pre>

h3. Step 4: Generate CDC events

<pre>
python -m app.stream_generator
</pre>

h3. Step 5: Open another terminal and run the consumer

<pre>
python healthcare_streaming_consumer.py
</pre>

h2. Debug steps

h3. 1. Restart Docker containers

<pre>
docker compose down -v
docker compose up -d --build
docker compose ps -a
</pre>

h3. 2. Test config inside the app container

<pre>
docker compose exec app python -c "from app.config import *; print(PG_HOST, PG_PORT, PG_ADMIN_DB, PG_APP_DB, KAFKA_BOOTSTRAP_SERVERS, DEBEZIUM_CONNECT_URL)"
</pre>

*Expected output:*

<pre>
postgres 5432 postgres healthcare_booking_realtime broker:29092 http://debezium:8083
</pre>

h3. 3. Create database

<pre>
docker compose exec app python -c "from app.create_schema import create_database; create_database()"
</pre>

h3. 4. Check created databases in PostgreSQL

<pre>
docker compose exec postgres psql -U postgres -d postgres -c "\l"
</pre>

h3. 5. Test connection between app and PostgreSQL

<pre>
docker compose exec app python -c "from app.db import get_app_connection; conn=get_app_connection(); print('app db ok'); conn.close()"
</pre>

h3. 6. Create schema

<pre>
docker compose exec app python -c "from app.create_schema import create_schema; create_schema()"
</pre>

h3. 7. Check created tables

<pre>
docker compose exec postgres psql -U postgres -d healthcare_booking_realtime -c "\dt"
</pre>

h3. 8. Seed data

<pre>
docker compose exec app python -c "from app.seed_master_data import seed_all; seed_all()"
</pre>

h3. 9. Check seeded data

<pre>
docker compose exec app python -c "from app.db import fetch_all; print(fetch_all('SELECT * FROM doctor LIMIT 5;'))"
</pre>

h3. 10. Wait for Debezium to start

<pre>
docker compose exec app python -c "from app.register_connector import wait_for_debezium; wait_for_debezium()"
</pre>

h3. 11. Register Debezium connector

<pre>
docker compose exec app python -c "from app.register_connector import register_connector; register_connector()"
</pre>

h3. 12. Check connector list from host machine

<pre>
curl http://localhost:8093/connectors
</pre>

*Expected output:*

<pre>
["healthcare-postgres-connector"]
</pre>

h3. 13. Check connector status

<pre>
curl http://localhost:8093/connectors/healthcare-postgres-connector/status
</pre>

h3. 14. Check whether Kafka topics were created

<pre>
docker compose exec broker bash
kafka-topics --bootstrap-server broker:29092 --list
</pre>

h3. 15. Check connector status and config

<pre>
curl http://localhost:8093/connectors/healthcare-postgres-connector/status
curl http://localhost:8093/connectors/healthcare-postgres-connector/config
</pre>

h3. 16. Consume CDC events from Kafka

Run this command first:

<pre>
kafka-console-consumer --bootstrap-server broker:29092 --topic healthcare.public.doctor --from-beginning
</pre>

Then open a new terminal and update data in PostgreSQL:

<pre>
docker compose exec app python -c "from app.db import execute_query; execute_query(\"UPDATE doctor SET doctor_name='Nguyen Van B', updated_at=NOW() WHERE doctor_id=1001;\"); print('updated doctor')"
</pre>

Check the broker terminal to see the new CDC event.