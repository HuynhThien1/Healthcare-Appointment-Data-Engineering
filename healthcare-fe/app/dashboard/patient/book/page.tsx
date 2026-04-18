"use client";

import { useEffect, useState } from "react";
import { SLOT_MAP } from "@/app/constants/slots";

type SlotStatus = "AVAILABLE" | "BOOKED" | "BLOCKED" | "NOT_AVAILABLE";

const getToday = () => {
  return new Date().toISOString().split("T")[0];
};

export default function PatientBookingPage() {
  const [doctorId, setDoctorId] = useState<string | null>(null);
  const [insurance, setInsurance] = useState<string | null>(null);
  const [patientId, setPatientId] = useState<string | null>(null);

  const [date, setDate] = useState<string>(() => {
    if (typeof window === "undefined") return "";
    const saved = localStorage.getItem("patient_selected_date");
    return saved ? saved : getToday();
  });

  const [slots, setSlots] = useState<Record<string, SlotStatus>>({});
  const [slotOwners, setSlotOwners] = useState<Record<string, string>>({});
  const [slotIds, setSlotIds] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);

  // KHOI TAO DU LIEU NGUOI DUNG
  useEffect(() => {
    setDoctorId(localStorage.getItem("selected_doctor_id"));
    setInsurance(localStorage.getItem("user_insurance"));
    setPatientId(localStorage.getItem("user_id"));
  }, []);

  // LAY NGAY TOI THIEU (TODAY + 2)
  const getTwoDate = () => {
    const d = new Date();
    d.setDate(d.getDate() + 2);
    return d.toISOString().split("T")[0];
  };

  useEffect(() => {
    if (date) {
      localStorage.setItem("patient_selected_date", date);
    }
  }, [date]);

  // FETCH SLOTS TU API
  useEffect(() => {
    if (!doctorId || !date) return;

    setSlots({});
    setSlotOwners({});
    setSlotIds({});
    const fetchSlots = async () => {
      try {
        setLoading(true);
        const res = await fetch(
          `http://127.0.0.1:8000/slots/doctor/slots/${doctorId}/${date}`
        );
        const data = await res.json();
        if (!res.ok) {
          setSlots({});
          return;
        }

        const mapped: Record<string, SlotStatus> = {};
        const ownerMap: Record<string, string> = {};
        const idMap: Record<string, string> = {};

        for (const s of data) {
          let status: SlotStatus;
          if (s.slot_status === "AVAILABLE") {
            status = "AVAILABLE";
          } else if (s.slot_status === "BOOKED") {
            status = "BOOKED";
          } else if (s.slot_status === "BLOCKED") {
            status = "BLOCKED";
          } else {
            status = "NOT_AVAILABLE";
          }

          mapped[s.slot_code] = status;
          if (s.slot_id) idMap[s.slot_code] = s.slot_id;
          if (status === "BOOKED") {
            ownerMap[s.slot_code] = String(s.patient_id || "");
          }
        }

        setSlots(mapped);
        setSlotOwners(ownerMap);
        setSlotIds(idMap);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchSlots();
  }, [doctorId, date]);

  // KIEM TRA NGAY CO TRUOC (TODAY + 2) KHONG
  const isBeforeTwoDays = (d: string) => {
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    const minValidDate = new Date(today);
    minValidDate.setDate(minValidDate.getDate() + 2);

    const selected = new Date(d);
    selected.setHours(0, 0, 0, 0);

    return selected < minValidDate;
  };

  const isInvalidDate = date ? isBeforeTwoDays(date) : true;

  // XU LY DAT LICH
  const handleBook = async (slot: string) => {
    if (!doctorId || !insurance || !date) return;
    if (isInvalidDate) {
      alert("Invalid date: Booking must be at least 2 days in advance");
      return;
    }

    const slotId = slotIds[slot];
    if (!slotId) {
      alert("Slot not found");
      return;
    }

    try {
      const res = await fetch("http://127.0.0.1:8000/appointments", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          slot_id: slotId,
          patient_id: Number(patientId),
        }),
      });

      if (!res.ok) {
        alert("Booking failed");
        return;
      }

      const result = await res.json();
      if (!result.success) {
        alert(result.message);
        return;
      }

      alert(`Booked successfully!\nTransaction: ${result.booking_ref}`);
      setSlots((prev) => ({ ...prev, [slot]: "BOOKED" }));
      setSlotOwners((prev) => ({ ...prev, [slot]: String(patientId) }));
    } catch (err) {
      console.error(err);
      alert("Server error");
    }
  };

  // XU LY HUY LICH
  const handleCancel = async (slot: string) => {
    if (!doctorId || !insurance || !date) return;
    const slotId = slotIds[slot];
    if (!slotId) return;

    try {
      const res = await fetch("http://127.0.0.1:8000/appointments/cancel", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          slot_id: slotId,
          insurance_number: insurance,
        }),
      });

      if (!res.ok) {
        alert("Cancel failed");
        return;
      }

      alert("Cancelled");
      setSlots((prev) => ({ ...prev, [slot]: "AVAILABLE" }));
      setSlotOwners((prev) => {
        const newOwners = { ...prev };
        delete newOwners[slot];
        return newOwners;
      });
    } catch (err) {
      console.error(err);
    }
  };

  if (!doctorId) return <div>Loading doctor...</div>;

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <h1 className="text-xl font-semibold">Booking Doctor ID: {doctorId}</h1>
      <div className="text-sm text-gray-500">Insurance: {insurance}</div>

      <input
        type="date"
        className="border p-2 rounded"
        value={date}
        min={getTwoDate()}
        onChange={(e) => setDate(e.target.value)}
      />

      {loading && <p>Loading slots...</p>}

      <div className="grid grid-cols-2 gap-4">
        {Object.entries(SLOT_MAP).map(([slot, time]) => {
          const status = slots[slot];

          // TRUONG HOP 1: SLOT CHUA DUOC TAO
          if (!status) {
            return (
              <div key={slot} className="border p-3 bg-gray-100 rounded">
                <div className="font-bold">{slot}</div>
                <div className="text-sm">{time}</div>
                <div className="text-red-500 text-sm mt-1">NOT AVAILABLE</div>
              </div>
            );
          }

          // TRUONG HOP 2: SLOT DA DUOC DAT
          if (status === "BOOKED") {
            const isMySlot = slotOwners[slot] === patientId;
            return (
              <div
                key={slot}
                className={`border p-3 rounded ${isMySlot ? "bg-pink-100" : "bg-yellow-50"}`}
              >
                <div className="font-bold">{slot}</div>
                <div className="text-sm">{time}</div>
                <div className={`font-bold mt-1 ${isMySlot ? "text-pink-600" : "text-red-500"}`}>
                  BOOKED
                </div>
                {isMySlot && (
                  <button
                    onClick={() => handleCancel(slot)}
                    className="mt-2 bg-red-500 text-white px-2 py-1 rounded text-xs"
                  >
                    Cancel
                  </button>
                )}
              </div>
            );
          }

          // TRUONG HOP 3: SLOT BI ADMIN HOAC BAC SI KHOA
          if (status === "BLOCKED") {
            return (
              <div key={slot} className="border p-3 bg-gray-300 rounded">
                <div className="font-bold">{slot}</div>
                <div className="text-sm">{time}</div>
                <div className="text-red-600 font-bold mt-1">BLOCKED</div>
              </div>
            );
          }

          // TRUONG HOP 4: SLOT KHONG KHA DUNG
          if (status === "NOT_AVAILABLE") {
            return (
              <div key={slot} className="border p-3 bg-gray-200 rounded">
                <div className="font-bold">{slot}</div>
                <div className="text-sm">{time}</div>
                <div className="text-gray-500 mt-1">NOT AVAILABLE</div>
              </div>
            );
          }

          // TRUONG HOP 5: SLOT TRONG NHUNG NGAY CHON < TODAY + 2 (HIEN QUA KHU)
          if (isInvalidDate) {
            return (
              <div key={slot} className="border p-3 bg-gray-200 rounded opacity-70">
                <div className="font-bold">{slot}</div>
                <div className="text-sm">{time}</div>
                <div className="text-gray-500 font-bold mt-1">PAST</div>
                <div className="text-xs text-gray-500 italic">Expired</div>
              </div>
            );
          }

          // TRUONG HOP 6: AVAILABLE VA CO THE DAT
          return (
            <div key={slot} className="border p-3 bg-green-50 rounded">
              <div className="font-bold">{slot}</div>
              <div className="text-sm">{time}</div>
              <div className="text-green-600 font-bold mt-1">AVAILABLE</div>
              <button
                onClick={() => handleBook(slot)}
                className="mt-2 bg-blue-500 text-white px-3 py-1 rounded text-sm hover:bg-blue-600"
              >
                Book
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
}