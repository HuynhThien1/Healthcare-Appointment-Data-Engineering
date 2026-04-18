"use client";

import { useEffect, useState, useMemo } from "react";
import React from "react";
import { DAYS, DAY_LABEL } from "@/app/constants/date";
import { SLOT_MAP, SlotCode } from "@/app/constants/slots";

type SlotState = "AVAILABLE" | "NOT AVAILABLE";

export default function GeneratePage() {
  const [grid, setGrid] = useState<Record<string, SlotState>>({});
  // Thay đổi: Cho phép chọn tháng/năm
  const [selectedMonth, setSelectedMonth] = useState(new Date().getMonth() + 3); // Mặc định month+2 (index+1+2)
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());

  const userId = useMemo(() => (typeof window !== "undefined" ? localStorage.getItem("user_id") : null), []);
  const SLOTS = useMemo(() => Object.keys(SLOT_MAP) as SlotCode[], []);

  // Tạo danh sách tháng từ tháng hiện tại + 2 đến 2050
  const monthOptions = useMemo(() => {
    const options = [];
    const now = new Date();
    // Bắt đầu từ tháng hiện tại + 2
    let startMonth = now.getMonth() + 1 + 2; 
    let startYear = now.getFullYear();
    
    if (startMonth > 12) {
        startMonth -= 12;
        startYear += 1;
    }

    for (let y = startYear; y <= 2050; y++) {
      for (let m = (y === startYear ? startMonth : 1); m <= 12; m++) {
        options.push({ month: m, year: y });
      }
    }
    return options;
  }, []);

  // FETCH DATA khi thay đổi tháng/năm
  useEffect(() => {
    if (!userId) return;
    setGrid({}); // Reset grid khi chuyển tháng

    fetch(`http://127.0.0.1:8000/schedule/preview/${userId}/${selectedYear}/${selectedMonth}`)
      .then((res) => res.json())
      .then((data) => {
        const fullGrid: Record<string, SlotState> = {};
        for (const d of DAYS) {
          for (const slot of SLOTS) {
            const key = `${d}_${slot}`;
            fullGrid[key] = data[key] === "GREEN" ? "AVAILABLE" : "NOT AVAILABLE";
          }
        }
        setGrid(fullGrid);
      });
  }, [userId, selectedMonth, selectedYear]);

  const toggle = (key: string) => {
    setGrid((prev) => ({
      ...prev,
      [key]: prev[key] === "AVAILABLE" ? "NOT AVAILABLE" : "AVAILABLE",
    }));
  };

  const handleConfirm = async () => {
    if (!userId) return;
    const slots = Object.entries(grid)
      .filter(([_, val]) => val === "AVAILABLE")
      .map(([key]) => {
        const [dow, slot_code] = key.split("_");
        return { dow: Number(dow), slot_code };
      });

    const res = await fetch("http://127.0.0.1:8000/schedule/confirm", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        doctor_id: userId,
        year: selectedYear,
        month: selectedMonth,
        slots,
      }),
    });

    if (res.ok) alert(`Schedule for ${selectedMonth}/${selectedYear} updated successfully!`);
  };

  if (!userId) return <div>Loading...</div>;

  return (
    <div className="space-y-4 p-4">
      <div className="flex items-center gap-4">
        <h1 className="text-xl font-semibold">Generate Schedule</h1>
        <select 
          className="border p-2 rounded"
          value={`${selectedMonth}-${selectedYear}`}
          onChange={(e) => {
            const [m, y] = e.target.value.split("-");
            setSelectedMonth(Number(m));
            setSelectedYear(Number(y));
          }}
        >
          {monthOptions.map(opt => (
            <option key={`${opt.month}-${opt.year}`} value={`${opt.month}-${opt.year}`}>
              Tháng {opt.month} / {opt.year}
            </option>
          ))}
        </select>
      </div>

      <div className="grid grid-cols-7 gap-2">
        <div></div>
        {DAY_LABEL.map((d) => <div key={d} className="text-center font-semibold">{d}</div>)}
        {SLOTS.map((slot) => (
          <React.Fragment key={slot}>
            <div className="font-semibold">{slot}<div className="text-xs text-gray-500">{SLOT_MAP[slot]}</div></div>
            {DAYS.map((d) => {
              const key = `${d}_${slot}`;
              const isAvailable = grid[key] === "AVAILABLE";
              return (
                <div key={key} onClick={() => toggle(key)}
                  className={`p-3 text-center cursor-pointer transition-colors border rounded ${
                    isAvailable ? "bg-green-200 text-black" : "bg-red-300 text-black"
                  }`}
                >
                  {isAvailable ? "AVAILABLE" : "NOT AVAILABLE"}
                </div>
              );
            })}
          </React.Fragment>
        ))}
      </div>

      <div className="flex justify-center mt-4">
        <button onClick={handleConfirm} className="bg-blue-600 text-white px-8 py-2 rounded-lg font-bold hover:bg-blue-700">
          Save & Apply Schedule
        </button>
      </div>
    </div>
  );
}