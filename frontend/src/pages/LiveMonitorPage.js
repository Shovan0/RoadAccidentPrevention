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
  const [config, setConfig] = useState(() => {
    // Load config from localStorage on component mount
    try {
      const saved = localStorage.getItem('simulationConfig');
      return saved ? JSON.parse(saved) : { limit: 60 };
    } catch {
      return { limit: 60 };
    }
  });
  const [isPlaying, setIsPlaying] = useState(false);

  // Save config to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem('simulationConfig', JSON.stringify(config));
  }, [config]);

  // Save stats to localStorage whenever they change
  useEffect(() => {
    if (isPlaying) {
      localStorage.setItem('simulationStats', JSON.stringify(liveStats));
    }
  }, [liveStats, isPlaying]);

  // Restore stats from localStorage on component mount
  useEffect(() => {
    try {
      const saved = localStorage.getItem('simulationStats');
      if (saved) {
        const restoredStats = JSON.parse(saved);
        setLiveStats(restoredStats);
      }
    } catch (err) {
      console.error('Failed to restore simulation stats:', err);
    }
  }, []);

  useEffect(() => {
    if (!streamUrl) return;
    const filename = "virtual_simulation";
    const interval = setInterval(() => {
      fetch(`${API_ENDPOINT}/api/stream-status/${filename}`)
        .then(res => res.json())
        .then(data => {
          setLiveStats(data);
          // Also save to localStorage for persistence
          localStorage.setItem('simulationStats', JSON.stringify(data));
        })
        .catch(err => console.error(err));
    }, 1000);
    return () => clearInterval(interval);
  }, [streamUrl]);

  const handleStart = () => {
    setIsPlaying(true);
    const initialStats = { total_vehicles: 0, total_violations: 0, avg_speed: 0, max_speed: 0, all_logs: [], overspeed_summary: [] };
    setLiveStats(initialStats);
    localStorage.setItem('simulationStats', JSON.stringify(initialStats));
    const url = `${API_ENDPOINT}/video_feed/virtual_simulation?save=false&limit=${config.limit}`;
    setStreamUrl(url);
  };

  const handleStop = async () => {
    setStreamUrl(null);
    setIsPlaying(false);
    
    // Save violations to database
    if (liveStats.overspeed_summary && liveStats.overspeed_summary.length > 0) {
      try {
        const response = await fetch(`${API_ENDPOINT}/api/save-simulation-violations`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ violations: liveStats.overspeed_summary })
        });
        
        if (response.ok) {
          const result = await response.json();
          console.log('✅ Simulation violations saved:', result.message);
        } else {
          console.warn('⚠️ Failed to save simulation violations');
        }
      } catch (err) {
        console.error('Error saving simulation violations:', err);
      }
    }
    
    // Keep stats in localStorage even after stopping
    localStorage.setItem('simulationStats', JSON.stringify(liveStats));
  };

  const handleClear = () => {
    const emptyStats = { total_vehicles: 0, total_violations: 0, avg_speed: 0, max_speed: 0, all_logs: [], overspeed_summary: [] };
    setLiveStats(emptyStats);
    localStorage.removeItem('simulationStats');
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
            {/* Distance input removed — backend uses configured trap-line distance */}
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

          {(liveStats.total_vehicles > 0 || liveStats.total_violations > 0) && (
            <button
              onClick={handleClear}
              className="w-full mt-2 bg-slate-700 hover:bg-slate-600 py-2 rounded-xl font-semibold text-white transition text-sm"
            >
              Clear Data
            </button>
          )}

          <div className="mt-4 p-3 bg-blue-900/30 text-blue-200 text-xs rounded border border-blue-900/50">
            ✅ Simulation state is now saved! Your data persists even after navigating away.
          </div>
        </div>

        <div className="lg:col-span-2 bg-black rounded-2xl overflow-hidden min-h-[400px] flex items-center justify-center border border-slate-700 shadow-2xl relative">
          {streamUrl ? (
            <>
              <iframe
                src={streamUrl}
                title="MJPEG Stream"
                className="w-full h-full border-0"
                frameBorder="0"
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
        <LogTable title="Virtual Violation Logs" data={liveStats.overspeed_summary} icon={<AlertTriangle className="text-red-400" />} color="red" showPlate={true} showDetails={true} />
      </div>

      {/* ── Violator Detail Cards ───────────────────────────────────── */}
      {liveStats.overspeed_summary && liveStats.overspeed_summary.length > 0 && (
        <div className="space-y-3">
          <h2 className="text-xl font-bold text-red-400 flex items-center gap-2">
            <AlertTriangle size={20} /> Violator Details (from Database)
          </h2>
          <div className="grid md:grid-cols-2 xl:grid-cols-3 gap-4">
            {[...liveStats.overspeed_summary].reverse().slice(0, 9).map((v, i) => (
              <div key={i} className="bg-slate-800 border border-red-700/50 rounded-2xl p-4 shadow-lg">
                <div className="flex justify-between items-start mb-3">
                  <span className="font-mono text-white font-bold text-lg tracking-wider bg-yellow-500/20 border border-yellow-500/40 px-3 py-1 rounded">
                    {v.plate}
                  </span>
                  <span className="text-red-400 font-bold text-sm bg-red-900/40 px-2 py-1 rounded">
                    {v.speed} km/h
                  </span>
                </div>
                <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-xs">
                  <div>
                    <p className="text-slate-400 uppercase tracking-wide">Type</p>
                    <p className="text-slate-200 capitalize">{v.label}</p>
                  </div>
                  <div>
                    <p className="text-slate-400 uppercase tracking-wide">Vehicle</p>
                    <p className="text-slate-200">
                      {v.vehicle_make && v.vehicle_model ? `${v.vehicle_make} ${v.vehicle_model}` : <span className="italic text-slate-500">N/A</span>}
                    </p>
                  </div>
                  <div>
                    <p className="text-slate-400 uppercase tracking-wide mt-2">Driver</p>
                    <p className="text-yellow-300 font-semibold">{v.driver_name || <span className="italic text-slate-500">N/A</span>}</p>
                  </div>
                  <div>
                    <p className="text-slate-400 uppercase tracking-wide mt-2">License</p>
                    <p className="text-slate-200 font-mono text-xs">{v.driver_license || <span className="italic text-slate-500">N/A</span>}</p>
                  </div>
                  <div>
                    <p className="text-slate-400 uppercase tracking-wide mt-2">Driver Contact</p>
                    <p className="text-blue-300">{v.driver_contact || <span className="italic text-slate-500">N/A</span>}</p>
                  </div>
                  <div>
                    <p className="text-slate-400 uppercase tracking-wide mt-2">Owner</p>
                    <p className="text-purple-300 font-semibold">{v.owner_name || <span className="italic text-slate-500">N/A</span>}</p>
                  </div>
                  <div className="col-span-2">
                    <p className="text-slate-400 uppercase tracking-wide mt-2">Owner Contact</p>
                    <p className="text-blue-300">{v.owner_contact || <span className="italic text-slate-500">N/A</span>}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default LiveMonitorPage;
