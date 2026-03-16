import psycopg2
from config import ADMIN_DB_CONFIG, APP_DB_CONFIG


def get_admin_connection():
    return psycopg2.connect(**ADMIN_DB_CONFIG)


def get_app_connection():
    return psycopg2.connect(**APP_DB_CONFIG)