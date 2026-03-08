import React, { useState, useEffect, useCallback } from 'react';
import { History as HistoryIcon, RefreshCw, Clock, FileVideo, FileText, AlertTriangle } from 'lucide-react';
import { API_ENDPOINT } from '../constants';
import { convertToCSVAndDownload } from '../utils/csv';

const HistoryPage = ({ token }) => {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchHistory = useCallback(() => {
    setLoading(true);
    fetch(`${API_ENDPOINT}/api/history`, { headers: { Authorization: `Bearer ${token}` } })
      .then(r => {
        if (!r.ok) throw new Error("Failed");
        return r.json();
      })
      .then(data => {
        if (Array.isArray(data)) setHistory(data);
        else setHistory([]);
      })
      .catch(() => setHistory([]))
      .finally(() => setLoading(false));
  }, [token]);

  useEffect(() => { fetchHistory(); }, [fetchHistory]);

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl text-white font-bold flex items-center gap-2"><HistoryIcon className="text-blue-400" /> History</h2>
        <button onClick={fetchHistory} className="text-slate-400 hover:text-white p-2 rounded hover:bg-slate-800"><RefreshCw size={18} /></button>
      </div>

      {loading ? (
        <div className="text-center p-10 text-slate-400">Loading history...</div>
      ) : history.length === 0 ? (
        <div className="text-center p-10 bg-slate-800 rounded-xl border border-slate-700 text-slate-400">
          <HistoryIcon className="mx-auto w-12 h-12 mb-2 opacity-50" />
          <p>No history records found.</p>
        </div>
      ) : (
        <div className="grid gap-6 md:grid-cols-2">
          {history.map(h => (
            <div key={h.id} className="bg-slate-800 p-6 rounded-xl text-white border border-slate-700 shadow-lg">
              <div className="flex justify-between items-start mb-2">
                <div className="font-bold text-lg truncate flex-1" title={h.original_filename}>{h.original_filename}</div>
                <div className="text-xs bg-slate-700 px-2 py-1 rounded text-slate-300">User: {h.user}</div>
              </div>
              <div className="text-sm text-slate-400 mb-4 flex items-center gap-2"><Clock size={14} /> {new Date(h.timestamp).toLocaleString()}</div>

              <div className="grid grid-cols-4 gap-2 text-center text-sm mb-4">
                <div className="bg-blue-900/50 p-2 rounded border border-blue-900"><div className="font-bold text-blue-400">{h.total_vehicles}</div> Vehicles</div>
                <div className="bg-red-900/50 p-2 rounded border border-red-900"><div className="font-bold text-red-400">{h.total_violations}</div> Violations</div>
                <div className="bg-orange-900/50 p-2 rounded border border-orange-900"><div className="font-bold text-orange-400">{h.overspeed_limit}</div> Limit</div>
                <div className="bg-green-900/50 p-2 rounded border border-green-900"><div className="font-bold text-green-400">{h.distance_meters}m</div> Dist</div>
              </div>

              <div className="flex flex-col gap-2">
                {h.download_name && (
                  <a href={`${API_ENDPOINT}/download/${h.download_name}`} className="flex items-center justify-center gap-2 w-full text-center bg-blue-600 hover:bg-blue-500 py-2 rounded font-bold transition" download>
                    <FileVideo size={16} /> Download Video
                  </a>
                )}
                <div className="flex gap-2">
                  <button onClick={() => convertToCSVAndDownload(h.all_logs, `logs_${h.download_name}.csv`)} className="flex-1 flex items-center justify-center gap-2 bg-slate-700 hover:bg-slate-600 py-2 rounded text-sm transition">
                    <FileText size={14} /> All Logs CSV
                  </button>
                  <button onClick={() => convertToCSVAndDownload(h.overspeed_summary, `violations_${h.download_name}.csv`)} className="flex-1 flex items-center justify-center gap-2 bg-slate-700 hover:bg-slate-600 py-2 rounded text-sm transition">
                    <AlertTriangle size={14} className="text-red-400" /> Violations CSV
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default HistoryPage;
