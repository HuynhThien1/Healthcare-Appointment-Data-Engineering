


from app.seeds.seed_table.seed_doctor import seed_doctors
from app.seeds.seed_table.seed_patient import seed_patients
from app.seeds.seed_table.seed_doctor_slot import seed_doctor_slots
from app.seeds.seed_table.seed_transaction_appointment import seed_appointment_transaction
# from app.seeds.seed_table.seed_actual_appointment import seed_appointment_actual_from_csv
from app.seeds.seed_table.seed_medical_record import seed_medical_record
def seed_all():
    seed_doctors()
    seed_patients()
    seed_doctor_slots()
    seed_appointment_transaction()
    # seed_appointment_actual_from_csv()
    seed_medical_record()

if __name__ == "__main__":
    seed_all()