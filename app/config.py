import os
from dotenv import load_dotenv

load_dotenv()

PG_HOST = os.getenv("PG_HOST", "localhost")
PG_PORT = int(os.getenv("PG_PORT", 5432))
PG_ADMIN_DB = os.getenv("PG_ADMIN_DB", "postgres")
PG_APP_DB = os.getenv("PG_APP_DB", "healthcare_booking_realtime")
PG_USER = os.getenv("PG_USER", "postgres")
PG_PASSWORD = os.getenv("PG_PASSWORD", "")

# explanation: Kafka bootstrap server để consumer đọc event.
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "broker:29092")

# explanation: Debezium Connect REST API URL.
DEBEZIUM_CONNECT_URL = os.getenv("DEBEZIUM_CONNECT_URL", "http://debezium:8083")


# explanation: Topic prefix phải khớp với connector JSON.
TOPIC_PREFIX = os.getenv("TOPIC_PREFIX", "healthcare")

# explanation: Các topic CDC tương ứng với 7 bảng.
# KAFKA_TOPICS = [
#     os.getenv("TOPIC_DOCTOR", "healthcare.public.doctor"),
#     os.getenv("TOPIC_PATIENT", "healthcare.public.patient"),
#     os.getenv("TOPIC_APPOINTMENT", "healthcare.public.appointment"),
#     os.getenv("TOPIC_PAYMENT", "healthcare.public.payment"),
#     os.getenv("TOPIC_CLINIC", "healthcare.public.clinic"),
#     os.getenv("TOPIC_SLOT", "healthcare.public.slot"),
#     os.getenv("TOPIC_MEDICAL_RECORD", "healthcare.public.medical_record"),
# ]

# KAFKA_TOPIC_DOCTOR = os.getenv("KAFKA_TOPIC_DOCTOR", "healthcare.public.doctor")

# # explanation: Cấu hình ClickHouse data warehouse
# CLICKHOUSE_HOST = os.getenv("CLICKHOUSE_HOST", "clickhouse")
# CLICKHOUSE_PORT = int(os.getenv("CLICKHOUSE_PORT", 8123))
# CLICKHOUSE_DB = os.getenv("CLICKHOUSE_DB", "healthcare_dw")
# CLICKHOUSE_USER = os.getenv("CLICKHOUSE_USER", "default")
# CLICKHOUSE_PASSWORD = os.getenv("CLICKHOUSE_PASSWORD", "")

ADMIN_DB_CONFIG = {
    "host": PG_HOST,
    "port": PG_PORT,
    "dbname": PG_ADMIN_DB,
    "user": PG_USER,
    "password": PG_PASSWORD
}

APP_DB_CONFIG = {
    "host": PG_HOST,
    "port": PG_PORT,
    "dbname": PG_APP_DB,
    "user": PG_USER,
    "password": PG_PASSWORD
}