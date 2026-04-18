
"use client";
import { useEffect, useState, useMemo } from "react";
import { useRouter } from "next/navigation";

export default function PatientMedicalRecordPage() {
  const [records, setRecords] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const router = useRouter();

  useEffect(() => {
    const insurance = localStorage.getItem("user_insurance");

    if (!insurance) {
      console.error("No insurance found in storage");
      setLoading(false);
      return;
    }

    fetch(`http://127.0.0.1:8000/records/patient-insurance/${insurance}`)
      .then((res) => res.json())
      .then((resData) => {
        setRecords(resData.data || []);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Fetch error:", err);
        setLoading(false);
      });
  }, []);

  // 🔍 Filter records theo doctor_name + doctor_id
  const filteredRecords = useMemo(() => {
    const keyword = searchTerm.toLowerCase();

    return records.filter((rec) => {
      return (
        rec.doctor_name?.toLowerCase().includes(keyword) ||
        rec.doctor_id?.toLowerCase().includes(keyword)
      );
    });
  }, [records, searchTerm]);

  if (loading) {
    return (
      <div className="p-10 text-center font-mono">
        LOADING_RECORDS...
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-xl font-bold mb-6 border-l-4 border-blue-600 pl-3 uppercase">
        Medical history
      </h1>

      {/* 🔍 Search box */}
      <input
        type="text"
        placeholder="Search doctor name or ID..."
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        className="w-full mb-4 p-2 border-2 border-black font-mono"
      />

      <div className="grid gap-4">
        {filteredRecords.length > 0 ? (
          filteredRecords.map((rec) => (
            <div
              key={`${rec.slot_id}-${rec.version_number}`} // ✅ fix duplicate key
              onClick={() =>
                router.push(`/dashboard/patient/medical-record/${rec.slot_id}`)
              }
              className="bg-white p-4 border-2 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-none transition-all cursor-pointer flex justify-between items-center"
            >
              <div>
                <p className="text-xs text-gray-500 font-mono mb-1">
                  SLOT: {rec.slot_code}
                </p>
                <h3 className="font-black text-lg text-gray-800">
                  Bác sĩ: {rec.doctor_name}
                </h3>
                <p className="text-sm font-bold text-blue-600">
                  ID: {rec.doctor_id}
                </p>
              </div>

              <div className="text-right">
                <p className="font-black text-gray-700">{rec.date}</p>
                <span className="text-[10px] bg-black text-white px-2 py-1 font-mono uppercase">
                  Ver: {rec.version_number}
                </span>
              </div>
            </div>
          ))
        ) : (
          <div className="p-10 border-2 border-dashed border-gray-300 text-center text-gray-400">
            {searchTerm
              ? "Không tìm thấy kết quả phù hợp."
              : "Chưa có dữ liệu hồ sơ cho mã bảo hiểm này."}
          </div>
        )}
      </div>
    </div>
  );
}
