"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { SPECIALTIES, type Specialty } from "@/app/constants/specialties";

export default function RegisterPage() {
  const [role, setRole] = useState<"doctor" | "patient">("patient");

  const [name, setName] = useState("");

  // doctor
  const [specialty, setSpecialty] = useState<Specialty>(SPECIALTIES[0]);

  // patient
  const [phone, setPhone] = useState("");
  const [address, setAddress] = useState("");
  const [email, setEmail] = useState("");
  const [insurance, setInsurance] = useState("");
  const [dob, setDob] = useState("");
  const [gender, setGender] = useState("");
  const router = useRouter();

  const handleRegister = async () => {
    let payload;

    if (role === "doctor") {
      payload = {
        doctor_name: name,
        specialty,
        start_working_date: new Date().toISOString().split("T")[0],
      };
    } else {
      payload = {
        patient_name: name,
        phone_number: phone,
        address,
        email,
        insurance_number: insurance,
        date_of_birth: dob,
        gender,
      };
    }

    try {
      const res = await fetch(
        `http://127.0.0.1:8000/${role === "doctor" ? "doctors" : "patients"}`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(payload),
        },
      );

      const data = await res.json();

      if (!res.ok) {
        alert(data.message || "Register failed");
        return;
      }

      // ✅ LƯU LOGIN INFO
      // ⚠️ giả sử backend trả id như:
      // doctor_id hoặc patient_id
      const userId =
        role === "doctor"
          ? data.doctor_id || data.id
          : data.patient_id || data.id;

      localStorage.setItem("user_id", userId);
      localStorage.setItem("role", role);

      // 🔥 REDIRECT
      if (role === "doctor") {
        router.push("/dashboard/doctor/slots");
      } else {
        router.push("/dashboard/patient");
      }
    } catch (err) {
      console.error(err);
      alert("Server error");
    }
  };

  return (
    <main className="min-h-screen flex flex-col items-center justify-center bg-white">
      <div className="w-[350px] space-y-6">
        {/* Toggle */}
        <div className="flex border rounded-lg overflow-hidden">
          <button
            onClick={() => setRole("patient")}
            className={`w-1/2 py-2 ${role === "patient" ? "bg-black text-white" : ""}`}
          >
            Patient
          </button>
          <button
            onClick={() => setRole("doctor")}
            className={`w-1/2 py-2 ${role === "doctor" ? "bg-black text-white" : ""}`}
          >
            Doctor
          </button>
        </div>

        <h1 className="text-xl font-semibold text-center">
          Register as {role}
        </h1>

        <div className="space-y-4">
          {/* COMMON */}
          <input
            type="text"
            placeholder="Name"
            className="w-full border p-2 rounded"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />

          {/* DOCTOR */}
          {role === "doctor" && (
            <select
              className="w-full border p-2 rounded"
              value={specialty}
              onChange={(e) => setSpecialty(e.target.value as Specialty)}
            >
              {SPECIALTIES.map((s) => (
                <option key={s}>{s}</option>
              ))}
            </select>
          )}

          {/* PATIENT */}
          {role === "patient" && (
            <>
              <input
                type="text"
                placeholder="Phone number"
                className="w-full border p-2 rounded"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
              />

              <input
                type="text"
                placeholder="Address"
                className="w-full border p-2 rounded"
                value={address}
                onChange={(e) => setAddress(e.target.value)}
              />

              <input
                type="email"
                placeholder="Email"
                className="w-full border p-2 rounded"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />

              <input
                type="text"
                placeholder="Insurance number"
                className="w-full border p-2 rounded"
                value={insurance}
                onChange={(e) => setInsurance(e.target.value)}
              />

              <input
                type="date"
                className="w-full border p-2 rounded"
                value={dob}
                onChange={(e) => setDob(e.target.value)}
              />

              <input
                type="text"
                placeholder="Gender"
                className="w-full border p-2 rounded"
                value={gender}
                onChange={(e) => setGender(e.target.value)}
              />
            </>
          )}
        </div>

        <button
          onClick={handleRegister}
          className="w-full bg-black text-white py-2 rounded"
        >
          Register
        </button>
      </div>
    </main>
  );
}
