import json
from kafka import KafkaConsumer

from app.config import KAFKA_BOOTSTRAP_SERVERS, KAFKA_TOPICS


def build_consumer():
    # explanation: Tạo Kafka consumer để đọc CDC events từ 7 topic.
    return KafkaConsumer(
        *KAFKA_TOPICS,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        group_id="healthcare-demo-consumer-group",
        value_deserializer=lambda x: json.loads(x.decode("utf-8")),
        key_deserializer=lambda x: x.decode("utf-8") if x else None,
    )


def main():
    # explanation: In message ra terminal để bạn nhìn thấy Debezium CDC events.
    consumer = build_consumer()
    print("Kafka consumer is listening...")

    for message in consumer:
        print("=" * 80)
        print(f"Topic     : {message.topic}")
        print(f"Partition : {message.partition}")
        print(f"Offset    : {message.offset}")
        print(f"Key       : {message.key}")
        print("Value     :")
        print(json.dumps(message.value, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()