from apscheduler.schedulers.background import BackgroundScheduler
from app.services.schedule_service import confirm_generate, generate_preview
from app.db import fetch_all, fetch_one
from datetime import datetime

scheduler = BackgroundScheduler()


# ==============================
# AUTO GENERATE
# ==============================
def auto_generate():
    today = datetime.today()

    # ==============================
    # FIX MONTH ROLLOVER
    # ==============================
    if today.month == 12:
        target_month = 1
        target_year = today.year + 1
    else:
        target_month = today.month + 1
        target_year = today.year

    print(f"[CRON] Running auto generate for {target_month}/{target_year}")

    doctors = fetch_all("SELECT doctor_id FROM doctor")

    for d in doctors:
        doctor_id = d["doctor_id"]

        # ==============================
        # CHECK LOCK
        # ==============================
        check = fetch_one("""
            SELECT is_inserted
            FROM doctor_insert_month
            WHERE doctor_id = %s
            AND year = %s
            AND month = %s
        """, (doctor_id, target_year, target_month))

        if check and check["is_inserted"]:
            print(f"[SKIP] {doctor_id} already generated")
            continue

        # ==============================
        # GENERATE PREVIEW
        # ==============================
        preview = generate_preview(doctor_id, target_year, target_month)

        if not preview:
            print(f"[WARN] No preview for {doctor_id}")
            continue

        slots = []

        for key, value in preview.items():
            if value == "GREEN":
                dow, slot_code = key.split("_")
                slots.append({
                    "dow": int(dow),
                    "slot_code": slot_code
                })

        # ==============================
        # NO SLOT → SKIP
        # ==============================
        if not slots:
            print(f"[SKIP] No valid slots for {doctor_id}")
            continue

        try:
            confirm_generate(doctor_id, target_year, target_month, slots)
            print(f"[SUCCESS] Generated for {doctor_id}")
        except Exception as e:
            print(f"[ERROR] {doctor_id}: {str(e)}")

# ==============================
# START SCHEDULER
# ==============================
def start_scheduler():
    scheduler.add_job(
        auto_generate,
        trigger='cron',
        day='last',
        hour=23,
        minute=0
    )
    scheduler.start()

    print("[CRON] Scheduler started")