"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { INSURANCE_PREFIX } from "@/app/constants/insurances";

export default function LoginPage() {
  const [role, setRole] = useState<"doctor" | "patient" | "admin">("patient");
  // doctor
  const [doctorId, setDoctorId] = useState("");
  const [adminCode, setAdminCode] = useState("");

  // patient insurance
  const [prefix, setPrefix] = useState("GD");
  const [insuranceNumber, setInsuranceNumber] = useState("");

  const router = useRouter();

  const handleLogin = async () => {
    try {
      // ======================
      // DOCTOR LOGIN
      // ======================
      if (role === "doctor") {
        if (!doctorId) {
          alert("Please enter Doctor ID");
          return;
        }

        if (!doctorId.startsWith("DR")) {
          alert("Doctor ID must be like DR001");
          return;
        }

        const res = await fetch(`http://127.0.0.1:8000/auth/login/doctor`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ doctor_id: doctorId }),
        });

        const data = await res.json();

        if (!res.ok) {
          alert(data.message || "Login failed");
          return;
        }

        localStorage.setItem("role", "doctor");
        localStorage.setItem("user_id", doctorId);

        router.push("/dashboard/doctor/slots");
        return;
      }
      if (role === "admin") {
        if (!adminCode) {
          alert("Please enter admin code");
          return;
        }

        const res = await fetch("http://127.0.0.1:8000/auth/login/admin", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ admin_code: adminCode }),
        });

        const data = await res.json();

        if (!res.ok) {
          alert(data.detail || "Login failed");
          return;
        }

        localStorage.setItem("role", "admin");
        localStorage.setItem("user_id", adminCode);

        router.push("/dashboard/admin");
        return;
      }

      // ======================
      // PATIENT LOGIN (INSURANCE)
      // ======================

      if (!/^\d{13}$/.test(insuranceNumber)) {
        alert("Insurance number must be 13 digits");
        return;
      }

      const fullInsurance = prefix + insuranceNumber;

      // 🔥 check tồn tại bằng API
      // 🔥 LẤY patient_id TRỰC TIẾP
      const res = await fetch(
        `http://127.0.0.1:8000/patients/by-insurance/${fullInsurance}`,
      );

      const data = await res.json();

      if (!res.ok || !data?.patient_id) {
        alert("Insurance number not found");
        return;
      }

      // ✅ lưu cả 2
      localStorage.setItem("role", "patient");
      localStorage.setItem("user_insurance", fullInsurance);
      localStorage.setItem("user_id", String(data.patient_id)); // 🔥 thêm dòng này

      router.push("/dashboard/patient");
    } catch (err) {
      console.error("Login error:", err);
      alert("Server error");
    }
  };

  return (
    <main className="min-h-screen flex flex-col items-center justify-center bg-white">
      <div className="w-[350px] space-y-6">
        {/* TOGGLE */}
        <div className="flex border rounded-lg overflow-hidden">
          <button
            onClick={() => setRole("patient")}
            className={`w-1/2 py-2 ${
              role === "patient" ? "bg-black text-white" : ""
            }`}
          >
            Patient
          </button>
          <button
            onClick={() => setRole("doctor")}
            className={`w-1/2 py-2 ${
              role === "doctor" ? "bg-black text-white" : ""
            }`}
          >
            Doctor
          </button>
          <button
            onClick={() => setRole("admin")}
            className={`w-1/3 py-2 ${role === "admin" ? "bg-black text-white" : ""}`}
          >
            Admin
          </button>
        </div>

        <h1 className="text-xl font-semibold text-center">Login as {role}</h1>

        {/* ===================== */}
        {/* DOCTOR */}
        {/* ===================== */}
        {role === "doctor" && (
          <div>
            <label className="block mb-1">Doctor ID</label>
            <input
              type="text"
              placeholder="DR001"
              className="w-full border p-2 rounded"
              value={doctorId}
              onChange={(e) => setDoctorId(e.target.value)}
            />
          </div>
        )}

        {/* ===================== */}
        {/* PATIENT */}
        {/* ===================== */}
        {role === "patient" && (
          <div>
            <label className="block mb-1">Patient Insurance</label>

            <div className="flex gap-2">
              <select
                className="border p-2 rounded"
                value={prefix}
                onChange={(e) => setPrefix(e.target.value)}
              >
                {INSURANCE_PREFIX.map((p) => (
                  <option key={p}>{p}</option>
                ))}
              </select>

              <input
                type="text"
                placeholder="13 digits"
                className="flex-1 border p-2 rounded"
                value={insuranceNumber}
                onChange={(e) => setInsuranceNumber(e.target.value)}
              />
            </div>
          </div>
        )}
        {role === "admin" && (
          <div>
            <label className="block mb-1">Admin Code</label>
            <input
              type="text"
              placeholder="ADMINHEALTHCARE"
              className="w-full border p-2 rounded"
              value={adminCode}
              onChange={(e) => setAdminCode(e.target.value)}
            />
          </div>
        )}

        <button
          onClick={handleLogin}
          className="w-full bg-black text-white py-2 rounded"
        >
          Login
        </button>
      </div>
    </main>
  );
}
