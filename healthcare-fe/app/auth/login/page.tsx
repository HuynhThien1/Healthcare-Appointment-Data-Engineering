"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function LoginPage() {
  const [role, setRole] = useState<"doctor" | "patient">("patient");
  const [id, setId] = useState("");
  const router = useRouter();

  const handleLogin = async () => {
    try {
      if (!id) {
        alert("Please enter ID");
        return;
      }

      // 🔥 validate nhẹ
      if (role === "doctor" && !id.startsWith("DR")) {
        alert("Doctor ID must be like DR001");
        return;
      }

      const res = await fetch(`http://127.0.0.1:8000/auth/login/${role}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          [`${role}_id`]: id,
        }),
      });

      const data = await res.json();

      if (!res.ok) {
        alert(data.message || "Login failed");
        return;
      }

      localStorage.setItem("role", role);
      localStorage.setItem("user_id", id);

      if (role === "doctor") {
        router.push("/dashboard/doctor/slots");
      } else {
        router.push("/dashboard/patient");
      }
    } catch (err) {
      console.error("Login error:", err);
      alert("Server error");
    }
  };

  return (
    <main className="min-h-screen flex flex-col items-center justify-center bg-white">
      <div className="w-[350px] space-y-6">
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
          Login as {role} (ID)
        </h1>

        <input
          type="text"
          placeholder={role === "doctor" ? "DR001" : "1"}
          className="w-full border p-2 rounded"
          value={id}
          onChange={(e) => setId(e.target.value)}
        />

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