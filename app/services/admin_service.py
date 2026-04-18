# app/services/admin_service.py

from app.db import fetch_one

def get_admin_by_code(admin_code: str):
    return fetch_one(
        "SELECT * FROM admin WHERE admin_code = %s",
        (admin_code,)
    )