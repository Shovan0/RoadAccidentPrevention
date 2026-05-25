import React, { useState, useEffect, useCallback } from 'react';
import { History as HistoryIcon, RefreshCw, Clock, FileVideo, FileText, AlertTriangle, ChevronDown, ChevronUp } from 'lucide-react';
import { API_ENDPOINT } from '../constants';
import { convertToCSVAndDownload } from '../utils/csv';

const HistoryPage = ({ token }) => {
  const [history, setHistory] = useState([]);
  const [violations, setViolations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expandedHistory, setExpandedHistory] = useState(null);
  const [activeTab, setActiveTab] = useState('history'); // 'history' or 'violations'

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

  const fetchViolations = useCallback(() => {
    fetch(`${API_ENDPOINT}/api/violations`, { headers: { Authorization: `Bearer ${token}` } })
      .then(r => {
        if (!r.ok) throw new Error("Failed");
        return r.json();
      })
      .then(data => {
        if (Array.isArray(data)) setViolations(data);
        else setViolations([]);
      })
      .catch(() => setViolations([]));
  }, [token]);

  useEffect(() => { 
    fetchHistory();
    fetchViolations();
  }, [fetchHistory, fetchViolations]);

  const handleRefresh = () => {
    fetchHistory();
    fetchViolations();
  };

  // Auto-refresh violations tab every 5 seconds when viewing it
  useEffect(() => {
    if (activeTab === 'violations') {
      const interval = setInterval(fetchViolations, 5000);
      return () => clearInterval(interval);
    }
  }, [activeTab, fetchViolations]);

  const toggleExpanded = (id) => {
    setExpandedHistory(expandedHistory === id ? null : id);
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl text-white font-bold flex items-center gap-2"><HistoryIcon className="text-blue-400" /> History & Violations</h2>
        <button onClick={handleRefresh} className="text-slate-400 hover:text-white p-2 rounded hover:bg-slate-800"><RefreshCw size={18} /></button>
      </div>

      {/* Tab Navigation */}
      <div className="flex gap-2 border-b border-slate-700">
        <button 
          onClick={() => setActiveTab('history')}
          className={`px-4 py-2 font-semibold transition ${activeTab === 'history' ? 'text-blue-400 border-b-2 border-blue-400' : 'text-slate-400 hover:text-white'}`}
        >
          Processing History
        </button>
        <button 
          onClick={() => setActiveTab('violations')}
          className={`px-4 py-2 font-semibold transition flex items-center gap-2 ${activeTab === 'violations' ? 'text-red-400 border-b-2 border-red-400' : 'text-slate-400 hover:text-white'}`}
        >
          <AlertTriangle size={16} /> Violation Logs ({violations.length})
        </button>
      </div>

      {loading && activeTab === 'history' ? (
        <div className="text-center p-10 text-slate-400">Loading history...</div>
      ) : activeTab === 'history' ? (
        history.length === 0 ? (
          <div className="text-center p-10 bg-slate-800 rounded-xl border border-slate-700 text-slate-400">
            <HistoryIcon className="mx-auto w-12 h-12 mb-2 opacity-50" />
            <p>No history records found.</p>
          </div>
        ) : (
          <div className="space-y-3">
            {history.map(h => (
              <div key={h.id} className="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden">
                <div 
                  onClick={() => toggleExpanded(h.id)}
                  className="p-4 cursor-pointer hover:bg-slate-700 transition flex justify-between items-center"
                >
                  <div className="flex-1 min-w-0">
                    <div className="font-bold text-white truncate">{h.original_filename}</div>
                    <div className="text-sm text-slate-400 flex items-center gap-2 mt-1">
                      <Clock size={14} /> {new Date(h.timestamp).toLocaleString()}
                    </div>
                  </div>
                  <div className="flex items-center gap-4 ml-4">
                    <div className="grid grid-cols-3 gap-4 text-right">
                      <div className="text-sm">
                        <div className="text-blue-400 font-bold">{h.total_vehicles}</div>
                        <div className="text-xs text-slate-400">Vehicles</div>
                      </div>
                      <div className="text-sm">
                        <div className="text-red-400 font-bold">{h.total_violations}</div>
                        <div className="text-xs text-slate-400">Violations</div>
                      </div>
                      <div className="text-sm">
                        <div className="text-slate-300 font-bold">{h.overspeed_limit}</div>
                        <div className="text-xs text-slate-400">Limit</div>
                      </div>
                    </div>
                    {expandedHistory === h.id ? <ChevronUp size={20} className="text-slate-400" /> : <ChevronDown size={20} className="text-slate-400" />}
                  </div>
                </div>

                {expandedHistory === h.id && (
                  <div className="border-t border-slate-700 p-4 bg-slate-900/50 space-y-3">
                    <div className="text-sm text-slate-300">
                      <p><span className="text-slate-400">User:</span> {h.user}</p>
                      <p><span className="text-slate-400">Distance:</span> {h.distance_meters}m</p>
                    </div>
                    <div className="flex flex-col gap-2">
                      {h.download_name && (
                        <a href={`${API_ENDPOINT}/download/${h.download_name}`} className="flex items-center justify-center gap-2 w-full text-center bg-blue-600 hover:bg-blue-500 py-2 rounded font-semibold transition text-sm" download>
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
                )}
              </div>
            ))}
          </div>
        )
      ) : (
        <div className="space-y-3">
          {violations.length === 0 ? (
            <div className="text-center p-10 bg-slate-800 rounded-xl border border-slate-700 text-slate-400">
              <AlertTriangle className="mx-auto w-12 h-12 mb-2 opacity-50" />
              <p>No violations recorded.</p>
            </div>
          ) : (
            <div className="overflow-x-auto rounded-xl border border-slate-700">
              <table className="w-full text-sm text-slate-300">
                <thead className="bg-slate-900 border-b border-slate-700">
                  <tr>
                    <th className="px-4 py-3 text-left font-semibold text-white">Plate</th>
                    <th className="px-4 py-3 text-left font-semibold text-white">Vehicle Type</th>
                    <th className="px-4 py-3 text-right font-semibold text-white">Speed (km/h)</th>
                    <th className="px-4 py-3 text-left font-semibold text-white">Driver Name</th>
                    <th className="px-4 py-3 text-left font-semibold text-white">Owner Name</th>
                    <th className="px-4 py-3 text-left font-semibold text-white">Timestamp</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-700">
                  {violations.map((violation, idx) => (
                    <tr key={idx} className="hover:bg-slate-800/50 transition">
                      <td className="px-4 py-3 font-mono text-blue-400">{violation.plate}</td>
                      <td className="px-4 py-3 text-slate-300">{violation.vehicle_type}</td>
                      <td className="px-4 py-3 text-right">
                        <span className="bg-red-900/50 text-red-400 px-3 py-1 rounded-full font-semibold text-xs">
                          {violation.speed} km/h
                        </span>
                      </td>
                      <td className="px-4 py-3 text-slate-300">{violation.driver_name || '-'}</td>
                      <td className="px-4 py-3 text-slate-300">{violation.owner_name || '-'}</td>
                      <td className="px-4 py-3 text-slate-400 text-xs">{new Date(violation.violation_timestamp).toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default HistoryPage;
