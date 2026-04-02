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

def load_connector_payload():
    # explanation:
    # Debezium create connector API thường nhận payload dạng:
    # {
    #   "name": "...",
    #   "config": {...}
    # }
    payload = json.loads(CONNECTOR_CONFIG_PATH.read_text(encoding="utf-8"))
    return payload


def connector_exists() -> bool:
    try:
        resp = requests.get(
            f"{DEBEZIUM_CONNECT_URL}/connectors/{CONNECTOR_NAME}",
            timeout=10,
        )
        return resp.status_code == 200
    except requests.RequestException as e:
        raise RuntimeError(f"Failed to check connector existence: {e}") from e


def create_connector(payload: dict):
    try:
        resp = requests.post(
            f"{DEBEZIUM_CONNECT_URL}/connectors",
            json=payload,
            timeout=20,
        )
    except requests.RequestException as e:
        raise RuntimeError(f"Failed to create connector: {e}") from e

    if resp.status_code in (200, 201):
        print(f"Connector created successfully: {CONNECTOR_NAME}")
    else:
        raise RuntimeError(
            f"Create connector failed: {resp.status_code} - {resp.text}"
        )


def update_connector(payload: dict):
    # explanation:
    # Update connector dùng endpoint:
    # PUT /connectors/{name}/config
    # và chỉ truyền phần config, không truyền cả object name+config.
    config = payload["config"]

    try:
        resp = requests.put(
            f"{DEBEZIUM_CONNECT_URL}/connectors/{CONNECTOR_NAME}/config",
            json=config,
            timeout=20,
        )
    except requests.RequestException as e:
        raise RuntimeError(f"Failed to update connector: {e}") from e

    if resp.status_code in (200, 201):
        print(f"Connector updated successfully: {CONNECTOR_NAME}")
    else:
        raise RuntimeError(
            f"Update connector failed: {resp.status_code} - {resp.text}"
        )


def register_connector(update_if_exists: bool = False):
    # explanation:
    # - Nếu connector chưa có -> create
    # - Nếu đã có:
    #     + update_if_exists=False -> bỏ qua
    #     + update_if_exists=True  -> update config
    wait_for_debezium()

    payload = load_connector_payload()

    if connector_exists():
        if update_if_exists:
            print(f"Connector already exists. Updating: {CONNECTOR_NAME}")
            update_connector(payload)
        else:
            print(f"Connector already exists: {CONNECTOR_NAME}")
        return

    create_connector(payload)


if __name__ == "__main__":
    register_connector(update_if_exists=False)