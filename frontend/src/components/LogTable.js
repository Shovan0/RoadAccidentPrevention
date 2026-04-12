import React from 'react';

const LogTable = ({ title, data, icon, color, showPlate = false, showDetails = false }) => (
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
            {showDetails && <th className="px-3 py-2">Driver</th>}
            {showDetails && <th className="px-3 py-2">Contact</th>}
            {showDetails && <th className="px-3 py-2">Owner</th>}
            {showDetails && <th className="px-3 py-2">Vehicle</th>}
          </tr>
        </thead>
        <tbody>
          {[...(data || [])].reverse().map((log, i) => (
            <tr key={i} className="border-b border-slate-700/50 hover:bg-slate-700/30">
              <td className="px-3 py-2">{log.id}</td>
              {showPlate && <td className="px-3 py-2 text-white font-mono">{log.plate}</td>}
              <td className="px-3 py-2">{log.label}</td>
              <td className={`px-3 py-2 font-bold ${log.overspeed ? 'text-red-400' : 'text-green-400'}`}>{log.speed} km/h</td>
              {showDetails && (
                <td className="px-3 py-2 text-yellow-300 font-semibold">
                  {log.driver_name || <span className="text-slate-500 italic">N/A</span>}
                </td>
              )}
              {showDetails && (
                <td className="px-3 py-2 text-blue-300">
                  {log.driver_contact || <span className="text-slate-500 italic">N/A</span>}
                </td>
              )}
              {showDetails && (
                <td className="px-3 py-2 text-purple-300">
                  {log.owner_name || <span className="text-slate-500 italic">N/A</span>}
                </td>
              )}
              {showDetails && (
                <td className="px-3 py-2 text-slate-300">
                  {log.vehicle_make && log.vehicle_model
                    ? `${log.vehicle_make} ${log.vehicle_model}`
                    : <span className="text-slate-500 italic">N/A</span>}
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  </div>
);

export default LogTable;
