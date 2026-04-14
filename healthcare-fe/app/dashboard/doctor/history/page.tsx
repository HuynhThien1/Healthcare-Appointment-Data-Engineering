"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

type Appointment = {
  patient_id: number;
  slot_id: string;
  slot_date: string;
  slot_code: string;
};

export default function DoctorHistoryPage() {
  const [data, setData] = useState<Appointment[]>([]);
  const [filteredData, setFilteredData] = useState<Appointment[]>([]);
  const [doctorId] = useState(() => localStorage.getItem("user_id"));

  // filter
  const [selectedDate, setSelectedDate] = useState("");

  // pagination
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 5;

  const router = useRouter();

  // 📡 fetch data
  useEffect(() => {
    if (!doctorId) return;

    const fetchData = async () => {
      const res = await fetch(
        `http://127.0.0.1:8000/appointments/appointments/doctor/${doctorId}`
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
  }, [doctorId]);

  // 🔍 filter by date
  const handleFilter = () => {
    if (!selectedDate) {
      setFilteredData(data);
      setCurrentPage(1);
      return;
    }

    const filtered = data.filter(
      (item) => item.slot_date === selectedDate
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

  // 📄 pagination logic
  const totalPages = Math.ceil(filteredData.length / itemsPerPage);

  const startIndex = (currentPage - 1) * itemsPerPage;
  const currentData = filteredData.slice(
    startIndex,
    startIndex + itemsPerPage
  );

  // 🔥 navigation
  const handleClick = (item: Appointment) => {
    localStorage.setItem("doctor_slot_date", item.slot_date);
    router.push("/dashboard/doctor/slots");
  };

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-semibold">Patient Bookings</h1>

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

        <button
          onClick={handleReset}
          className="bg-gray-300 px-4 py-2 rounded"
        >
          Reset
        </button>
      </div>

      {/* 📋 LIST */}
      {currentData.length === 0 ? (
        <div className="text-gray-500">No data</div>
      ) : (
        currentData.map((item, idx) => (
          <div
            key={idx}
            className="border p-3 cursor-pointer hover:shadow-md transition"
            onClick={() => handleClick(item)}
          >
            <div><b>Date:</b> {item.slot_date}</div>
            <div><b>Slot:</b> {item.slot_code}</div>
            <div><b>Patient:</b> {item.patient_id}</div>
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