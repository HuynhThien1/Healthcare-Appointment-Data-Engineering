"use client";
import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";

export default function MedicalRecordDetailPage() {
  const { slotId } = useParams();
  const [history, setHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [formData, setFormData] = useState({ diagnosis: "", prescription: "" });
  const router = useRouter();

  const fetchHistory = () => {
    fetch(`http://127.0.0.1:8000/records/slot/${slotId}`)
      .then(res => res.json())
      .then(data => {
        setHistory(data.data || []);
        // Fill form với data mới nhất để dễ modify
        if (data.data?.length > 0) {
          setFormData({
            diagnosis: data.data[0].diagnosis_note || "",
            prescription: data.data[0].prescription_note || ""
          });
        }
        setLoading(false);
      });
  };

  useEffect(() => { fetchHistory(); }, [slotId]);

  const handleSaveNewVersion = async () => {
    const res = await fetch(`http://127.0.0.1:8000/records/create-version`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        slot_id: slotId,
        patient_id: history[0]?.patient_id,
        diagnosis_note: formData.diagnosis,
        prescription_note: formData.prescription
      })
    });
    if (res.ok) {
      alert("New version created!");
      fetchHistory(); // Refresh danh sách
    }
  };

  if (loading) return <div className="p-10 text-center">Loading history...</div>;

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <button onClick={() => router.back()} className="mb-4 text-sm font-bold">← BACK</button>
      
      <h1 className="text-2xl font-bold mb-6">Patient: {history[0]?.patient_name}</h1>

      {/* FORM ADD/MODIFY */}
      <div className="bg-yellow-50 border-2 border-black p-6 mb-10 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
        <h3 className="font-black mb-4 uppercase">Create New Version / Modify</h3>
        <div className="space-y-4">
          <textarea 
            placeholder="Diagnosis"
            className="w-full border-2 border-black p-2"
            value={formData.diagnosis}
            onChange={e => setFormData({...formData, diagnosis: e.target.value})}
          />
          <textarea 
            placeholder="Prescription"
            className="w-full border-2 border-black p-2"
            value={formData.prescription}
            onChange={e => setFormData({...formData, prescription: e.target.value})}
          />
          <button 
            onClick={handleSaveNewVersion}
            className="bg-black text-white px-6 py-2 font-bold hover:bg-gray-800"
          >
            SAVE AS NEW VERSION
          </button>
        </div>
      </div>

      {/* VERSION HISTORY */}
      <div className="space-y-4">
        <h3 className="font-bold text-gray-500 uppercase tracking-tighter">Version History</h3>
        {history.map((v) => (
          <div key={v.record_id} className="border-l-4 border-black pl-4 py-2 bg-gray-50">
            <div className="flex justify-between text-xs font-mono mb-2">
              <span className="font-bold">VER: {v.version_number}</span>
              <span>{new Date(v.created_at).toLocaleString()}</span>
            </div>
            <p className="text-sm"><strong>Diagnosis:</strong> {v.diagnosis_note}</p>
            <p className="text-sm"><strong>Prescription:</strong> {v.prescription_note}</p>
          </div>
        ))}
      </div>
    </div>
  );
}