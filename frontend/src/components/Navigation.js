import React from 'react';
import { Activity, Home, Eye, History as HistoryIcon, Info, LogOut, Shield } from 'lucide-react';

const NavBtn = ({ active, onClick, icon, label }) => (
  <button
    onClick={onClick}
    className={`flex items-center gap-2 px-4 py-2 rounded-lg transition ${active ? 'bg-blue-600 text-white' : 'text-slate-300 hover:bg-slate-700'}`}
  >
    {icon} {label}
  </button>
);

const Navigation = ({ currentPage, setCurrentPage, user, onLogout }) => (
  <nav className="bg-slate-800 p-4 text-white flex justify-between items-center sticky top-0 z-50 border-b border-slate-700 shadow-lg">
    <div className="flex items-center gap-2 font-bold text-xl"><Activity className="text-blue-400" /> Traffic AI</div>
    <div className="hidden md:flex gap-2">
      <NavBtn active={currentPage === 'home'} onClick={() => setCurrentPage('home')} icon={<Home size={18} />} label="Processing" />
      <NavBtn active={currentPage === 'monitor'} onClick={() => setCurrentPage('monitor')} icon={<Eye size={18} />} label="Live Simulation" />
      <NavBtn active={currentPage === 'history'} onClick={() => setCurrentPage('history')} icon={<HistoryIcon size={18} />} label="History" />
      {user?.role === 'admin' && <NavBtn active={currentPage === 'admin'} onClick={() => setCurrentPage('admin')} icon={<Shield size={18} />} label="Admin" />}
      <NavBtn active={currentPage === 'about'} onClick={() => setCurrentPage('about')} icon={<Info size={18} />} label="About" />
    </div>
    <button onClick={onLogout} className="bg-red-600 hover:bg-red-500 px-3 py-1.5 rounded text-sm font-medium transition flex items-center gap-2">
      <LogOut size={16} /> Logout
    </button>
  </nav>
);

export default Navigation;
