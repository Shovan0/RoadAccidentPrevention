import React from 'react';

const LogTable = ({ title, data, icon, color, showPlate = false }) => (
  <div className={`bg-slate-800 rounded-2xl border border-${color}-700 overflow-hidden`}>
    <div className={`p-4 bg-${color}-900/20 font-bold text-white border-b border-slate-700 flex justify-between items-center`}>
      <span className="flex items-center gap-2">{icon} {title}</span>
      <span className="text-xs bg-slate-700 px-2 py-1 rounded">{data?.length || 0}</span>
    </div>
    <div className="h-64 overflow-y-auto p-2 custom-scrollbar">
      <table className="w-full text-sm text-left text-slate-300">
        <thead className="text-xs text-slate-400 uppercase bg-slate-700/30">
          <tr>
            <th className="px-3 py-2">ID</th>
            {showPlate && <th className="px-3 py-2">Plate</th>}
            <th className="px-3 py-2">Type</th>
            <th className="px-3 py-2">Speed</th>
          </tr>
        </thead>
        <tbody>
          {[...(data || [])].reverse().map((log, i) => (
            <tr key={i} className="border-b border-slate-700/50 hover:bg-slate-700/30">
              <td className="px-3 py-2">{log.id}</td>
              {showPlate && <td className="px-3 py-2 text-white font-mono">{log.plate}</td>}
              <td className="px-3 py-2">{log.label}</td>
              <td className={`px-3 py-2 font-bold ${log.overspeed ? 'text-red-400' : 'text-green-400'}`}>{log.speed} km/h</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  </div>
);

export default LogTable;
