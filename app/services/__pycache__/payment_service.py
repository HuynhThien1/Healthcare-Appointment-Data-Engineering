from app.db import fetch_all, execute_query

def get_all_payments():
    return fetch_all("SELECT * FROM payment;")

def create_payment(data:dict):
    query="""
    INSERT INTO payment(
        payment_id, appointment_id,
        amount_total, amount_covered,
        amount_patient_responsibility,
        payment_status, created_at, updated_at
    )
    VALUES (%s,%s,%s,%s,%s,%s,NOW(),NOW());
    """
    execute_query(query,(
        data["payment_id"],data["appointment_id"],
        data["amount_total"],data.get("amount_covered",0),
        data.get("amount_patient_responsibility",0),
        data.get("payment_status","PENDING")
    ))