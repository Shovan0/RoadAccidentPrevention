import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { 
  Upload, Play, Loader, AlertTriangle, Download, Car, Activity, Zap, 
  FileVideo, TrendingUp, LogOut, User, Home, History as HistoryIcon, 
  Info, Menu, X, Shield, Eye, Trash2, Clock, Settings, Video, RefreshCw, 
  FileText, Square, Lock 
} from 'lucide-react';

const API_ENDPOINT = 'http://127.0.0.1:5000';

// --- UTILS ---
const convertToCSVAndDownload = (data, filename) => {
  if (!data || data.length === 0) return alert("No data to download");
  const header = ['ID', 'Label', 'Speed (km/h)', 'Frame', 'Overspeed'];
  const csvRows = [header.join(',')];
  for (const row of data) {
    const values = [
      row.id,
      row.label,
      typeof row.speed === 'number' ? row.speed.toFixed(2) : row.speed,
      row.frame,
      row.overspeed ? 'Yes' : 'No',
    ];
    csvRows.push(values.join(','));
  }
  const csvString = csvRows.join('\n');
  const blob = new Blob([csvString], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.setAttribute('download', filename);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

// --- POLISHED LOGIN PAGE ---
const LoginPage = ({ onLogin }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      const res = await fetch(`${API_ENDPOINT}/api/login`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({username, password})
      });
      const data = await res.json();
      if(res.ok) {
         localStorage.setItem('token', data.access_token);
         localStorage.setItem('username', data.username);
         localStorage.setItem('role', data.role);
         onLogin(data);
      } else { alert("Login Failed: " + (data.error || "Unknown error")); }
    } catch(err) { alert("Connection Error. Is the backend running?"); }
    setIsLoading(false);
  };

  return (
    <div className="min-h-screen flex items-center justify-center relative bg-slate-900 overflow-hidden">
       {/* Background Decoration */}
       <div className="absolute inset-0 z-0">
          <div className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1492684223066-81342ee5ff30?q=80&w=2070&auto=format&fit=crop')] bg-cover bg-center opacity-20"></div>
          <div className="absolute inset-0 bg-gradient-to-t from-slate-900 via-slate-900/90 to-slate-900/80"></div>
       </div>

       {/* Login Card */}
       <div className="relative z-10 w-full max-w-md p-8 m-4 bg-slate-800/80 backdrop-blur-xl border border-slate-700/50 rounded-3xl shadow-2xl transform transition-all hover:scale-[1.01]">
          <div className="text-center mb-8">
             <div className="mx-auto w-20 h-20 bg-gradient-to-tr from-blue-600 to-cyan-500 rounded-2xl flex items-center justify-center shadow-lg shadow-blue-500/20 mb-6">
               <Shield className="text-white w-10 h-10" />
             </div>
             <h2 className="text-3xl font-bold text-white tracking-tight">Welcome Back</h2>
             <p className="text-slate-400 mt-2 text-sm">Sign in to SpeedGuard AI Monitor</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
             <div className="space-y-4">
                <div className="relative group">
                    <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                        <User className="h-5 w-5 text-slate-500 group-focus-within:text-blue-400 transition-colors" />
                    </div>
                    <input 
                        className="w-full pl-12 pr-4 py-4 bg-slate-900/50 border border-slate-600 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all" 
                        placeholder="Username" 
                        value={username} 
                        onChange={e=>setUsername(e.target.value)} 
                        required
                    />
                </div>
                
                <div className="relative group">
                    <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                        <Lock className="h-5 w-5 text-slate-500 group-focus-within:text-blue-400 transition-colors" />
                    </div>
                    <input 
                        className="w-full pl-12 pr-4 py-4 bg-slate-900/50 border border-slate-600 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all" 
                        type="password" 
                        placeholder="Password" 
                        value={password} 
                        onChange={e=>setPassword(e.target.value)} 
                        required
                    />
                </div>
             </div>

             <button 
                type="submit"
                disabled={isLoading}
                className="w-full bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 text-white font-bold py-4 rounded-xl shadow-lg shadow-blue-500/30 transition-all duration-200 transform hover:-translate-y-0.5 disabled:opacity-70 disabled:cursor-not-allowed flex justify-center items-center gap-2"
             >
                {isLoading ? <Loader className="animate-spin w-5 h-5"/> : "Access Dashboard"}
             </button>
          </form>

          <div className="mt-8 pt-6 border-t border-slate-700/50 text-center">
             <p className="text-xs text-slate-500">Demo Credentials</p>
             <div className="flex justify-center gap-4 mt-2 text-xs font-mono text-slate-400">
                <span className="bg-slate-900/50 px-3 py-1 rounded-full border border-slate-700">admin / admin123</span>
                <span className="bg-slate-900/50 px-3 py-1 rounded-full border border-slate-700">user / user123</span>
             </div>
          </div>
       </div>
    </div>
  );
}

// --- NAVIGATION ---
const Navigation = ({ currentPage, setCurrentPage, user, onLogout }) => (
  <nav className="bg-slate-800 p-4 text-white flex justify-between items-center sticky top-0 z-50 border-b border-slate-700 shadow-lg">
     <div className="flex items-center gap-2 font-bold text-xl"><Activity className="text-blue-400"/> Traffic AI</div>
     <div className="hidden md:flex gap-2">
        <NavBtn active={currentPage==='home'} onClick={()=>setCurrentPage('home')} icon={<Home size={18}/>} label="Processing" />
        <NavBtn active={currentPage==='monitor'} onClick={()=>setCurrentPage('monitor')} icon={<Eye size={18}/>} label="Live Simulation" />
        <NavBtn active={currentPage==='history'} onClick={()=>setCurrentPage('history')} icon={<HistoryIcon size={18}/>} label="History" />
        {user?.role==='admin' && <NavBtn active={currentPage==='admin'} onClick={()=>setCurrentPage('admin')} icon={<Shield size={18}/>} label="Admin" />}
        <NavBtn active={currentPage==='about'} onClick={()=>setCurrentPage('about')} icon={<Info size={18}/>} label="About" />
     </div>
     <button onClick={onLogout} className="bg-red-600 hover:bg-red-500 px-3 py-1.5 rounded text-sm font-medium transition flex items-center gap-2">
       <LogOut size={16}/> Logout
     </button>
  </nav>
);

const NavBtn = ({active, onClick, icon, label}) => (
  <button 
    onClick={onClick} 
    className={`flex items-center gap-2 px-4 py-2 rounded-lg transition ${active ? 'bg-blue-600 text-white' : 'text-slate-300 hover:bg-slate-700'}`}
  >
    {icon} {label}
  </button>
);

// --- HISTORY PAGE ---
const HistoryPage = ({token}) => {
    const [history, setHistory] = useState([]);
    const [loading, setLoading] = useState(true);

    const fetchHistory = useCallback(() => {
        setLoading(true);
        fetch(`${API_ENDPOINT}/api/history`, {headers:{Authorization:`Bearer ${token}`}})
        .then(r => {
            if (!r.ok) throw new Error("Failed");
            return r.json();
        })
        .then(data => {
            if (Array.isArray(data)) setHistory(data);
            else setHistory([]);
        })
        .catch(err => setHistory([]))
        .finally(() => setLoading(false));
    }, [token]);

    useEffect(() => { fetchHistory(); }, [fetchHistory]);
    
    return (
        <div className="space-y-4">
            <div className="flex justify-between items-center">
                <h2 className="text-2xl text-white font-bold flex items-center gap-2"><HistoryIcon className="text-blue-400"/> History</h2>
                <button onClick={fetchHistory} className="text-slate-400 hover:text-white p-2 rounded hover:bg-slate-800"><RefreshCw size={18}/></button>
            </div>
            
            {loading ? <div className="text-center p-10 text-slate-400">Loading history...</div> : 
             history.length === 0 ? (
                <div className="text-center p-10 bg-slate-800 rounded-xl border border-slate-700 text-slate-400">
                    <HistoryIcon className="mx-auto w-12 h-12 mb-2 opacity-50"/>
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
                            <div className="text-sm text-slate-400 mb-4 flex items-center gap-2"><Clock size={14}/> {new Date(h.timestamp).toLocaleString()}</div>
                            
                            <div className="grid grid-cols-4 gap-2 text-center text-sm mb-4">
                                <div className="bg-blue-900/50 p-2 rounded border border-blue-900"><div className="font-bold text-blue-400">{h.total_vehicles}</div> Vehicles</div>
                                <div className="bg-red-900/50 p-2 rounded border border-red-900"><div className="font-bold text-red-400">{h.total_violations}</div> Violations</div>
                                <div className="bg-orange-900/50 p-2 rounded border border-orange-900"><div className="font-bold text-orange-400">{h.overspeed_limit}</div> Limit</div>
                                <div className="bg-green-900/50 p-2 rounded border border-green-900"><div className="font-bold text-green-400">{h.distance_meters}m</div> Dist</div>
                            </div>
                            
                            <div className="flex flex-col gap-2">
                                {h.download_name && (
                                    <a href={`${API_ENDPOINT}/download/${h.download_name}`} className="flex items-center justify-center gap-2 w-full text-center bg-blue-600 hover:bg-blue-500 py-2 rounded font-bold transition" download>
                                        <FileVideo size={16}/> Download Video
                                    </a>
                                )}
                                <div className="flex gap-2">
                                    <button onClick={()=>convertToCSVAndDownload(h.all_logs, `logs_${h.download_name}.csv`)} className="flex-1 flex items-center justify-center gap-2 bg-slate-700 hover:bg-slate-600 py-2 rounded text-sm transition">
                                        <FileText size={14}/> All Logs CSV
                                    </button>
                                    <button onClick={()=>convertToCSVAndDownload(h.overspeed_summary, `violations_${h.download_name}.csv`)} className="flex-1 flex items-center justify-center gap-2 bg-slate-700 hover:bg-slate-600 py-2 rounded text-sm transition">
                                        <AlertTriangle size={14} className="text-red-400"/> Violations CSV
                                    </button>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    )
}

const AdminDashboard = ({token}) => {
  const [stats, setStats] = useState(null);
  useEffect(() => {
    fetch(`${API_ENDPOINT}/api/stats`, { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.json()).then(setStats)
      .catch(() => setStats({total_videos:0, total_vehicles:0, total_violations:0, avg_speed:0}));
  }, [token]);

  if (!stats) return <div className="text-white p-10 text-center">Loading stats...</div>;

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-white flex items-center gap-3"><Shield className="text-blue-400"/> Admin Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatBox label="Total Videos" value={stats.total_videos} icon={<FileVideo/>} color="blue" />
        <StatBox label="Total Vehicles" value={stats.total_vehicles} icon={<Car/>} color="green" />
        <StatBox label="Violations" value={stats.total_violations} icon={<AlertTriangle/>} color="red" />
        <StatBox label="Avg Speed" value={`${stats.avg_speed} km/h`} icon={<Activity/>} color="purple" />
      </div>
    </div>
  );
};

const StatBox = ({label, value, icon, color}) => (
  <div className={`bg-slate-800 p-6 rounded-xl border-b-4 border-${color}-500 shadow-xl`}>
    <div className={`text-${color}-400 mb-2`}>{icon}</div>
    <div className="text-3xl font-bold text-white">{value}</div>
    <div className="text-slate-400 text-sm">{label}</div>
  </div>
);

// --- ABOUT PAGE ---
const AboutPage = () => (
  <div className="space-y-6">
    <div className="bg-slate-800 p-8 rounded-2xl border border-slate-700 shadow-xl">
      <h1 className="text-3xl font-bold mb-4 flex items-center gap-3 text-white">
        <Info className="text-blue-400" size={32} /> 
        About SpeedGuard AI
      </h1>
      <p className="text-slate-300 leading-relaxed text-lg">
        SpeedGuard AI is a cutting-edge Road Accident Prevention System designed to automate traffic monitoring. 
        By leveraging the power of <strong>YOLOv8</strong> (You Only Look Once) for object detection and 
        <strong>ByteTrack</strong> for vehicle tracking, the system provides accurate, real-time speed estimation 
        and violation logging. Our mission is to reduce road accidents through technology-driven enforcement and analytics.
      </p>
    </div>

    <div className="grid md:grid-cols-2 gap-6">
      <div className="bg-slate-800 p-6 rounded-xl border border-slate-700">
        <h3 className="text-xl font-bold text-white mb-3 flex items-center gap-2">
          <Activity className="text-green-400"/> Core Capabilities
        </h3>
        <ul className="space-y-2 text-slate-300 list-disc pl-5">
          <li>Real-time Vehicle Detection & Classification (Car, Bus, Truck, Bike).</li>
          <li>Physics-based Speed Calculation using Virtual Trap Lines.</li>
          <li>Live Simulation Mode with Synthetic Traffic Generation.</li>
          <li>Automated Violation Logging & History Management.</li>
        </ul>
      </div>
      <div className="bg-slate-800 p-6 rounded-xl border border-slate-700">
        <h3 className="text-xl font-bold text-white mb-3 flex items-center gap-2">
          <Shield className="text-purple-400"/> Technical Stack
        </h3>
        <ul className="space-y-2 text-slate-300 list-disc pl-5">
          <li><strong>AI Engine:</strong> YOLOv8 + PyTorch</li>
          <li><strong>Computer Vision:</strong> OpenCV</li>
          <li><strong>Backend:</strong> Python Flask + JWT Auth</li>
          <li><strong>Frontend:</strong> React.js + Tailwind CSS</li>
        </ul>
      </div>
    </div>

    <div className="bg-gradient-to-br from-blue-900/50 to-slate-800 p-8 rounded-2xl border border-blue-800/50 shadow-xl">
      <h2 className="text-2xl font-bold mb-6 text-white flex items-center gap-3">
        <Zap className="text-yellow-400" size={28}/> Future Roadmap & Innovations
      </h2>
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="bg-slate-900/50 p-5 rounded-lg border border-slate-700 hover:border-blue-500/50 transition">
          <h4 className="font-bold text-blue-300 mb-2">OCR Integration</h4>
          <p className="text-sm text-slate-400">Implementing real-time Optical Character Recognition to extract actual number plates from live CCTV footage.</p>
        </div>
        <div className="bg-slate-900/50 p-5 rounded-lg border border-slate-700 hover:border-blue-500/50 transition">
          <h4 className="font-bold text-blue-300 mb-2">SMS & Call Alerts</h4>
          <p className="text-sm text-slate-400">Integration with Twilio API to send instant SMS warnings or automated calls to vehicle owners upon violation.</p>
        </div>
        <div className="bg-slate-900/50 p-5 rounded-lg border border-slate-700 hover:border-blue-500/50 transition">
          <h4 className="font-bold text-blue-300 mb-2">RTO Database Sync</h4>
          <p className="text-sm text-slate-400">Connecting with the Regional Transport Office (RTO) API to fetch owner details and issue e-Challans automatically.</p>
        </div>
        <div className="bg-slate-900/50 p-5 rounded-lg border border-slate-700 hover:border-blue-500/50 transition">
          <h4 className="font-bold text-blue-300 mb-2">Accident Detection</h4>
          <p className="text-sm text-slate-400">Using anomaly detection algorithms to identify crashes or stalled vehicles and alert emergency services.</p>
        </div>
        <div className="bg-slate-900/50 p-5 rounded-lg border border-slate-700 hover:border-blue-500/50 transition">
          <h4 className="font-bold text-blue-300 mb-2">Smart Signal Control</h4>
          <p className="text-sm text-slate-400">Analyzing traffic density in real-time to optimize traffic light durations and reduce congestion.</p>
        </div>
      </div>
    </div>
    
    <div className="text-center text-slate-500 text-sm mt-8">
      © 2026 Road Accident Prevention System. All Rights Reserved.
    </div>
  </div>
);

// --- HELPER COMPONENT: Log Table ---
const LogTable = ({title, data, icon, color, showPlate = false}) => (
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
                           <td className={`px-3 py-2 font-bold ${log.overspeed?'text-red-400':'text-green-400'}`}>{log.speed} km/h</td>
                       </tr>
                   ))}
               </tbody>
           </table>
       </div>
   </div>
);

// =========================================================
//  PROCESSING PAGE (Batch) - LIVE LOGS
// =========================================================
const ProcessingPage = ({ token }) => {
  const [file, setFile] = useState(null);
  const [streamUrl, setStreamUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false); 
  const [config, setConfig] = useState({ limit: 60, dist: 20 });
  const [liveStats, setLiveStats] = useState({ total_vehicles: 0, total_violations: 0, avg_speed: 0, max_speed: 0, all_logs: [], overspeed_summary: [] });
  
  useEffect(() => {
     if (!streamUrl) return;
     const match = streamUrl.match(/\/video_feed\/([^\?]+)/);
     if (!match) return;
     const filename = match[1];

     const interval = setInterval(() => {
        fetch(`${API_ENDPOINT}/api/stream-status/${filename}`)
           .then(res => res.json())
           .then(data => setLiveStats(data))
           .catch(err => console.error("Stats poll error", err));
     }, 1000); 

     return () => clearInterval(interval);
  }, [streamUrl]);

  const handleUploadAndStart = async () => {
     if(!file) return alert("Select a file");
     setLoading(true);
     setLiveStats({ total_vehicles: 0, total_violations: 0, avg_speed: 0, max_speed: 0, all_logs: [], overspeed_summary: [] }); 
     
     const formData = new FormData();
     formData.append('video', file);
     
     try {
        const res = await fetch(`${API_ENDPOINT}/api/prepare-simulation`, { method: 'POST', body: formData });
        const data = await res.json();
        
        if(res.ok) {
            const url = `${API_ENDPOINT}/video_feed/${data.filename}?save=true&user=${localStorage.getItem('username')}&limit=${config.limit}&dist=${config.dist}`;
            setStreamUrl(url);
            setIsPlaying(true); 
        } else {
            alert("Error: " + data.error);
        }
     } catch(e) { alert("Error uploading file"); }
     setLoading(false);
  };

  return (
    <div className="space-y-6">
       <h1 className="text-3xl font-bold text-white flex items-center gap-3">
          <Home className="text-blue-400"/> Immediate Processing
       </h1>
       
       <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-gradient-to-br from-blue-600 to-blue-800 p-4 rounded-xl shadow-xl text-white">
             <div className="flex items-center gap-2 text-blue-200 mb-1 text-sm"><Car size={16}/> Total Vehicles</div>
             <div className="text-3xl font-bold">{liveStats.total_vehicles}</div>
          </div>
          <div className="bg-gradient-to-br from-red-600 to-red-800 p-4 rounded-xl shadow-xl text-white">
             <div className="flex items-center gap-2 text-red-200 mb-1 text-sm"><AlertTriangle size={16}/> Violations</div>
             <div className="text-3xl font-bold">{liveStats.total_violations}</div>
          </div>
          <div className="bg-gradient-to-br from-green-600 to-green-800 p-4 rounded-xl shadow-xl text-white">
             <div className="flex items-center gap-2 text-green-200 mb-1 text-sm"><Activity size={16}/> Avg Speed</div>
             <div className="text-3xl font-bold">{liveStats.avg_speed} <span className="text-sm font-normal">km/h</span></div>
          </div>
          <div className="bg-gradient-to-br from-purple-600 to-purple-800 p-4 rounded-xl shadow-xl text-white">
             <div className="flex items-center gap-2 text-purple-200 mb-1 text-sm"><Zap size={16}/> Max Speed</div>
             <div className="text-3xl font-bold">{liveStats.max_speed} <span className="text-sm font-normal">km/h</span></div>
          </div>
       </div>

       <div className="grid lg:grid-cols-3 gap-6">
          <div className="bg-slate-800 p-6 rounded-2xl h-fit border border-slate-700 shadow-xl">
             <h3 className="text-white font-bold mb-4 flex items-center gap-2"><Settings size={16}/> Configuration</h3>
             <div className="space-y-3 mb-6">
                <div>
                   <label className="text-xs text-slate-400">Speed Limit (km/h)</label>
                   <input type="number" value={config.limit} onChange={e=>setConfig({...config, limit:e.target.value})} className="w-full bg-slate-900 border border-slate-600 rounded p-2 text-white text-sm"/>
                </div>
                <div>
                   <label className="text-xs text-slate-400">Distance (meters)</label>
                   <input type="number" value={config.dist} onChange={e=>setConfig({...config, dist:e.target.value})} className="w-full bg-slate-900 border border-slate-600 rounded p-2 text-white text-sm"/>
                </div>
             </div>
             <div className="border-2 border-dashed border-slate-600 rounded-xl p-8 text-center mb-6 hover:bg-slate-700/50 transition cursor-pointer relative">
                <input type="file" accept="video/*" onChange={e=>setFile(e.target.files[0])} className="absolute inset-0 opacity-0 cursor-pointer w-full h-full"/>
                <FileVideo className="w-12 h-12 text-blue-400 mx-auto mb-2"/>
                <div className="text-white font-bold">{file ? file.name : "Select Video"}</div>
             </div>
             <button onClick={handleUploadAndStart} disabled={loading||!file||isPlaying} className="w-full bg-blue-600 py-3 rounded-xl font-bold text-white hover:bg-blue-500 disabled:opacity-50 transition shadow-lg flex justify-center items-center">
                {loading ? <Loader className="animate-spin mx-auto"/> : isPlaying ? <><Loader className="animate-spin mr-2 w-4 h-4"/> Processing...</> : "Start Processing"}
             </button>
          </div>
          <div className="lg:col-span-2 bg-black rounded-2xl overflow-hidden min-h-[400px] flex items-center justify-center relative border border-slate-700 shadow-2xl">
             {streamUrl ? (
                <>
                   <img src={streamUrl} alt="Stream" className="w-full h-full object-contain" onError={() => setIsPlaying(false)} />
                   {isPlaying && <div className="absolute top-4 left-4 bg-red-600 px-3 py-1 rounded-full text-xs font-bold text-white animate-pulse flex items-center gap-2 shadow-lg"><div className="w-2 h-2 bg-white rounded-full"></div> REC</div>}
                   <div className="absolute bottom-4 left-0 w-full text-center"><span className="bg-black/70 text-white px-4 py-1 rounded-full text-sm backdrop-blur-sm border border-white/10">{isPlaying ? "Results are being saved to History..." : "Processing Complete."}</span></div>
                </>
             ) : (
                <div className="text-slate-600 text-center"><Play className="w-16 h-16 mx-auto mb-4 opacity-50"/><div>Waiting for video...</div></div>
             )}
          </div>
       </div>

       {/* LOG TABLES */}
       <div className="grid lg:grid-cols-2 gap-6">
           <LogTable title="Total Vehicle Logs" data={liveStats.all_logs} icon={<Car className="text-green-400"/>} color="slate" />
           <LogTable title="Violation Logs" data={liveStats.overspeed_summary} icon={<AlertTriangle className="text-red-400"/>} color="red" />
       </div>
    </div>
  );
};

// =========================================================
//  UPDATED: LiveMonitorPage (Virtual Simulation)
// =========================================================
const LiveMonitorPage = ({ token }) => {
  const [streamUrl, setStreamUrl] = useState(null);
  const [liveStats, setLiveStats] = useState({ total_vehicles: 0, total_violations: 0, avg_speed: 0, max_speed: 0, all_logs: [], overspeed_summary: [] });
  const [config, setConfig] = useState({ limit: 60, dist: 20 });
  const [isPlaying, setIsPlaying] = useState(false);

  useEffect(() => {
     if (!streamUrl) return;
     const filename = "virtual_simulation";
     const interval = setInterval(() => {
        fetch(`${API_ENDPOINT}/api/stream-status/${filename}`)
           .then(res => res.json())
           .then(data => setLiveStats(data))
           .catch(err => console.error(err));
     }, 1000);
     return () => clearInterval(interval);
  }, [streamUrl]);
  
  const handleStart = async () => {
      setIsPlaying(true);
      setLiveStats({ total_vehicles: 0, total_violations: 0, avg_speed: 0, max_speed: 0, all_logs: [], overspeed_summary: [] });
      const url = `${API_ENDPOINT}/video_feed/virtual_simulation?save=false&limit=${config.limit}&dist=${config.dist}`;
      setStreamUrl(url);
  };

  const handleStop = () => {
      setStreamUrl(null);
      setIsPlaying(false);
  };

  return (
    <div className="space-y-6">
        <h1 className="text-3xl font-bold text-white flex items-center gap-3"><Eye className="text-blue-400"/> Virtual Simulation</h1>
        
        {/* STATS */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatBox label="Total Vehicles" value={liveStats.total_vehicles} icon={<Car/>} color="blue" />
          <StatBox label="Violations" value={liveStats.total_violations} icon={<AlertTriangle/>} color="red" />
          <StatBox label="Avg Speed" value={liveStats.avg_speed} icon={<Activity/>} color="green" />
          <StatBox label="Max Speed" value={liveStats.max_speed} icon={<Zap/>} color="purple" />
       </div>

        <div className="grid lg:grid-cols-3 gap-6">
            <div className="bg-slate-800 p-6 rounded-2xl h-fit border border-slate-700 shadow-xl">
                <div className="space-y-3 mb-6">
                    <div>
                        <label className="text-xs text-slate-400">Speed Limit (km/h)</label>
                        <input type="number" value={config.limit} onChange={e=>setConfig({...config, limit:e.target.value})} className="w-full bg-slate-900 border border-slate-600 rounded p-2 text-white text-sm"/>
                    </div>
                    <div>
                        <label className="text-xs text-slate-400">Distance (meters)</label>
                        <input type="number" value={config.dist} onChange={e=>setConfig({...config, dist:e.target.value})} className="w-full bg-slate-900 border border-slate-600 rounded p-2 text-white text-sm"/>
                    </div>
                </div>
                {/* START / STOP BUTTONS */}
                {!isPlaying ? (
                    <button 
                        onClick={handleStart} 
                        className="w-full bg-green-600 hover:bg-green-500 py-3 rounded-xl font-bold text-white transition shadow-lg flex justify-center items-center"
                    >
                        <Play size={18} className="mr-2"/> Start Virtual Simulation
                    </button>
                ) : (
                    <button 
                        onClick={handleStop} 
                        className="w-full bg-red-600 hover:bg-red-500 py-3 rounded-xl font-bold text-white transition shadow-lg flex justify-center items-center animate-pulse"
                    >
                        <Square size={18} className="mr-2 fill-current"/> Stop Simulation
                    </button>
                )}
                
                <div className="mt-4 p-3 bg-blue-900/30 text-blue-200 text-xs rounded border border-blue-900/50">
                   This mode generates synthetic traffic data with AI logic: Vehicles spawn in lanes, accelerate, and detection occurs only when crossing start/end lines.
                </div>
            </div>
            
            {/* VIDEO DISPLAY */}
            <div className="lg:col-span-2 bg-black rounded-2xl overflow-hidden min-h-[400px] flex items-center justify-center border border-slate-700 shadow-2xl relative">
                {streamUrl ? (
                    <>
                        <img 
                            src={streamUrl} 
                            alt="Stream" 
                            className="w-full h-full object-contain"
                            onError={() => setIsPlaying(false)}
                        />
                        <div className="absolute top-4 left-4 bg-purple-600 px-3 py-1 rounded-full text-xs font-bold text-white shadow-lg flex items-center gap-2">
                            <div className="w-2 h-2 bg-white rounded-full animate-ping"></div> VIRTUAL LIVE
                        </div>
                    </>
                ) : (
                    <div className="text-slate-600 flex flex-col items-center"><Video className="w-16 h-16 mb-4 opacity-50"/>Ready to start simulation</div>
                )}
            </div>
        </div>

        {/* LOG TABLES (Added for Simulation too, WITH PLATES) */}
        <div className="grid lg:grid-cols-2 gap-6">
           <LogTable title="Virtual Vehicle Logs" data={liveStats.all_logs} icon={<Car className="text-green-400"/>} color="slate" showPlate={true} />
           <LogTable title="Virtual Violation Logs" data={liveStats.overspeed_summary} icon={<AlertTriangle className="text-red-400"/>} color="red" showPlate={true} />
        </div>
    </div>
  );
};

// --- MAIN APP ---
const App = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [currentPage, setCurrentPage] = useState('home');

  useEffect(() => {
     const token = localStorage.getItem('token');
     const u = localStorage.getItem('username');
     if(token && u) { setUser({username:u, role:localStorage.getItem('role')}); setIsAuthenticated(true); }
  }, []);

  if (!isAuthenticated) return <LoginPage onLogin={(u)=>{setUser({username:u.username, role:u.role}); setIsAuthenticated(true);}} />;

  return (
    <div className="min-h-screen bg-slate-900 text-white font-sans">
      <Navigation currentPage={currentPage} setCurrentPage={setCurrentPage} user={user} onLogout={()=>{setIsAuthenticated(false); localStorage.clear();}} />
      <div className="max-w-7xl mx-auto p-4 sm:p-8">
        {currentPage === 'home' && <ProcessingPage token={localStorage.getItem('token')} />}
        {currentPage === 'monitor' && <LiveMonitorPage token={localStorage.getItem('token')} />}
        {currentPage === 'history' && <HistoryPage key={user?.username} token={localStorage.getItem('token')} />}
        {currentPage === 'admin' && <AdminDashboard token={localStorage.getItem('token')} />}
        {currentPage === 'about' && <AboutPage />}
      </div>
    </div>
  );
};

export default App;