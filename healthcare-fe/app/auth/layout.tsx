"use client";

import { useState } from "react";
import { usePathname, useRouter } from "next/navigation";

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const router = useRouter();

  const isLogin = pathname.includes("login");

  return (
    <main className="min-h-screen flex flex-col items-center justify-center bg-white">
      <div className="w-[350px] space-y-6">

        {/* Toggle between pages */}
        <div className="flex border rounded-lg overflow-hidden">
          <button
            onClick={() => router.push("/auth/login")}
            className={`w-1/2 py-2 ${
              isLogin ? "bg-black text-white" : ""
            }`}
          >
            Login
          </button>
          <button
            onClick={() => router.push("/auth/register")}
            className={`w-1/2 py-2 ${
              !isLogin ? "bg-black text-white" : ""
            }`}
          >
            Register
          </button>
        </div>

        {/* Inject page content */}
        {children}
      </div>
    </main>
  );
}