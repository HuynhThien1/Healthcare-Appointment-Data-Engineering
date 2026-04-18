"use client";

import { useEffect, useState, useCallback } from "react";

type CalendarDay = {
  date: string;
  status: "NORMAL_DAY" | "HOLIDAY" | "WEEKEND";
  weekday_name: string;
};

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export default function AdminCalendar() {
  const [data, setData] = useState<CalendarDay[]>([]);
  const [selectedMonth, setSelectedMonth] = useState<Date>(new Date());

  // ===== FIX TIMEZONE =====
  const format = (d: Date) => {
    const offset = d.getTimezoneOffset();
    const local = new Date(d.getTime() - offset * 60000);
    return local.toISOString().split("T")[0];
  };

  // ===== RANGE =====
  const getMonthRange = (baseDate: Date) => {
    const year = baseDate.getFullYear();
    const month = baseDate.getMonth();

    return {
      start: format(new Date(year, month, 1)),
      end: format(new Date(year, month + 1, 0)),
    };
  };

  // ===== EDIT RULE =====
  const isEditableMonth = (selectedDate: Date) => {
    const now = new Date();
    const minEditable = new Date(now.getFullYear(), now.getMonth() + 2, 1);
    return selectedDate >= minEditable;
  };

  // ===== WEEKDAY (MON = 0) =====
  const getWeekdayIndex = (date: string) => {
    const d = new Date(date);
    const day = d.getDay(); // 0 = Sunday
    return day === 0 ? 6 : day - 1;
  };

  // ===== BUILD GRID =====
  const getCalendarGrid = (data: CalendarDay[]) => {
    if (data.length === 0) return [];

    const offset = getWeekdayIndex(data[0].date);
    const emptySlots = Array.from({ length: offset }, () => null);

    return [...emptySlots, ...data];
  };

  // ===== FETCH =====
  const fetchData = useCallback(async () => {
    try {
      const { start, end } = getMonthRange(selectedMonth);

      const res = await fetch(
        `${API_BASE_URL}/calendar/?start=${start}&end=${end}`
      );

      if (!res.ok) {
        throw new Error(`Fetch calendar failed: ${res.status}`);
      }

      const json = await res.json();

      if (Array.isArray(json)) setData(json);
      else if (Array.isArray(json.data)) setData(json.data);
      else setData([]);
    } catch (err) {
      console.error(err);
      setData([]);
    }
  }, [selectedMonth]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // ===== UPDATE =====
  const handleChange = async (date: string, status: string) => {
    
     try {
      const res = await fetch(`${API_BASE_URL}/calendar/update`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ date, status }),
      });

      if (!res.ok) {
        throw new Error(`Update calendar failed: ${res.status}`);
      }

      await fetchData();
    } catch (err) {
      console.error(err);
    }
  };

  // ===== CHANGE MONTH =====
  const handleMonthChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const [year, month] = e.target.value.split("-").map(Number);
    setSelectedMonth(new Date(year, month - 1, 1));
  };

  const editable = isEditableMonth(selectedMonth);
  const calendarGrid = getCalendarGrid(data);

  const today = format(new Date());

  return (
    <div className="p-6 space-y-4">
      <h1 className="text-xl font-bold">Admin - Holiday Management</h1>

      {/* chọn tháng */}
      <input
        type="month"
        onChange={handleMonthChange}
        className="border p-2 rounded"
      />

      {!editable && (
        <p className="text-red-500 text-sm">
          This schedule is already set. You can only edit schedules at least 2
          months in advance.
        </p>
      )}

      {/* HEADER */}
      <div className="grid grid-cols-7 text-center font-semibold">
        {["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"].map((d) => (
          <div key={d} className="p-2 border bg-gray-100">
            {d}
          </div>
        ))}
      </div>

      {/* CALENDAR */}
      <div className="grid grid-cols-7 gap-2">
        {calendarGrid.map((d, index) => {
          if (!d) return <div key={index} />;

          const isToday = d.date === today;

          return (
            <div
              key={d.date}
              className={`
                p-2 border rounded min-h-[90px] flex flex-col justify-between
                ${d.status === "NORMAL_DAY" ? "bg-green-100" : "bg-red-100"} 
                ${isToday ? "border-2 border-blue-500" : ""}
              `}
            >
              <div>
                <div className="text-sm font-semibold">{d.date}</div>
                <div className="text-xs text-gray-600">{d.weekday_name}</div>
              </div>

              <select
                value={d.status}
                disabled={!editable || d.status === "WEEKEND"}
                onChange={(e) => handleChange(d.date, e.target.value)}
                className="mt-2 text-sm border rounded p-1"
              >
                <option value="NORMAL_DAY">WORKING DAY</option>
                <option value="HOLIDAY">DAY OFF</option>
                {/* Thêm dòng này để hứng giá trị WEEKEND từ Database */}
                <option value="WEEKEND">WEEKEND</option> 
              </select>
            </div>
          );
        })}
      </div>
    </div>
  );
}
