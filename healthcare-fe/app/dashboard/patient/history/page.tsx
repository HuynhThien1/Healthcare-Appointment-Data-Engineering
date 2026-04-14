"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

type Appointment = {
  doctor_id: string;
  slot_date: string;
  slot_code: string;
  booking_ref: string;
};

export default function PatientHistoryPage() {
  const [data, setData] = useState<Appointment[]>([]);
  const [filteredData, setFilteredData] = useState<Appointment[]>([]);
  const [patientId] = useState<string | null>(() => {
    if (typeof window !== "undefined") {
      return localStorage.getItem("user_id");
    }
    return null;
  });

  // filter
  const [selectedDate, setSelectedDate] = useState("");

  // pagination
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 5;

  const router = useRouter();

  // 📡 fetch data
  useEffect(() => {
    if (!patientId) return;

    const fetchData = async () => {
      const res = await fetch(
        `http://127.0.0.1:8000/appointments/appointments/patient/${patientId}`,
      );

      if (!res.ok) {
        console.error("API error:", res.status);
        return;
      }

      const d = await res.json();

      if (Array.isArray(d)) {
        setData(d);
        setFilteredData(d); // init
      }
    };

    fetchData();
  }, [patientId]);

  // 🔍 filter by date
  const handleFilter = () => {
    if (!selectedDate) {
      setFilteredData(data);
      setCurrentPage(1);
      return;
    }

    const filtered = data.filter(
      (item) => item.slot_date === selectedDate,
      // nếu backend trả datetime → dùng:
      // item.slot_date.slice(0, 10) === selectedDate
    );

    setFilteredData(filtered);
    setCurrentPage(1);
  };

  // 🔄 reset filter
  const handleReset = () => {
    setSelectedDate("");
    setFilteredData(data);
    setCurrentPage(1);
  };

  // 📄 pagination
  const totalPages = Math.ceil(filteredData.length / itemsPerPage);

  const startIndex = (currentPage - 1) * itemsPerPage;
  const currentData = filteredData.slice(startIndex, startIndex + itemsPerPage);

  // 🔥 navigation
  const handleClick = (appt: Appointment) => {
    localStorage.setItem("patient_selected_date", appt.slot_date);
    localStorage.setItem("selected_doctor_id", appt.doctor_id);

    router.push("/dashboard/patient/book");
  };

  return (
    <div className="max-w-3xl mx-auto p-6 space-y-4">
      <h1 className="text-xl font-semibold">My Appointments</h1>

      {/* 🔍 FILTER */}
      <div className="flex gap-2 items-center">
        <input
          type="date"
          className="border p-2"
          value={selectedDate}
          onChange={(e) => setSelectedDate(e.target.value)}
        />

        <button
          onClick={handleFilter}
          className="bg-blue-500 text-white px-4 py-2 rounded"
        >
          Confirm
        </button>

        <button onClick={handleReset} className="bg-gray-300 px-4 py-2 rounded">
          Reset
        </button>
      </div>

      {/* 📋 LIST */}
      {currentData.length === 0 ? (
        <div className="text-gray-500">No data</div>
      ) : (
        currentData.map((appt, idx) => (
          <div
            key={idx}
            className="border p-3 rounded bg-blue-50 cursor-pointer hover:bg-blue-100 transition"
            onClick={() => handleClick(appt)}
          >
            <div>
              <b>Date:</b> {appt.slot_date}
            </div>
            <div>
              <b>Slot:</b> {appt.slot_code}
            </div>
            <div>
              <b>Doctor:</b> {appt.doctor_id}
            </div>
          </div>
        ))
      )}

      {/* 📄 PAGINATION */}
      {totalPages > 1 && (
        <div className="flex gap-2 mt-4 items-center">
          <button
            disabled={currentPage === 1}
            onClick={() => setCurrentPage((p) => p - 1)}
            className="px-3 py-1 border disabled:opacity-50"
          >
            Prev
          </button>

          <span>
            Page {currentPage} / {totalPages}
          </span>

          <button
            disabled={currentPage === totalPages}
            onClick={() => setCurrentPage((p) => p + 1)}
            className="px-3 py-1 border disabled:opacity-50"
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}
