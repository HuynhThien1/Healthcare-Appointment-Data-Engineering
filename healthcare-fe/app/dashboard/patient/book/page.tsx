"use client";

import { useEffect, useState } from "react";
import { SLOT_MAP } from "@/app/constants/slots";
type SlotStatus = "AVAILABLE" | "BOOKED" | "BLOCKED";
const getToday = () => {
  return new Date().toISOString().split("T")[0];
};
export default function PatientBookingPage() {
  const [doctorId, setDoctorId] = useState<string | null>(null);
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
  // =========================
  // INIT USER DATA
  // =========================
  useEffect(() => {
    setDoctorId(localStorage.getItem("selected_doctor_id"));
    setPatientId(localStorage.getItem("user_id"));
  }, []);

  // =========================
  // MIN DATE (>= TODAY + 2)
  // =========================
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
  // =========================
  // FETCH SLOTS
  // =========================
  useEffect(() => {
    if (!doctorId || !date) return;

    const fetchSlots = async () => {
      try {
        setLoading(true);

        const res = await fetch(
          `http://127.0.0.1:8000/slots/doctor/slots/${doctorId}/${date}`,
        );

        const data = await res.json();

        const mapped: Record<string, SlotStatus> = {};
        const ownerMap: Record<string, string> = {};
        const idMap: Record<string, string> = {};

        for (const s of data) {
          mapped[s.slot_code] = s.slot_status;

          if (s.slot_id) {
            idMap[s.slot_code] = s.slot_id;
          }

          if (s.slot_status === "BOOKED") {
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

  // =========================
  // VALIDATE DATE
  // =========================
  const isPastOrToday = (d: string) => {
    const today = new Date();
    const selected = new Date(d);

    today.setHours(0, 0, 0, 0);
    selected.setHours(0, 0, 0, 0);

    return selected <= today;
  };

  const isInvalidDate = date ? isPastOrToday(date) : true;

  // =========================
  // BOOK SLOT
  // =========================
  const handleBook = async (slot: string) => {
    if (!doctorId || !patientId || !date) return;

    if (isInvalidDate) {
      alert("Invalid date");
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
        headers: {
          "Content-Type": "application/json",
        },
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

      alert(`Booked successfully!\nTransaction: ${result.booking_ref}`);

      // update UI ngay lập tức
      setSlots((prev) => ({ ...prev, [slot]: "BOOKED" }));
      setSlotOwners((prev) => ({ ...prev, [slot]: patientId! }));
    } catch (err) {
      console.error(err);
      alert("Server error");
    }
  };

  // =========================
  // CANCEL SLOT
  // =========================
  const handleCancel = async (slot: string) => {
    if (!doctorId || !patientId || !date) return;

    const slotId = slotIds[slot];

    if (!slotId) {
      alert("Slot not found");
      return;
    }

    try {
      const res = await fetch("http://127.0.0.1:8000/appointments/cancel", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          slot_id: slotId,
          patient_id: Number(patientId),
        }),
      });

      if (!res.ok) {
        alert("Cancel failed");
        return;
      }

      alert("Cancelled");

      setSlots((prev) => ({ ...prev, [slot]: "AVAILABLE" }));
      setSlotOwners((prev) => {
        const copy = { ...prev };
        delete copy[slot];
        return copy;
      });
    } catch (err) {
      console.error(err);
      alert("Server error");
    }
  };

  if (!doctorId) return <div>Loading doctor...</div>;

  // =========================
  // UI
  // =========================
  return (
    
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <h1 className="text-xl font-semibold">Booking Doctor ID: {doctorId}</h1>

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

          if (!status) {
            return (
              <div key={slot} className="border p-3 bg-gray-100 rounded">
                <div>{slot}</div>
                <div>{time}</div>
                <div className="text-red-500">NOT AVAILABLE</div>
              </div>
            );
          }

          if (status === "BOOKED") {
            const isMine = slotOwners[slot] === patientId;

            if (isMine) {
              return (
                <div key={slot} className="border p-3 bg-pink-50 rounded">
                  <div>{slot}</div>
                  <div>{time}</div>
                  <div className="text-pink-600 font-bold">YOUR BOOKING</div>

                  <button
                    onClick={() => handleCancel(slot)}
                    className="mt-2 bg-pink-500 text-white px-2 py-1 rounded"
                  >
                    Cancel
                  </button>
                </div>
              );
            }

            return (
              <div key={slot} className="border p-3 bg-yellow-50 rounded">
                <div>{slot}</div>
                <div>{time}</div>
                <div className="text-red-500 font-bold">BOOKED</div>
              </div>
            );
          }

          if (status === "BLOCKED") {
            return (
              <div key={slot} className="border p-3 bg-gray-200 rounded">
                <div>{slot}</div>
                <div>{time}</div>
                <div className="text-gray-500">BLOCKED</div>
              </div>
            );
          }

          return (
            <div key={slot} className="border p-3 bg-green-50 rounded">
              <div>{slot}</div>
              <div>{time}</div>
              <div className="text-green-600 font-bold">AVAILABLE</div>

              <button
                disabled={isInvalidDate}
                onClick={() => handleBook(slot)}
                className="mt-2 bg-blue-500 text-white px-2 py-1 rounded"
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
