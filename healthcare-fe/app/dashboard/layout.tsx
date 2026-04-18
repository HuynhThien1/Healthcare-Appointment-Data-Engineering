"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();

  const [mounted, setMounted] = useState(false);
  const [role, setRole] = useState<string | null>(null);
  const [userId, setUserId] = useState<string | null>(null);
  const [insurance, setInsurance] = useState<string | null>(null);
  const getTodayFormatted = () => {
    const today = new Date();

    const day = String(today.getDate()).padStart(2, "0");
    const month = String(today.getMonth() + 1).padStart(2, "0");
    const year = today.getFullYear();

    return `${day}/${month}/${year}`;
  };

  useEffect(() => {
    setMounted(true);

    const r = localStorage.getItem("role");
    const id = localStorage.getItem("user_id");
    const ins = localStorage.getItem("user_insurance");

    if (!r || !id) {
      router.push("/auth/login");
    } else {
      setRole(r);
      setUserId(id);
      setInsurance(ins);
    }
  }, [router]);

  if (!mounted || !role || !userId) return null;

  return (
    <div className="min-h-screen bg-gray-100">
      {/* HEADER */}
      <div className="grid grid-cols-3 items-center p-4 bg-white shadow">
        {/* LEFT */}
        <div className="font-medium">
          {role === "doctor"
            ? `Doctor ID: ${userId}`
            : `Patient Insurance: ${insurance}`}
        </div>

        {/* CENTER */}
        <div className="text-xl font-semibold text-gray-700 text-center">
          Date: {getTodayFormatted()}
        </div>

        {/* RIGHT */}
        <div className="flex justify-end">
          <button
            onClick={() => {
              localStorage.clear();
              router.push("/auth/login");
            }}
            className="px-4 py-2 bg-black text-white rounded"
          >
            Logout
          </button>
        </div>
      </div>

      {/* CONTENT */}
      <div className="p-6">{children}</div>
    </div>
  );
}
