import time
import random
from app.db import get_app_connection


def main():
    while True:
        conn = get_app_connection()
        cur = conn.cursor()

        try:
            action = random.choice(["insert", "update"])
            print(f"Running action: {action}")

            # chỗ này sau đó viết logic insert/update appointment
            conn.commit()

        except Exception as e:
            conn.rollback()
            print("Error:", e)

        finally:
            cur.close()
            conn.close()

        time.sleep(3)


if __name__ == "__main__":
    main()