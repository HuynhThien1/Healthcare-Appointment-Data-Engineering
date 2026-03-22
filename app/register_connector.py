import json
import time
from pathlib import Path

import requests

from app.config import DEBEZIUM_CONNECT_URL

# explanation: Tên connector sẽ hiển thị trong Debezium UI / Kafka Connect.
CONNECTOR_NAME = "healthcare-postgres-connector"

# explanation: File JSON chứa config connector.
CONNECTOR_CONFIG_PATH = Path("debezium/healthcare-postgres-connector.json")


def wait_for_debezium(timeout_seconds: int = 120):
    # explanation: Chờ Debezium Connect REST API sẵn sàng trước khi tạo connector.
    start = time.time()

    while time.time() - start < timeout_seconds:
        try:
            resp = requests.get(f"{DEBEZIUM_CONNECT_URL}/connectors", timeout=5)
            if resp.status_code == 200:
                print("Debezium is ready.")
                return
        except requests.RequestException:
            pass

        print("Waiting for Debezium...")
        time.sleep(5)

    raise TimeoutError("Debezium did not become ready in time.")


def register_connector():
    # explanation: Tạo connector nếu nó chưa tồn tại.
    payload = json.loads(CONNECTOR_CONFIG_PATH.read_text(encoding="utf-8"))

    existing = requests.get(
        f"{DEBEZIUM_CONNECT_URL}/connectors/{CONNECTOR_NAME}",
        timeout=10,
    )

    if existing.status_code == 200:
        print(f"Connector already exists: {CONNECTOR_NAME}")
        return

    resp = requests.post(
        f"{DEBEZIUM_CONNECT_URL}/connectors",
        json=payload,
        timeout=20,
    )

    if resp.status_code in (200, 201):
        print(f"Connector created: {CONNECTOR_NAME}")
    else:
        print(f"Create connector failed: {resp.status_code} - {resp.text}")


if __name__ == "__main__":
    wait_for_debezium()
    register_connector()