import os
from dotenv import load_dotenv

load_dotenv()

PG_HOST = os.getenv("PG_HOST", "localhost")
PG_PORT = int(os.getenv("PG_PORT", 5432))
PG_ADMIN_DB = os.getenv("PG_ADMIN_DB", "postgres")
PG_APP_DB = os.getenv("PG_APP_DB", "healthcare_booking_realtime")
PG_USER = os.getenv("PG_USER", "postgres")
PG_PASSWORD = os.getenv("PG_PASSWORD", "")

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