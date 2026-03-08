import React, { useState, useEffect } from 'react';
import { Eye, Play, Square, Car, AlertTriangle, Activity, Zap, Video } from 'lucide-react';
import { API_ENDPOINT } from '../constants';
import StatBox from '../components/StatBox';
import LogTable from '../components/LogTable';

const LiveMonitorPage = ({ token }) => {
  const [streamUrl, setStreamUrl] = useState(null);
  const [liveStats, setLiveStats] = useState({
    total_vehicles: 0, total_violations: 0, avg_speed: 0, max_speed: 0, all_logs: [], overspeed_summary: []
  });
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

  const handleStart = () => {
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
      <h1 className="text-3xl font-bold text-white flex items-center gap-3"><Eye className="text-blue-400" /> Virtual Simulation</h1>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatBox label="Total Vehicles" value={liveStats.total_vehicles} icon={<Car />} color="blue" />
        <StatBox label="Violations" value={liveStats.total_violations} icon={<AlertTriangle />} color="red" />
        <StatBox label="Avg Speed" value={liveStats.avg_speed} icon={<Activity />} color="green" />
        <StatBox label="Max Speed" value={liveStats.max_speed} icon={<Zap />} color="purple" />
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        <div className="bg-slate-800 p-6 rounded-2xl h-fit border border-slate-700 shadow-xl">
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

          {!isPlaying ? (
            <button
              onClick={handleStart}
              className="w-full bg-green-600 hover:bg-green-500 py-3 rounded-xl font-bold text-white transition shadow-lg flex justify-center items-center"
            >
              <Play size={18} className="mr-2" /> Start Virtual Simulation
            </button>
          ) : (
            <button
              onClick={handleStop}
              className="w-full bg-red-600 hover:bg-red-500 py-3 rounded-xl font-bold text-white transition shadow-lg flex justify-center items-center animate-pulse"
            >
              <Square size={18} className="mr-2 fill-current" /> Stop Simulation
            </button>
          )}

          <div className="mt-4 p-3 bg-blue-900/30 text-blue-200 text-xs rounded border border-blue-900/50">
            This mode generates synthetic traffic data with AI logic: Vehicles spawn in lanes, accelerate, and detection occurs only when crossing start/end lines.
          </div>
        </div>

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
            <div className="text-slate-600 flex flex-col items-center"><Video className="w-16 h-16 mb-4 opacity-50" />Ready to start simulation</div>
          )}
        </div>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        <LogTable title="Virtual Vehicle Logs" data={liveStats.all_logs} icon={<Car className="text-green-400" />} color="slate" showPlate={true} />
        <LogTable title="Virtual Violation Logs" data={liveStats.overspeed_summary} icon={<AlertTriangle className="text-red-400" />} color="red" showPlate={true} />
      </div>
    </div>
  );
};

export default LiveMonitorPage;
