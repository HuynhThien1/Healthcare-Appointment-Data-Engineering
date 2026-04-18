-- =========================================
-- 1) CREATE DATABASE
-- =========================================
-- CREATE DATABASE healthcare_booking_realtime;
-- Nếu dùng psql thì connect vào DB:
-- \c healthcare_booking_realtime;

-- CREATE EXTENSION IF NOT EXISTS "pg_cron";
DO $$ BEGIN IF NOT EXISTS (
    SELECT 1
    FROM pg_type
    WHERE typname = 'user_role_enum'
) THEN CREATE TYPE user_role_enum AS ENUM ('ADMIN', 'DOCTOR', 'PATIENT');
END IF;
IF NOT EXISTS (
    SELECT 1
    FROM pg_type
    WHERE typname = 'employment_status_enum'
) THEN CREATE TYPE employment_status_enum AS ENUM ('ACTIVE', 'INACTIVE', 'ON_LEAVE');
END IF;
IF NOT EXISTS (
    SELECT 1
    FROM pg_type
    WHERE typname = 'admin_status_enum'
    ) THEN CREATE TYPE admin_status_enum AS ENUM ('AVAILABLE', 'BLOCKED');
    END IF;
    IF NOT EXISTS (
        SELECT 1
        FROM pg_type
    WHERE typname = 'patient_status_enum'
) THEN CREATE TYPE patient_status_enum AS ENUM ('ACTIVE', 'INACTIVE');
END IF;
IF NOT EXISTS (
    SELECT 1
    FROM pg_type
    WHERE typname = 'slot_status_enum'
) THEN CREATE TYPE slot_status_enum AS ENUM ('AVAILABLE', 'BOOKED', 'BLOCKED', 'CANCELLED');
END IF;
IF NOT EXISTS (
    SELECT 1
    FROM pg_type
    WHERE typname = 'slot_type_enum'
) THEN CREATE TYPE slot_type_enum AS ENUM ('CONSULTATION', 'FOLLOW_UP', 'TEST', 'EMERGENCY');
END IF;
IF NOT EXISTS (
    SELECT 1
    FROM pg_type
    WHERE typname = 'appointment_status_enum'
) THEN CREATE TYPE appointment_status_enum AS ENUM (
    'BOOKED',
    'CONFIRMED',
    'CANCELLED',
    'COMPLETED',
    'NO_SHOW'
);
END IF;
IF NOT EXISTS (
    SELECT 1
    FROM pg_type
    WHERE typname = 'booking_channel_enum'
) THEN CREATE TYPE booking_channel_enum AS ENUM ('WEB', 'MOBILE', 'PHONE', 'WALK_IN');
END IF;
IF NOT EXISTS (
    SELECT 1
    FROM pg_type
    WHERE typname = 'appointment_type_enum'
) THEN CREATE TYPE appointment_type_enum AS ENUM ('NEW', 'FOLLOW_UP', 'CHECKUP');
END IF;
IF NOT EXISTS (
    SELECT 1
    FROM pg_type
    WHERE typname = 'payment_status_enum'
) THEN CREATE TYPE payment_status_enum AS ENUM (
    'PENDING',
    'PAID',
    'FAILED',
    'REFUNDED',
    'PARTIALLY_PAID'
);
END IF;
IF NOT EXISTS (
    SELECT 1
    FROM pg_type
    WHERE typname = 'record_status_enum'
) THEN CREATE TYPE record_status_enum AS ENUM ('DRAFT', 'FINAL', 'AMENDED');
END IF;
END $$;

CREATE TABLE IF NOT EXISTS admin (
    admin_code TEXT PRIMARY KEY
);

-- Insert đúng 1 admin
INSERT INTO admin (admin_code)
VALUES ('ADMINHEALTHCARE')
ON CONFLICT (admin_code) DO NOTHING;

CREATE TABLE IF NOT EXISTS calendar_day (
    date DATE PRIMARY KEY,
    status VARCHAR(10) NOT NULL CHECK (status IN ('NORMAL_DAY', 'HOLIDAY', 'WEEKEND')),
    weekday_name VARCHAR(20) NOT NULL
);

INSERT INTO calendar_day (date, status, weekday_name)
SELECT
    d::date,

    CASE 
        WHEN (EXTRACT(MONTH FROM d) = 1 AND EXTRACT(DAY FROM d) = 1)
          OR (EXTRACT(MONTH FROM d) = 4 AND EXTRACT(DAY FROM d) = 30)
          OR (EXTRACT(MONTH FROM d) = 5 AND EXTRACT(DAY FROM d) = 1)
        THEN 'HOLIDAY'

        WHEN EXTRACT(ISODOW FROM d) = 7
        THEN 'WEEKEND'

        ELSE 'NORMAL_DAY'
    END,

    CASE EXTRACT(ISODOW FROM d)
        WHEN 1 THEN 'MON'
        WHEN 2 THEN 'TUE'
        WHEN 3 THEN 'WED'
        WHEN 4 THEN 'THU'
        WHEN 5 THEN 'FRI'
        WHEN 6 THEN 'SAT'
        WHEN 7 THEN 'SUN'
    END

FROM generate_series(
    DATE '2026-01-01',
    DATE '2050-12-31',
    INTERVAL '1 day'
) d

ON CONFLICT (date) 
DO UPDATE SET 
    status = EXCLUDED.status,
    weekday_name = EXCLUDED.weekday_name;

-- =========================================
-- 3) TABLE: slot_code_template
-- =========================================
CREATE TABLE IF NOT EXISTS slot_code_template (
    slot_code VARCHAR(10) PRIMARY KEY,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    display_order INT
);
-- =========================================
-- Hard insert slot code templates (can be modified later if needed)
-- =========================================
INSERT INTO slot_code_template (slot_code, start_time, end_time, display_order)
VALUES ('8A', '08:00', '08:30', 1),
    ('8B', '08:30', '09:00', 2),
    ('9A', '09:00', '09:30', 3),
    ('9B', '09:30', '10:00', 4),
    ('10A', '10:00', '10:30', 5),
    ('10B', '10:30', '11:00', 6),
    ('11A', '11:00', '11:30', 7),
    ('11B', '11:30', '12:00', 8),
    ('13A', '13:00', '13:30', 9),
    ('13B', '13:30', '14:00', 10),
    ('14A', '14:00', '14:30', 11),
    ('14B', '14:30', '15:00', 12),
    ('15A', '15:00', '15:30', 13),
    ('15B', '15:30', '16:00', 14),
    ('16A', '16:00', '16:30', 15),
    ('16B', '16:30', '17:00', 16) ON CONFLICT (slot_code) DO NOTHING;


CREATE SEQUENCE doctor_seq START 1 INCREMENT 1 MINVALUE 1 MAXVALUE 900;
CREATE SEQUENCE patient_seq START 1 INCREMENT 1;
CREATE SEQUENCE appointment_seq START 1 INCREMENT 1;
CREATE SEQUENCE medical_record_seq START 1 INCREMENT 1 MINVALUE 1 MAXVALUE 99999999;
CREATE SEQUENCE transaction_seq START 1 INCREMENT 1 MINVALUE 1 MAXVALUE 99999999;

-- =========================================
-- 3) TABLE: doctor
-- =========================================

CREATE TABLE IF NOT EXISTS doctor (
    doctor_id TEXT PRIMARY KEY DEFAULT 'DR' || LPAD(nextval('doctor_seq')::text, 3, '0'),
    doctor_name TEXT NOT NULL,
    specialty TEXT NOT NULL,
    start_working_date DATE
);
-- =========================================
-- 4) TABLE: patient
-- =========================================
CREATE TABLE IF NOT EXISTS patient (
    patient_id INT PRIMARY KEY DEFAULT nextval('patient_seq'),

    patient_name VARCHAR(255) NOT NULL,
    address VARCHAR(500),
    phone_number VARCHAR(20) NOT NULL,
    insurance_number VARCHAR(100) UNIQUE,
    date_of_birth DATE,
    gender VARCHAR(20),
    email VARCHAR(255),

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
-- =========================================
-- 5) TABLE: doctor_slot
-- =========================================
CREATE TABLE IF NOT EXISTS doctor_slot (
    slot_id TEXT PRIMARY KEY,

    doctor_id TEXT NOT NULL,
    slot_date DATE NOT NULL,
    slot_code VARCHAR(10) NOT NULL,
    slot_status slot_status_enum DEFAULT 'AVAILABLE',

    FOREIGN KEY (doctor_id) REFERENCES doctor(doctor_id),
    FOREIGN KEY (slot_code) REFERENCES slot_code_template(slot_code),
    admin_status admin_status_enum DEFAULT 'AVAILABLE',
    CONSTRAINT unique_slot UNIQUE (doctor_id, slot_date, slot_code)
);
-- =========================================
-- 6) TABLE: appointment
-- =========================================
CREATE TABLE IF NOT EXISTS appointment (
    appointment_id INT PRIMARY KEY DEFAULT nextval('appointment_seq'),

    booking_ref TEXT UNIQUE,

    slot_id TEXT NOT NULL,
    patient_id INT NOT NULL,


    booked_at TIMESTAMP,

    FOREIGN KEY (slot_id) REFERENCES doctor_slot(slot_id),
    FOREIGN KEY (patient_id) REFERENCES patient(patient_id),
    CONSTRAINT unique_slot_booking UNIQUE (slot_id)
);
-- =========================================
-- 7) TABLE: appointment_transaction
-- =========================================

CREATE TABLE IF NOT EXISTS appointment_transaction (
    transaction_id TEXT PRIMARY KEY DEFAULT 'TXN26' || LPAD(nextval('transaction_seq')::text, 8, '0'),

    slot_id TEXT NOT NULL,
    patient_id INT NOT NULL,

    action appointment_status_enum NOT NULL,

    created_at TIMESTAMP NOT NULL,

    FOREIGN KEY (slot_id) REFERENCES doctor_slot(slot_id),
    FOREIGN KEY (patient_id) REFERENCES patient(patient_id)
);

-- =========================================
-- 9) TABLE: medical_record
-- =========================================

CREATE TABLE IF NOT EXISTS medical_record (
    record_id TEXT PRIMARY KEY DEFAULT 'REC26' || LPAD(nextval('medical_record_seq')::text, 8, '0'),

    slot_id TEXT NOT NULL,
    patient_id INT NOT NULL,

    version_number INT NOT NULL CHECK (version_number > 0),

    diagnosis_note TEXT,
    prescription_note TEXT,

    created_at TIMESTAMP,
    updated_at TIMESTAMP,

    CONSTRAINT fk_medical_record_slot FOREIGN KEY (slot_id) REFERENCES doctor_slot(slot_id),
    CONSTRAINT fk_medical_record_patient FOREIGN KEY (patient_id) REFERENCES patient(patient_id),
    CONSTRAINT unique_record_version UNIQUE (slot_id, patient_id, version_number)
);
-- =========================================
-- 10) INDEXES (recommended)
-- =========================================
CREATE INDEX IF NOT EXISTS idx_doctor_slot_doctor_id ON doctor_slot(doctor_id);
CREATE INDEX IF NOT EXISTS idx_appointment_slot_id ON appointment(slot_id);
CREATE INDEX IF NOT EXISTS idx_appointment_patient_id ON appointment(patient_id);
CREATE INDEX IF NOT EXISTS idx_appointment_booked_at ON appointment(booked_at);
CREATE INDEX IF NOT EXISTS idx_medical_record_patient_id ON medical_record(patient_id);

-- =========================================
-- 11) TABLE: doctor_insert_month
-- =========================================
CREATE TABLE IF NOT EXISTS doctor_insert_month (
    doctor_id TEXT NOT NULL,
    year INT NOT NULL,
    month INT NOT NULL,
    is_inserted BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (doctor_id, year, month),
    FOREIGN KEY (doctor_id) REFERENCES doctor(doctor_id),
    CONSTRAINT unique_doctor_month UNIQUE (doctor_id, year, month)
);
INSERT INTO doctor_insert_month (doctor_id, year, month)
SELECT d.doctor_id,
    EXTRACT(
        YEAR
        FROM dt
    )::int,
    EXTRACT(
        MONTH
        FROM dt
    )::int
FROM doctor d
    CROSS JOIN generate_series(
        DATE '2026-05-01',
        DATE '2050-12-01',
        INTERVAL '1 month'
    ) dt ON CONFLICT (doctor_id, year, month) DO NOTHING;
