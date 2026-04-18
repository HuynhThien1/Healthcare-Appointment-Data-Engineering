"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

import { INSURANCE_PREFIX } from "@/app/constants/insurances";

export default function RegisterPage() {
  const router = useRouter();

  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");
  const [address, setAddress] = useState("");
  const [email, setEmail] = useState("");

  // insurance split
  const [insurancePrefix, setInsurancePrefix] = useState("GD");
  const [insuranceNumber, setInsuranceNumber] = useState("");

  const [dob, setDob] = useState("");
  const [gender, setGender] = useState("");

  const [existingInsurance, setExistingInsurance] = useState<string[]>([]);

  // 🔥 fetch existing insurance
  useEffect(() => {
    fetch("http://127.0.0.1:8000/patients/insurance-numbers/all")
      .then((res) => res.json())
      .then((data) => {
        type InsuranceItem = {
          insurance_number: string;
        };

        let list: string[] = [];

        if (Array.isArray(data)) {
          list = data.map((i: InsuranceItem) => i.insurance_number);
        } else if (Array.isArray(data.data)) {
          list = data.data.map((i: InsuranceItem) => i.insurance_number);
        } else {
          console.error("Unexpected API format:", data);
        }

        setExistingInsurance(list);
        setExistingInsurance(list);
      })
      .catch(console.error);
  }, []);

  const validate = () => {
    // phone
    if (!/^0\d{9}$/.test(phone)) {
      alert("Phone must be 10 digits and start with 0");
      return false;
    }

    // email
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      alert("Invalid email");
      return false;
    }

    // insurance 13 digits
    if (!/^\d{13}$/.test(insuranceNumber)) {
      alert("Insurance number must be 13 digits");
      return false;
    }

    const fullInsurance = insurancePrefix + insuranceNumber;

    if (existingInsurance.includes(fullInsurance)) {
      alert("Insurance already exists");
      return false;
    }

    // gender
    if (!["male", "female"].includes(gender)) {
      alert("Gender must be male or female");
      return false;
    }

    // dob
    const year = new Date(dob).getFullYear();
    const currentYear = new Date().getFullYear();

    if (year > currentYear - 10) {
      alert(`DOB must be before ${currentYear - 10}`);
      return false;
    }

    return true;
  };

  const handleRegister = async () => {
    if (!validate()) return;

    const fullInsurance = insurancePrefix + insuranceNumber;

    const payload = {
      patient_name: name,
      phone_number: phone,
      address,
      email,
      insurance_number: fullInsurance,
      date_of_birth: dob,
      gender,
    };

    try {
      const res = await fetch("http://127.0.0.1:8000/patients", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      const data = await res.json();

      if (!res.ok) {
        alert(data.message || "Register failed");
        return;
      }
      alert(`Registered successfully with insurance ${fullInsurance}`);
      localStorage.setItem("user_insurance", fullInsurance);
      localStorage.setItem("user_id", String(data.patient_id));
      localStorage.setItem("role", "patient");

      router.push("/dashboard/patient");
    } catch (err) {
      console.error(err);
      alert("Server error");
    }
  };

  return (
    <main className="min-h-screen flex items-center justify-center bg-white">
      <div className="w-[350px] space-y-4">
        <h1 className="text-xl font-semibold text-center">
          Register as Patient
        </h1>

        {/* NAME */}
        <div>
          <label>Name</label>
          <input
            className="w-full border p-2 rounded"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
        </div>

        {/* PHONE */}
        <div>
          <label>Phone</label>
          <input
            className="w-full border p-2 rounded"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
          />
        </div>

        {/* ADDRESS */}
        <div>
          <label>Address</label>
          <input
            className="w-full border p-2 rounded"
            value={address}
            onChange={(e) => setAddress(e.target.value)}
          />
        </div>

        {/* EMAIL */}
        <div>
          <label>Email</label>
          <input
            className="w-full border p-2 rounded"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </div>

        {/* INSURANCE */}
        <div>
          <label>Insurance</label>
          <div className="flex gap-2">
            <select
              className="border p-2 rounded"
              value={insurancePrefix}
              onChange={(e) => setInsurancePrefix(e.target.value)}
            >
              {INSURANCE_PREFIX.map((p) => (
                <option key={p}>{p}</option>
              ))}
            </select>

            <input
              className="flex-1 border p-2 rounded"
              placeholder="13 digits"
              value={insuranceNumber}
              onChange={(e) => setInsuranceNumber(e.target.value)}
            />
          </div>
        </div>

        {/* DOB */}
        <div>
          <label>Date of Birth</label>
          <input
            type="date"
            className="w-full border p-2 rounded"
            value={dob}
            onChange={(e) => setDob(e.target.value)}
          />
        </div>

        {/* GENDER */}
        <div>
          <label>Gender</label>
          <select
            className="w-full border p-2 rounded"
            value={gender}
            onChange={(e) => setGender(e.target.value)}
          >
            <option value="">Select</option>
            <option value="male">male</option>
            <option value="female">female</option>
          </select>
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
