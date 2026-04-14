"use client";

import { useRouter, usePathname } from "next/navigation";

export default function PatientLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const pathname = usePathname();

  return (
    <div className="min-h-screen bg-gray-50">
      {/* HEADER */}
      <div className="bg-white border-b px-6 py-4 flex justify-between items-center">
        <h1 className="text-lg font-semibold text-gray-700">
          Patient Dashboard
        </h1>

        <div className="flex gap-2">
          <button
            onClick={() => router.push("/dashboard/patient")}
            className={`btn ${
              pathname === "/dashboard/patient"
                ? "btn-primary"
                : "btn-secondary"
            }`}
          >
            Home
          </button>

          <button
            onClick={() => router.push("/dashboard/patient/history")}
            className={`btn ${
              pathname.includes("history") ? "btn-primary" : "btn-secondary"
            }`}
          >
            History
          </button>
        </div>
      </div>

      {/* CONTENT */}
      <div className="p-6">{children}</div>
    </div>
  );
}
