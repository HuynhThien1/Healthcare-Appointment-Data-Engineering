"use client";

import { useRouter, usePathname } from "next/navigation";
import { useEffect, useState } from "react";

type Doctor = {
  doctor_id: number;
  doctor_name: string;
  specialty: string;
};

export default function DoctorLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const pathname = usePathname();

  const [mounted, setMounted] = useState(false);
  const [userId, setUserId] = useState<string | null>(null);
  const [doctor, setDoctor] = useState<Doctor | null>(null);
  const [loadingDoctor, setLoadingDoctor] = useState(true);

  // 🔐 Effect 1: Auth + lấy userId
  useEffect(() => {
    setMounted(true);

    const role = localStorage.getItem("role");
    const id = localStorage.getItem("user_id");

    if (!role || !id || role !== "doctor") {
      router.replace("/auth/login");
      return;
    }

    setUserId(id);
  }, [router]);

  // 📡 Effect 2: fetch doctor (🔥 đúng dependency)
  useEffect(() => {
    if (!userId) return;

    const fetchDoctor = async () => {
      try {
        const res = await fetch(
          `http://127.0.0.1:8000/doctors/${userId}`, // ⚠️ nhớ đúng endpoint
        );

        if (!res.ok) {
          console.error("Doctor fetch failed:", res.status);
          return;
        }

        const data: Doctor = await res.json();
        console.log("Doctor data:", data);

        setDoctor(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoadingDoctor(false);
      }
    };

    fetchDoctor();
  }, [userId]);

  // 🔒 tránh hydration mismatch
  if (!mounted || !userId) return null;

  return (
    <div className="space-y-4">
      {/* Tabs */}
      <div className="flex gap-2">
        <button
          onClick={() => router.push("/dashboard/doctor/slots")}
          className={`px-4 py-1 rounded ${
            pathname.includes("slots") ? "bg-black text-white" : "bg-gray-200"
          }`}
        >
          Manage Slots
        </button>

        <button
          onClick={() => router.push("/dashboard/doctor/history")}
          className={`px-4 py-1 rounded ${
            pathname.includes("history") ? "bg-black text-white" : "bg-gray-200"
          }`}
        >
          Booking History
        </button>
      </div>

      {/* 🔥 QUAN TRỌNG */}
      <div>{children}</div>
    </div>
  );
}
