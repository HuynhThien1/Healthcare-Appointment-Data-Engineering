"use client";
import { useEffect, useState, useMemo } from "react";
import { useRouter } from "next/navigation";

export default function MedicalRecordListPage() {
  const [records, setRecords] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [doctorId, setDoctorId] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    const id = localStorage.getItem("user_id");
    if (id) setDoctorId(id);
    else router.push("/auth/login");
  }, []);

  useEffect(() => {
    if (doctorId) {
      fetch(`http://127.0.0.1:8000/records/doctor/${doctorId}`)
        .then((res) => res.json())
        .then((resData) => {
          setRecords(resData.data || []);
          setLoading(false);
        })
        .catch(() => setLoading(false));
    }
  }, [doctorId]);

  const filteredRecords = useMemo(() => {
    const keyword = searchTerm.toLowerCase();
    return records.filter((item) => 
      item.patient_name?.toLowerCase().includes(keyword) || 
      item.slot_code?.toLowerCase().includes(keyword)
    );
  }, [records, searchTerm]);

  if (loading) return <div className="p-10 text-center font-mono">LOADING_SYSTEM_DATA...</div>;

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <h1 className="text-2xl font-black mb-8 border-b-4 border-black pb-2">MEDICAL RECORDS INDEX</h1>
      
      <input
        type="text"
        placeholder="Filter by patient or slot code..."
        className="w-full border-2 border-black p-3 mb-8 focus:bg-yellow-50 outline-none"
        onChange={(e) => setSearchTerm(e.target.value)}
      />

      <div className="grid gap-4">
        {filteredRecords.map((item) => (
          <div
            key={item.slot_id}
            onClick={() => router.push(`/dashboard/doctor/medical-record/${item.slot_id}`)}
            className="cursor-pointer bg-white border-2 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:shadow-none hover:translate-x-1 hover:translate-y-1 transition-all p-5"
          >
            <div className="flex justify-between items-start mb-4">
              <div>
                <span className="bg-black text-white px-2 py-1 text-xs font-bold uppercase">Slot: {item.slot_code}</span>
                <h2 className="text-xl font-bold mt-2 uppercase">{item.patient_name}</h2>
              </div>
              <div className="text-right font-mono text-sm">
                <p className="font-bold">{item.slot_date}</p>
                <p className="text-gray-500">ID: {item.patient_id}</p>
              </div>
            </div>
            <div className="text-xs font-mono text-blue-600 font-bold uppercase tracking-widest">
              Click to view/edit history →
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}