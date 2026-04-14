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

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setMounted(true);

    const r = localStorage.getItem("role");
    const id = localStorage.getItem("user_id");

    if (!r || !id) {
      router.push("/auth/login");
    } else {
      setRole(r);
      setUserId(id);
    }
  }, [router]);

  // ❗ QUAN TRỌNG: tránh mismatch
  if (!mounted || !role || !userId) return null;

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="flex justify-between items-center p-4 bg-white shadow">
        <div className="font-medium">
          {role === "doctor" ? "Doctor" : "Patient"} ID: {userId}
        </div>

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

      <div className="p-6">{children}</div>
    </div>
  );
}