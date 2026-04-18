from app.db import fetch_all, fetch_one, execute_query
from datetime import datetime

# ==============================
# CHECK MONTH STATUS
# ==============================
def get_month_status(doctor_id: str, year: int, month: int):
    return fetch_one("""
        SELECT is_inserted
        FROM doctor_insert_month
        WHERE doctor_id = %s
        AND year = %s
        AND month = %s
    """, (doctor_id, year, month))


# ==============================
# GENERATE PREVIEW
# ==============================
def generate_preview(doctor_id: str, year: int, month: int):
    prev_month = month - 1
    prev_year = year

    if prev_month == 0:
        prev_month = 12
        prev_year -= 1

    start = f"{prev_year}-{prev_month:02d}-01"
    end = f"{year}-{month:02d}-01"

    rows = fetch_all("""
        SELECT
            EXTRACT(ISODOW FROM slot_date) AS dow,
            slot_code,
            COUNT(*) AS cnt
        FROM doctor_slot
        WHERE doctor_id = %s
        AND slot_status = 'AVAILABLE'
        AND slot_date >= %s
        AND slot_date < %s
        AND EXTRACT(ISODOW FROM slot_date) BETWEEN 1 AND 6
        GROUP BY dow, slot_code
    """, (doctor_id, start, end))

    result = {}

    for r in rows:
        key = f"{int(r['dow'])}_{r['slot_code']}"
        result[key] = "GREEN" if r["cnt"] >= 2 else "RED"

    return result


# ==============================
# CONFIRM GENERATE
# ==============================

def confirm_generate(doctor_id: str, year: int, month: int, slots: list):
    from datetime import date, timedelta
    from app.db import get_app_connection
    from psycopg2.extras import execute_values

    # 1. Template tất cả các slot trong ngày
    ALL_SLOTS = ["8A","8B","9A","9B","10A","10B","11A","11B","13A","13B","14A","14B","15A","15B","16A","16B"]

    # --- BỎ STEP 2 (Kiểm tra lock) ĐỂ CHO PHÉP MODIFY ---

    # 2. Xác định khoảng ngày trong tháng
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year + 1, 1, 1)
    else:
        end_date = date(year, month + 1, 1)
    
    delta = end_date - start_date

    # 3. Lấy danh sách ngày Lễ (HOLIDAY) từ DB
    holidays = fetch_all("SELECT date FROM calendar_day WHERE date >= %s AND date < %s AND status = 'HOLIDAY'", (start_date, end_date))
    holiday_set = set(h["date"] for h in holidays)

    # 4. Map các slot bác sĩ đã chọn (AVAILABLE) từ UI
    available_set = set((s["dow"], s["slot_code"]) for s in slots)

    insert_rows = []

    for i in range(delta.days):
        current_date = start_date + timedelta(days=i)
        dow = current_date.isoweekday() 

        if dow == 7: # Bỏ qua Chủ Nhật
            continue

        for slot_code in ALL_SLOTS:
            slot_id = f"{current_date.strftime('%Y%m%d')}{doctor_id}{slot_code}"
            
            # Mặc định ban đầu là BLOCKED (NOT AVAILABLE)
            admin_status = "AVAILABLE"
            
            if current_date in holiday_set:
                admin_status = "BLOCKED"
                slot_status = "BLOCKED"
            else:
                # Nếu bác sĩ chọn trong UI thì là AVAILABLE, ngược lại là BLOCKED
                if (dow, slot_code) in available_set:
                    slot_status = "AVAILABLE"
                else:
                    slot_status = "BLOCKED"

            insert_rows.append((
                slot_id, doctor_id, current_date, slot_code, slot_status, admin_status
            ))

    # 5. Thực hiện Batch Insert với logic ON CONFLICT cải tiến
    if insert_rows:
        conn = get_app_connection()
        try:
            with conn.cursor() as cur:
                execute_values(
                    cur,
                    """
                    INSERT INTO doctor_slot (slot_id, doctor_id, slot_date, slot_code, slot_status, admin_status)
                    VALUES %s
                    ON CONFLICT (slot_id) DO UPDATE SET
                        admin_status = EXCLUDED.admin_status,
                        -- CHỈ cập nhật slot_status nếu hiện tại KHÔNG PHẢI là 'BOOKED'
                        slot_status = CASE 
                            WHEN doctor_slot.slot_status = 'BOOKED' THEN 'BOOKED'
                            ELSE EXCLUDED.slot_status 
                        END;
                    """,
                    insert_rows
                )
            conn.commit()
        finally:
            conn.close()

    # 6. Đánh dấu/Cập nhật bảng trạng thái
    execute_query("""
        INSERT INTO doctor_insert_month (doctor_id, year, month, is_inserted)
        VALUES (%s, %s, %s, TRUE)
        ON CONFLICT (doctor_id, year, month) DO UPDATE SET is_inserted = TRUE;
    """, (doctor_id, year, month))

    return {"message": "Schedule updated successfully"}
