-- =========================================
-- 1) CREATE DATABASE
-- =========================================
-- CREATE DATABASE healthcare_booking_realtime;

-- Nếu dùng psql thì connect vào DB:
-- \c healthcare_booking_realtime;


-- =========================================
-- 2) ENUM TYPES
-- =========================================
CREATE TYPE employment_status_enum AS ENUM ('ACTIVE', 'INACTIVE', 'ON_LEAVE');
CREATE TYPE patient_status_enum AS ENUM ('ACTIVE', 'INACTIVE');
CREATE TYPE slot_status_enum AS ENUM ('AVAILABLE', 'BOOKED', 'BLOCKED', 'CANCELLED');
CREATE TYPE slot_type_enum AS ENUM ('CONSULTATION', 'FOLLOW_UP', 'TEST', 'EMERGENCY');
CREATE TYPE appointment_status_enum AS ENUM ('BOOKED', 'CONFIRMED', 'CANCELLED', 'COMPLETED', 'NO_SHOW');
CREATE TYPE booking_channel_enum AS ENUM ('WEB', 'MOBILE', 'PHONE', 'WALK_IN');
CREATE TYPE appointment_type_enum AS ENUM ('NEW', 'FOLLOW_UP', 'CHECKUP');
CREATE TYPE payment_status_enum AS ENUM ('PENDING', 'PAID', 'FAILED', 'REFUNDED', 'PARTIALLY_PAID');
CREATE TYPE record_status_enum AS ENUM ('DRAFT', 'FINAL', 'AMENDED');


-- =========================================
-- 3) TABLE: doctor
-- =========================================
CREATE TABLE doctor (
    doctor_id INT PRIMARY KEY,
    doctor_code VARCHAR(50),
    doctor_name VARCHAR(255) NOT NULL,
    specialty VARCHAR(255) NOT NULL,
    phone_number VARCHAR(20),
    email VARCHAR(255),
    employment_status employment_status_enum,
    clinic_id INT,
    start_working_date DATE,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);


-- =========================================
-- 4) TABLE: patient
-- =========================================
CREATE TABLE patient (
    patient_id INT PRIMARY KEY,
    patient_name VARCHAR(255) NOT NULL,
    address VARCHAR(500),
    phone_number VARCHAR(20) NOT NULL,
    email VARCHAR(255),
    insurance_number VARCHAR(100),
    insurance_provider VARCHAR(255),
    date_of_birth DATE,
    gender VARCHAR(20),
    patient_status patient_status_enum,
    emergency_contact_name VARCHAR(255),
    emergency_contact_phone VARCHAR(20),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);


-- =========================================
-- 5) TABLE: doctor_slot
-- =========================================
CREATE TABLE doctor_slot (
    slot_id INT PRIMARY KEY,
    doctor_id INT NOT NULL,
    clinic_id INT,
    slot_date DATE NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    slot_status slot_status_enum NOT NULL,
    slot_type slot_type_enum,
    max_capacity INT DEFAULT 1 CHECK (max_capacity > 0),
    created_at TIMESTAMP,
    updated_at TIMESTAMP,

    CONSTRAINT fk_doctor_slot_doctor
        FOREIGN KEY (doctor_id) REFERENCES doctor(doctor_id),

    CONSTRAINT chk_doctor_slot_time
        CHECK (end_time > start_time)
);


-- =========================================
-- 6) TABLE: appointment
-- =========================================
CREATE TABLE appointment (
    appointment_id INT PRIMARY KEY,
    confirmation_number VARCHAR(100) UNIQUE,
    slot_id INT NOT NULL,
    doctor_id INT NOT NULL,
    patient_id INT NOT NULL,

    status appointment_status_enum NOT NULL,
    booking_channel booking_channel_enum,
    appointment_type appointment_type_enum,
    reason_for_visit TEXT,
    booked_at TIMESTAMP,
    cancelled_at TIMESTAMP,
    completed_at TIMESTAMP,
    cancel_reason TEXT,
    created_by VARCHAR(100),
    updated_by VARCHAR(100),
    created_at TIMESTAMP,
    updated_at TIMESTAMP,

    CONSTRAINT fk_appointment_slot
        FOREIGN KEY (slot_id) REFERENCES doctor_slot(slot_id),

    CONSTRAINT fk_appointment_doctor
        FOREIGN KEY (doctor_id) REFERENCES doctor(doctor_id),

    CONSTRAINT fk_appointment_patient
        FOREIGN KEY (patient_id) REFERENCES patient(patient_id)
);


-- =========================================
-- 7) TABLE: appointment_status_history
-- =========================================
CREATE TABLE appointment_status_history (
    history_id INT PRIMARY KEY,
    appointment_id INT NOT NULL,
    old_status appointment_status_enum,
    new_status appointment_status_enum NOT NULL,
    changed_at TIMESTAMP NOT NULL,
    changed_by VARCHAR(100),
    reason TEXT,

    CONSTRAINT fk_appointment_status_history_appointment
        FOREIGN KEY (appointment_id) REFERENCES appointment(appointment_id)
);


-- =========================================
-- 8) TABLE: payment
-- =========================================
CREATE TABLE payment (
    payment_id INT PRIMARY KEY,
    appointment_id INT NOT NULL,
    amount_total DECIMAL(12,2) NOT NULL CHECK (amount_total >= 0),
    amount_covered DECIMAL(12,2) DEFAULT 0 CHECK (amount_covered >= 0),
    amount_patient_responsibility DECIMAL(12,2) DEFAULT 0 CHECK (amount_patient_responsibility >= 0),
    paid_datetime TIMESTAMP,
    payment_status payment_status_enum,
    payment_method VARCHAR(100),
    transaction_reference VARCHAR(255),
    currency VARCHAR(10) DEFAULT 'USD',
    created_at TIMESTAMP,
    updated_at TIMESTAMP,

    CONSTRAINT fk_payment_appointment
        FOREIGN KEY (appointment_id) REFERENCES appointment(appointment_id)
);


-- =========================================
-- 9) TABLE: medical_record
-- =========================================
CREATE TABLE medical_record (
    record_id INT PRIMARY KEY,
    appointment_id INT NOT NULL,
    patient_id INT NOT NULL,
    doctor_id INT NOT NULL,
    version_number INT NOT NULL DEFAULT 1 CHECK (version_number > 0),
    diagnosis_note TEXT,
    prescription_note TEXT,
    lab_summary TEXT,
    follow_up_instruction TEXT,
    record_status record_status_enum,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,

    CONSTRAINT fk_medical_record_appointment
        FOREIGN KEY (appointment_id) REFERENCES appointment(appointment_id),

    CONSTRAINT fk_medical_record_patient
        FOREIGN KEY (patient_id) REFERENCES patient(patient_id),

    CONSTRAINT fk_medical_record_doctor
        FOREIGN KEY (doctor_id) REFERENCES doctor(doctor_id)
);


-- =========================================
-- 10) INDEXES (recommended)
-- =========================================
CREATE INDEX idx_doctor_slot_doctor_id ON doctor_slot(doctor_id);
CREATE INDEX idx_appointment_slot_id ON appointment(slot_id);
CREATE INDEX idx_appointment_doctor_id ON appointment(doctor_id);
CREATE INDEX idx_appointment_patient_id ON appointment(patient_id);
CREATE INDEX idx_appointment_status ON appointment(status);
CREATE INDEX idx_appointment_booked_at ON appointment(booked_at);
CREATE INDEX idx_appointment_status_history_appointment_id ON appointment_status_history(appointment_id);
CREATE INDEX idx_payment_appointment_id ON payment(appointment_id);
CREATE INDEX idx_medical_record_appointment_id ON medical_record(appointment_id);
CREATE INDEX idx_medical_record_patient_id ON medical_record(patient_id);
CREATE INDEX idx_medical_record_doctor_id ON medical_record(doctor_id);