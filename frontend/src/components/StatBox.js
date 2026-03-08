import React from 'react';

const StatBox = ({ label, value, icon, color }) => (
  <div className={`bg-slate-800 p-6 rounded-xl border-b-4 border-${color}-500 shadow-xl`}>
    <div className={`text-${color}-400 mb-2`}>{icon}</div>
    <div className="text-3xl font-bold text-white">{value}</div>
    <div className="text-slate-400 text-sm">{label}</div>
  </div>
);

export default StatBox;
