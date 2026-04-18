"use client";

import { useEffect, useState } from "react";
import { SLOT_MAP } from "@/app/constants/slots";

type SlotStatus = "AVAILABLE" | "BOOKED" | "BLOCKED";

type SlotResponse = {
  slot_code: string;
  slot_status: "AVAILABLE" | "BLOCKED" | "BOOKED" | null;
  admin_status: "AVAILABLE" | "BLOCKED";
  patient_id?: number | null;
};

const getToday = () => {
  return new Date().toISOString().split("T")[0];
};

export default function SlotPage() {
  const [date, setDate] = useState<string>(() => {
    if (typeof window === "undefined") return "";
    const saved = localStorage.getItem("doctor_slot_date");
    return saved ? saved : getToday();
  });

  const [slots, setSlots] = useState<Record<string, SlotResponse>>({});

  const [userId, setUserId] = useState<string | null>(() => {
    if (typeof window !== "undefined") {
      return localStorage.getItem("user_id");
    }
    return null;
  });

  const [patientMap, setPatientMap] = useState<Record<string, string>>({});

  useEffect(() => {
    if (date) {
      localStorage.setItem("doctor_slot_date", date);
    }
  }, [date]);

  useEffect(() => {
    if (!date || !userId) return;

    const fetchSlots = async () => {
      try {
        const res = await fetch(
          `http://127.0.0.1:8000/slots/doctor/slots/${userId}/${date}`,
        );

        if (!res.ok) {
          setSlots({});
          return;
        }

        const data: SlotResponse[] = await res.json();

        const mapped: Record<string, SlotResponse> = {};
        const patientTemp: Record<string, string> = {};

        for (const s of data) {
          mapped[s.slot_code] = s;

          if (s.slot_status === "BOOKED") {
            patientTemp[s.slot_code] = String(s.patient_id ?? "No patient");
          }
        }

        setSlots(mapped);
        setPatientMap(patientTemp);
      } catch (err) {
        console.error(err);
      }
    };

    fetchSlots();
  }, [date, userId]);

  const isPastOrToday = (d: string) => {
    const today = new Date();
    const selected = new Date(d);

    today.setHours(0, 0, 0, 0);
    selected.setHours(0, 0, 0, 0);

    return selected <= today;
  };

  const handleUpdate = async (slot: string, value: SlotStatus) => {
    if (!date || !userId) return;

    try {
      const res = await fetch(
        `http://127.0.0.1:8000/slots/doctor/slot/${userId}/${date}/${slot}/${value}`,
        { method: "PUT" },
      );

      if (!res.ok) {
        alert("Update failed");
        return;
      }

      setSlots((prev) => ({
        ...prev,
        [slot]: {
          ...prev[slot],
          slot_status: value,
        },
      }));
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-semibold">Manage Slots</h1>

      <input
        type="date"
        className="border p-2"
        value={date}
        onChange={(e) => setDate(e.target.value)}
      />

      <div className="grid grid-cols-2 gap-4">
        {Object.entries(SLOT_MAP).map(([slot, time]) => {
          const slotData = slots[slot];
          const status: SlotStatus | null = slotData?.slot_status;

          // 1. Phân biệt Admin Block
          const isAdminBlocked = slotData?.admin_status === "BLOCKED";

          // Chưa được tạo trong database (Slot trống hoàn toàn)
          if (!slotData || slotData.slot_status === null) {
            return (
              <div
                key={slot}
                className="border p-3 bg-gray-50 flex flex-col gap-1"
              >
                <div className="font-bold">{slot}</div>
                <div className="text-sm">{time}</div>
                <div className="text-gray-400 text-sm">NOT AVAILABLE</div>
              </div>
            );
          }

          // ==========================================
          // TRƯỜNG HỢP 1: BỊ ADMIN KHÓA (Do ngày lễ/nghỉ)
          // ==========================================
          if (isAdminBlocked) {
            return (
              <div
                key={slot}
                className="border p-3 bg-red-100 flex flex-col gap-1"
              >
                <div className="font-bold">{slot}</div>
                <div className="text-sm">{time}</div>
                <div className="text-red-600 font-bold text-sm flex items-center gap-1">
                  🔒 BLOCKED BY ADMIN
                </div>
                <span className="text-xs text-red-500">
                  Holiday / System Off
                </span>
              </div>
            );
          }

          // ==========================================
          // TRƯỜNG HỢP 2: ĐÃ CÓ BỆNH NHÂN ĐẶT (BOOKED)
          // ==========================================
          if (slotData.slot_status === "BOOKED") {
            return (
              <div
                key={slot}
                className="border p-3 bg-yellow-100 flex flex-col gap-1"
              >
                <div className="font-bold">{slot}</div>
                <div className="text-sm">{time}</div>
                <div className="text-yellow-700 font-bold text-sm">
                  ✅ BOOKED
                </div>
                {patientMap[slot] && (
                  <div className="text-xs text-gray-700 font-medium">
                    Patient ID: {patientMap[slot]}
                  </div>
                )}
              </div>
            );
          }

          // ==========================================
          // TRƯỜNG HỢP 3: SLOT TRONG QUÁ KHỨ HOẶC HÔM NAY (Không cho sửa nữa)
          // ==========================================
          if (isPastOrToday(date)) {
            return (
              <div
                key={slot}
                className="border p-3 bg-gray-200 opacity-70 flex flex-col gap-1"
              >
                <div className="font-bold">{slot}</div>
                <div className="text-sm">{time}</div>
                <div className="text-gray-500 font-semibold text-sm">
                  {status === "BLOCKED" ? "🛑 DOCTOR BLOCKED" : status}
                </div>
                <div className="text-xs text-gray-500 italic">
                  Locked (Past/Today)
                </div>
              </div>
            );
          }

          // ==========================================
          // TRƯỜNG HỢP 4: AVAILABLE & NORMAL BLOCKED (Bác sĩ tự khóa)
          // ==========================================
          const currentStatus = status || "AVAILABLE";

          const safeStatus: SlotStatus =
            currentStatus === "AVAILABLE" || currentStatus === "BOOKED"
              ? currentStatus
              : "BLOCKED";

          const bgColor =
            safeStatus === "AVAILABLE"
              ? "bg-green-50 border-green-200"
              : "bg-gray-200 border-gray-300";

          return (
            <div
              key={slot}
              className={`border p-3 flex flex-col gap-2 ${bgColor}`}
            >
              <div>
                <div className="font-bold">{slot}</div>
                <div className="text-sm">{time}</div>
              </div>

              {safeStatus === "BLOCKED" && (
                <div className="text-xs text-gray-600 font-semibold">
                  🛑 Blocked by you
                </div>
              )}

              <select
                className="border border-gray-300 p-1 rounded text-sm w-full outline-none focus:ring-2 focus:ring-blue-400 bg-white"
                value={safeStatus}
                onChange={(e) =>
                  handleUpdate(slot, e.target.value as SlotStatus)
                }
              >
                <option value="AVAILABLE">✅ Available</option>
                <option value="BLOCKED">🛑 Block (Manual)</option>
              </select>
            </div>
          );
        })}
      </div>
    </div>
  );
}
