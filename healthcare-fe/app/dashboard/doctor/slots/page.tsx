"use client";

import { useEffect, useState } from "react";
import { SLOT_MAP } from "@/app/constants/slots";

type SlotStatus = "AVAILABLE" | "BOOKED" | "BLOCKED";

type SlotResponse = {
  slot_code: string;
  slot_status: SlotStatus | null;
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
  const [slots, setSlots] = useState<Record<string, SlotStatus>>({});
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
  // 📡 fetch slots
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

        const mapped: Record<string, SlotStatus> = {};
        const patientTemp: Record<string, string> = {};

        for (const s of data) {
          if (s.slot_status) {
            mapped[s.slot_code] = s.slot_status;
          }

          if (s.slot_status === "BOOKED") {
            patientTemp[s.slot_code] = String(s.patient_id ?? "No patient");
          }
        }

        setSlots(mapped);
        setPatientMap(patientTemp); // ✅ không reset riêng nữa
      } catch (err) {
        console.error(err);
      }
    };

    fetchSlots();
  }, [date, userId]);

  // 📅 check past + today
  const isPastOrToday = (d: string) => {
    const today = new Date();
    const selected = new Date(d);

    today.setHours(0, 0, 0, 0);
    selected.setHours(0, 0, 0, 0);

    return selected <= today;
  };

  // 🔄 update slot
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
        [slot]: value,
      }));
    } catch (err) {
      console.error(err);
    }
  };

  // 🔥 VIEW PATIENT
  // const handleViewPatient = async (slot: string) => {
  //   if (!userId || !date) return;

  //   try {
  //     const res = await fetch(
  //       `http://127.0.0.1:8000/slots/doctor/${userId}/${date}/${slot}/patient`,
  //     );

  //     const data = await res.json();

  //     setPatientMap((prev) => ({
  //       ...prev,
  //       [slot]: String(data?.patient_id ?? "No patient"),
  //     }));
  //   } catch (err) {
  //     console.error(err);
  //   }
  // };

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
          const status = slots[slot];

          // ❌ NOT AVAILABLE
          if (!status) {
            return (
              <div key={slot} className="border p-3 bg-gray-100">
                <div>{slot}</div>
                <div>{time}</div>
                <div className="text-red-500">NOT AVAILABLE</div>
              </div>
            );
          }

          // 🔥 BOOKED
          if (status === "BOOKED") {
            return (
              <div key={slot} className="border p-3 bg-yellow-50 space-y-2">
                <div>{slot}</div>
                <div>{time}</div>
                <div className="text-red-500 font-bold">BOOKED</div>

                {/* <button
                  onClick={() => handleViewPatient(slot)}
                  className="text-blue-600 underline"
                >
                  View Patient
                </button> */}

                {patientMap[slot] && <div>Patient: {patientMap[slot]}</div>}
              </div>
            );
          }

          // ⛔ PAST
          if (isPastOrToday(date)) {
            return (
              <div key={slot} className="border p-3 bg-gray-100">
                <div>{slot}</div>
                <div>{time}</div>
                <div>{status}</div>
                <div className="text-gray-500">LOCKED</div>
              </div>
            );
          }

          // ✅ NORMAL
          return (
            <div key={slot} className="border p-3">
              <div>{slot}</div>
              <div>{time}</div>
              <div>{status}</div>

              <select
                value={status}
                onChange={(e) =>
                  handleUpdate(slot, e.target.value as SlotStatus)
                }
              >
                <option value="AVAILABLE">Available</option>
                <option value="BLOCKED">Blocked</option>
              </select>
            </div>
          );
        })}
      </div>
    </div>
  );
}
