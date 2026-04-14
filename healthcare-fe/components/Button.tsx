"use client";

import { useRouter } from "next/navigation";

type ButtonProps = {
  label: string;
  href: string;
};

export default function Button({ label, href }: ButtonProps) {
  const router = useRouter();

  return (
    <button
      onClick={() => router.push(href)}
      className="
        w-64 h-40
        bg-blue-500 text-white
        rounded-3xl
        flex items-center justify-center
        text-lg font-medium
        hover:bg-blue-600 transition
      "
    >
      {label}
    </button>
  );
}