import React, { useState, useEffect } from 'react';
import { Home, Settings, FileVideo, Loader, Play, Car, AlertTriangle, Activity, Zap } from 'lucide-react';
import { API_ENDPOINT } from '../constants';
import LogTable from '../components/LogTable';

const ProcessingPage = ({ token }) => {
  const [file, setFile] = useState(null);
  const [streamUrl, setStreamUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [config, setConfig] = useState({ limit: 60, dist: 20 });
  const [liveStats, setLiveStats] = useState({
    total_vehicles: 0, total_violations: 0, avg_speed: 0, max_speed: 0, all_logs: [], overspeed_summary: []
  });

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
    if (!file) return alert("Select a file");
    setLoading(true);
    setLiveStats({ total_vehicles: 0, total_violations: 0, avg_speed: 0, max_speed: 0, all_logs: [], overspeed_summary: [] });

    const formData = new FormData();
    formData.append('video', file);

    try {
      const res = await fetch(`${API_ENDPOINT}/api/prepare-simulation`, { method: 'POST', body: formData });
      const data = await res.json();

      if (res.ok) {
        const url = `${API_ENDPOINT}/video_feed/${data.filename}?save=true&user=${localStorage.getItem('username')}&limit=${config.limit}&dist=${config.dist}`;
        setStreamUrl(url);
        setIsPlaying(true);
      } else {
        alert("Error: " + data.error);
      }
    } catch (e) { alert("Error uploading file"); }
    setLoading(false);
  };

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-white flex items-center gap-3">
        <Home className="text-blue-400" /> Immediate Processing
      </h1>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-gradient-to-br from-blue-600 to-blue-800 p-4 rounded-xl shadow-xl text-white">
          <div className="flex items-center gap-2 text-blue-200 mb-1 text-sm"><Car size={16} /> Total Vehicles</div>
          <div className="text-3xl font-bold">{liveStats.total_vehicles}</div>
        </div>
        <div className="bg-gradient-to-br from-red-600 to-red-800 p-4 rounded-xl shadow-xl text-white">
          <div className="flex items-center gap-2 text-red-200 mb-1 text-sm"><AlertTriangle size={16} /> Violations</div>
          <div className="text-3xl font-bold">{liveStats.total_violations}</div>
        </div>
        <div className="bg-gradient-to-br from-green-600 to-green-800 p-4 rounded-xl shadow-xl text-white">
          <div className="flex items-center gap-2 text-green-200 mb-1 text-sm"><Activity size={16} /> Avg Speed</div>
          <div className="text-3xl font-bold">{liveStats.avg_speed} <span className="text-sm font-normal">km/h</span></div>
        </div>
        <div className="bg-gradient-to-br from-purple-600 to-purple-800 p-4 rounded-xl shadow-xl text-white">
          <div className="flex items-center gap-2 text-purple-200 mb-1 text-sm"><Zap size={16} /> Max Speed</div>
          <div className="text-3xl font-bold">{liveStats.max_speed} <span className="text-sm font-normal">km/h</span></div>
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        <div className="bg-slate-800 p-6 rounded-2xl h-fit border border-slate-700 shadow-xl">
          <h3 className="text-white font-bold mb-4 flex items-center gap-2"><Settings size={16} /> Configuration</h3>
          <div className="space-y-3 mb-6">
            <div>
              <label className="text-xs text-slate-400">Speed Limit (km/h)</label>
              <input type="number" value={config.limit} onChange={e => setConfig({ ...config, limit: e.target.value })} className="w-full bg-slate-900 border border-slate-600 rounded p-2 text-white text-sm" />
            </div>
            <div>
              <label className="text-xs text-slate-400">Distance (meters)</label>
              <input type="number" value={config.dist} onChange={e => setConfig({ ...config, dist: e.target.value })} className="w-full bg-slate-900 border border-slate-600 rounded p-2 text-white text-sm" />
            </div>
          </div>
          <div className="border-2 border-dashed border-slate-600 rounded-xl p-8 text-center mb-6 hover:bg-slate-700/50 transition cursor-pointer relative">
            <input type="file" accept="video/*" onChange={e => setFile(e.target.files[0])} className="absolute inset-0 opacity-0 cursor-pointer w-full h-full" />
            <FileVideo className="w-12 h-12 text-blue-400 mx-auto mb-2" />
            <div className="text-white font-bold">{file ? file.name : "Select Video"}</div>
          </div>
          <button onClick={handleUploadAndStart} disabled={loading || !file || isPlaying} className="w-full bg-blue-600 py-3 rounded-xl font-bold text-white hover:bg-blue-500 disabled:opacity-50 transition shadow-lg flex justify-center items-center">
            {loading ? <Loader className="animate-spin mx-auto" /> : isPlaying ? <><Loader className="animate-spin mr-2 w-4 h-4" /> Processing...</> : "Start Processing"}
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
            <div className="text-slate-600 text-center"><Play className="w-16 h-16 mx-auto mb-4 opacity-50" /><div>Waiting for video...</div></div>
          )}
        </div>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        <LogTable title="Total Vehicle Logs" data={liveStats.all_logs} icon={<Car className="text-green-400" />} color="slate" />
        <LogTable title="Violation Logs" data={liveStats.overspeed_summary} icon={<AlertTriangle className="text-red-400" />} color="red" />
      </div>
    </div>
  );
};

export default ProcessingPage;
