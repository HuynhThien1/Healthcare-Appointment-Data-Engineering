"use client";
import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";

export default function PatientRecordDetail() {
  const { slotId } = useParams();
  const [history, setHistory] = useState<any[]>([]);
  const router = useRouter();

  useEffect(() => {
    fetch(`http://127.0.0.1:8000/records/slot/${slotId}`)
      .then(res => res.json())
      .then(data => setHistory(data.data || []));
  }, [slotId]);

  return (
    <div className="max-w-3xl mx-auto p-4">
      <button onClick={() => router.back()} className="text-blue-600 mb-6 font-medium">← Quay lại danh sách</button>
      
      <h2 className="text-2xl font-bold mb-2">Profile details</h2>
      <p className="text-gray-500 mb-8 font-mono">SLOT_ID: {slotId}</p>

      <div className="space-y-6">
        {history.map((v) => (
          <div key={v.record_id} className="bg-white border-2 border-gray-100 rounded-xl p-6 shadow-sm">
            <div className="flex justify-between items-center border-b pb-3 mb-4">
              <span className="font-black text-blue-700">VERSION {v.version_number}</span>
              <span className="text-xs text-gray-400">{new Date(v.created_at).toLocaleString('vi-VN')}</span>
            </div>
            
            <div className="grid gap-4">
              <div>
                <label className="text-[10px] uppercase font-bold text-gray-400">Chẩn đoán</label>
                <p className="text-gray-800 bg-gray-50 p-3 rounded mt-1">{v.diagnosis_note || "Trống"}</p>
              </div>
              <div>
                <label className="text-[10px] uppercase font-bold text-gray-400">Đơn thuốc</label>
                <p className="text-gray-800 bg-gray-50 p-3 rounded mt-1">{v.prescription_note || "Trống"}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}