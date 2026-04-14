"use client";

import { useState } from "react";
import { SPECIALTIES } from "@/app/constants/specialties";
import { useRouter } from "next/navigation";

export default function PatientPage() {
  type Doctor = {
    doctor_id: number;
    doctor_name: string;
    specialty: string;
  };

  const [selectedSpecialty, setSelectedSpecialty] = useState("");
  const [doctors, setDoctors] = useState<Doctor[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const router = useRouter();

  const handleConfirm = async () => {
    if (!selectedSpecialty) {
      alert("Please select a specialty");
      return;
    }

    try {
      setLoading(true);
      setError("");

      const res = await fetch(
        `http://127.0.0.1:8000/doctors/specialty/${encodeURIComponent(selectedSpecialty)}`
      );

      const data: Doctor[] = await res.json();

      if (!res.ok) {
        setError("Failed to fetch doctors");
        return;
      }

      setDoctors(data);
    } catch (err) {
      console.error(err);
      setError("Server error");
    } finally {
      setLoading(false);
    }
  };

  const handleBook = (doctorId: number) => {
    localStorage.setItem("selected_doctor_id", String(doctorId));
    router.push("/dashboard/patient/book");
  };

  return (
    <div className="p-6">
      <h1 className="text-xl font-semibold mb-4">
        Select your symptom / specialty
      </h1>

      <select
        className="border p-2 rounded mr-3"
        value={selectedSpecialty}
        onChange={(e) => setSelectedSpecialty(e.target.value)}
      >
        <option value="">-- Choose --</option>
        {SPECIALTIES.map((spec) => (
          <option key={spec} value={spec}>
            {spec}
          </option>
        ))}
      </select>

      <button
        onClick={handleConfirm}
        className="bg-blue-500 text-white px-4 py-2 rounded"
      >
        Confirm
      </button>

      {loading && <p className="mt-4">Loading...</p>}
      {error && <p className="mt-4 text-red-500">{error}</p>}

      <div className="mt-6 space-y-3">
        {doctors.map((doc) => (
          <div key={doc.doctor_id} className="border p-4 rounded shadow-sm">
            <p><strong>ID:</strong> {doc.doctor_id}</p>
            <p><strong>Name:</strong> {doc.doctor_name}</p>
            <p><strong>Specialty:</strong> {doc.specialty}</p>

            <button
              onClick={() => handleBook(doc.doctor_id)}
              className="mt-2 bg-green-500 text-white px-3 py-1 rounded"
            >
              Book
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}