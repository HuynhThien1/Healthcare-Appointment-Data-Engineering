from pyspark.sql.types import LongType, StringType, StructField, StructType


def debezium_envelope(after_schema: StructType) -> StructType:
    payload_schema = StructType(
        [
            StructField("before", after_schema, True),
            StructField("after", after_schema, True),
            StructField("op", StringType(), True),
            StructField("ts_ms", LongType(), True),
        ]
    )

    return StructType(
        [
            StructField("payload", payload_schema, True),
        ]
    )


slot_code_template_after_schema = StructType(
    [
        StructField("slot_code", StringType(), True),
        StructField("start_time", StringType(), True),
        StructField("end_time", StringType(), True),
        StructField("display_order", LongType(), True),
    ]
)

doctor_after_schema = StructType(
    [
        StructField("doctor_id", StringType(), True),
        StructField("doctor_name", StringType(), True),
        StructField("specialty", StringType(), True),
        StructField("start_working_date", LongType(), True),
    ]
)

patient_after_schema = StructType(
    [
        StructField("patient_id", LongType(), True),
        StructField("patient_name", StringType(), True),
        StructField("address", StringType(), True),
        StructField("phone_number", StringType(), True),
        StructField("insurance_number", StringType(), True),
        StructField("date_of_birth", LongType(), True),
        StructField("gender", StringType(), True),
        StructField("email", StringType(), True),
        StructField("created_at", LongType(), True),
        StructField("updated_at", LongType(), True),
    ]
)

doctor_slot_after_schema = StructType(
    [
        StructField("slot_id", StringType(), True),
        StructField("doctor_id", StringType(), True),
        StructField("slot_date", LongType(), True),
        StructField("slot_code", StringType(), True),
        StructField("slot_status", StringType(), True),
    ]
)

appointment_after_schema = StructType(
    [
        StructField("appointment_id", LongType(), True),
        StructField("booking_ref", StringType(), True),
        StructField("slot_id", StringType(), True),
        StructField("patient_id", LongType(), True),
        StructField("booked_at", LongType(), True),
    ]
)

appointment_transaction_after_schema = StructType(
    [
        StructField("transaction_id", StringType(), True),
        StructField("slot_id", StringType(), True),
        StructField("patient_id", LongType(), True),
        StructField("action", StringType(), True),
        StructField("created_at", LongType(), True),
    ]
)

medical_record_after_schema = StructType(
    [
        StructField("record_id", StringType(), True),
        StructField("slot_id", StringType(), True),
        StructField("patient_id", LongType(), True),
        StructField("version_number", LongType(), True),
        StructField("diagnosis_note", StringType(), True),
        StructField("prescription_note", StringType(), True),
        StructField("created_at", LongType(), True),
        StructField("updated_at", LongType(), True),
    ]
)

debezium_slot_code_template_schema = debezium_envelope(slot_code_template_after_schema)
debezium_doctor_schema = debezium_envelope(doctor_after_schema)
debezium_patient_schema = debezium_envelope(patient_after_schema)
debezium_doctor_slot_schema = debezium_envelope(doctor_slot_after_schema)
debezium_appointment_schema = debezium_envelope(appointment_after_schema)
debezium_appointment_transaction_schema = debezium_envelope(appointment_transaction_after_schema)
debezium_medical_record_schema = debezium_envelope(medical_record_after_schema)