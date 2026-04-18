"use client";

import { useRouter, usePathname } from "next/navigation";
import { useEffect, useState } from "react";

export default function DoctorLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const pathname = usePathname();

  // ✅ init state từ localStorage (không cần setState trong effect)
  const [userId] = useState<string | null>(() => {
    if (typeof window === "undefined") return null;

    const role = localStorage.getItem("role");
    const id = localStorage.getItem("user_id");

    if (!role || !id || role !== "doctor") {
      return null;
    }

    return id;
  });

  // ✅ chỉ dùng effect để redirect (side-effect đúng nghĩa)
  useEffect(() => {
    if (!userId) {
      router.replace("/auth/login");
    }
  }, [userId, router]);

  if (!userId) return null;

  return (
    <div className="space-y-4">
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

        <button
          onClick={() => router.push("/dashboard/doctor/generate")}
          className={`px-4 py-1 rounded ${
            pathname.includes("generate")
              ? "bg-black text-white"
              : "bg-gray-200"
          }`}
        >
          Generate Schedule
        </button>
        <button
          onClick={() => router.push("/dashboard/doctor/medical-record")}
          className={`px-4 py-1 rounded ${
            pathname.includes("medical-record")
              ? "bg-black text-white"
              : "bg-gray-200"
          }`}
        >
          Medical Records
        </button>
      </div>

      <div>{children}</div>
    </div>
  );
}
