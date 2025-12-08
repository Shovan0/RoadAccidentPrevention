import React, { useState, useCallback, useMemo, useEffect } from 'react';
import {
  Upload,
  Play,
  Loader,
  AlertTriangle,
  CheckCircle,
  Clock,
  Download,
  TrendingUp,
  Car,
  Activity,
  Zap,
  FileVideo,
  BarChart3
} from 'lucide-react';

const API_ENDPOINT = "http://127.0.0.1:5000/upload-and-process";

const convertToCSVAndDownload = (data, filename) => {
  if (!data || data.length === 0) return;
  const header = ["ID", "Label", "Speed (km/h)", "Frame", "Overspeed"];
  const csvRows = [header.join(',')];

  for (const row of data) {
    // escape commas in label if present
    const safeLabel = typeof row.label === 'string' ? `"${row.label.replace(/"/g, '""')}"` : row.label;
    const values = [
      row.id,
      safeLabel,
      typeof row.speed === "number" ? row.speed.toFixed(2) : row.speed,
      row.frame,
      row.overspeed ? 'Yes' : 'No'
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

const App = () => {
  const [file, setFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [logs, setLogs] = useState([]);
  const [statusMessage, setStatusMessage] = useState("Ready to process traffic video");
  const [downloadLink, setDownloadLink] = useState(null);

  useEffect(() => {
    // cleanup preview URL when component unmounts or file changes
    return () => {
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }
    };
  }, [previewUrl]);

  const overspeedRecords = useMemo(() => logs.filter(log => log.overspeed), [logs]);
  const compliantVehicles = useMemo(() => logs.filter(log => !log.overspeed), [logs]);
  const avgSpeed = useMemo(() => {
    if (logs.length === 0) return 0;
    const total = logs.reduce((sum, log) => sum + (Number(log.speed) || 0), 0);
    return (total / logs.length).toFixed(1);
  }, [logs]);
  const maxSpeed = useMemo(() => {
    if (logs.length === 0) return 0;
    return Math.max(...logs.map(log => Number(log.speed) || 0)).toFixed(1);
  }, [logs]);

  const handleFileChange = (event) => {
    const selectedFile = event.target.files?.[0];
    if (selectedFile) {
      if (previewUrl) URL.revokeObjectURL(previewUrl);
      setFile(selectedFile);
      setPreviewUrl(URL.createObjectURL(selectedFile));
      setProgress(0);
      setLogs([]);
      setIsProcessing(false);
      setDownloadLink(null);
      setStatusMessage(`Video loaded: ${selectedFile.name}`);
    }
  };

  const handleProcessing = useCallback(async () => {
    if (!file) {
      setStatusMessage("Please upload a video file first.");
      return;
    }

    setIsProcessing(true);
    setLogs([]);
    setProgress(5);
    setDownloadLink(null);
    setStatusMessage("Processing video with AI detection...");

    const formData = new FormData();
    formData.append('video', file);

    try {
      const response = await fetch(API_ENDPOINT, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(errorData?.error || `Server responded with status ${response.status}`);
      }

      const result = await response.json();

      // defensive extraction: different servers may return logs under different keys
      const rawLogs =
        result.all_logs
        ?? result.logs
        ?? result.data
        ?? result.vehicles
        ?? [];

      const globalSpeedLimit = result.speed_limit ?? result.limit ?? null;

      const normalized = Array.isArray(rawLogs) ? rawLogs.map((l, i) => {
        // normalize id & label
        const id = l.id ?? l.vehicle_id ?? l.v_id ?? l.track_id ?? `v${i + 1}`;
        const label = l.label ?? l.type ?? l.class ?? l.name ?? 'Vehicle';

        // normalize speed (strip strings, parse floats)
        let speed = l.speed ?? l.spd ?? l.speed_kmh ?? l.v_speed ?? null;
        if (typeof speed === 'string') {
          const parsed = parseFloat(speed.replace(/[^\d.\-]/g, ''));
          speed = Number.isFinite(parsed) ? parsed : null;
        }
        if (speed === null || Number.isNaN(Number(speed))) {
          speed = 0;
        } else {
          speed = Number(speed);
        }

        // normalize frame
        const frame = l.frame ?? l.frame_no ?? l.frameNumber ?? l.frame_index ?? 0;

        // normalize overspeed flag (boolean/string/int) or infer from limit
        const overspeedFlag = (l.overspeed ?? l.over_speed ?? l.is_overspeed ?? l.violation ?? l.is_violation ?? l.over_speeding);
        let overspeed = false;
        if (typeof overspeedFlag === 'boolean') {
          overspeed = overspeedFlag;
        } else if (typeof overspeedFlag === 'number') {
          overspeed = overspeedFlag === 1;
        } else if (typeof overspeedFlag === 'string') {
          overspeed = ['true', '1', 'yes', 'y'].includes(overspeedFlag.toLowerCase());
        } else {
          const recLimit = l.limit ?? l.speed_limit ?? globalSpeedLimit;
          if (recLimit !== undefined && recLimit !== null && !Number.isNaN(Number(recLimit))) {
            overspeed = speed > Number(recLimit);
          } else {
            overspeed = false;
          }
        }

        return {
          id,
          label,
          speed,
          frame,
          overspeed
        };
      }) : [];

      setProgress(100);
      setStatusMessage("✅ Processing complete! Analysis ready.");
      setLogs(normalized);

      const serverOrigin = new URL(API_ENDPOINT).origin;
      const outputUrl = result.output_video_url ?? result.output_url ?? result.video_url ?? null;
      const fullDownloadUrl = outputUrl ? (outputUrl.startsWith('http') ? outputUrl : serverOrigin + outputUrl) : null;
      setDownloadLink(fullDownloadUrl || null);
    } catch (error) {
      console.error("Processing failed:", error);
      setStatusMessage(`❌ Error: ${error.message}`);
      setProgress(0);
    } finally {
      setIsProcessing(false);
    }
  }, [file]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 p-4 sm:p-8">
      {/* Header Section */}
      <header className="text-center mb-8 relative">
        <div className="absolute inset-0 bg-blue-500 opacity-10 blur-3xl"></div>
        <div className="relative">
          <div className="flex items-center justify-center mb-4">
            <div className="bg-gradient-to-r from-blue-500 to-cyan-500 p-3 rounded-2xl shadow-lg">
              <Activity className="w-10 h-10 text-white" />
            </div>
          </div>
          <h1 className="text-4xl sm:text-5xl font-black text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-cyan-400 to-blue-500 tracking-tight mb-3">
            AI Traffic Speed Detection
          </h1>
          <p className="text-blue-300 text-lg font-medium">Powered by YOLOv8 Neural Network</p>
          <div className="flex items-center justify-center gap-4 mt-4 text-sm text-blue-400">
            <span className="flex items-center gap-1"><Zap className="w-4 h-4" /> Real-time Analysis</span>
            <span className="flex items-center gap-1"><Car className="w-4 h-4" /> Multi-vehicle Tracking</span>
            <span className="flex items-center gap-1"><BarChart3 className="w-4 h-4" /> Statistical Insights</span>
          </div>
        </div>
      </header>

      {/* Statistics Cards */}
      {logs.length > 0 && (
        <div className="max-w-7xl mx-auto grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl p-5 shadow-xl">
            <div className="flex items-center justify-between mb-2">
              <Car className="w-8 h-8 text-white opacity-80" />
              <span className="text-3xl font-bold text-white">{logs.length}</span>
            </div>
            <p className="text-blue-100 text-sm font-medium">Total Vehicles</p>
          </div>

          <div className="bg-gradient-to-br from-red-500 to-red-600 rounded-2xl p-5 shadow-xl">
            <div className="flex items-center justify-between mb-2">
              <AlertTriangle className="w-8 h-8 text-white opacity-80" />
              <span className="text-3xl font-bold text-white">{overspeedRecords.length}</span>
            </div>
            <p className="text-red-100 text-sm font-medium">Violations</p>
          </div>

          <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-2xl p-5 shadow-xl">
            <div className="flex items-center justify-between mb-2">
              <TrendingUp className="w-8 h-8 text-white opacity-80" />
              <span className="text-3xl font-bold text-white">{avgSpeed}</span>
            </div>
            <p className="text-green-100 text-sm font-medium">Avg Speed (km/h)</p>
          </div>

          <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-2xl p-5 shadow-xl">
            <div className="flex items-center justify-between mb-2">
              <Zap className="w-8 h-8 text-white opacity-80" />
              <span className="text-3xl font-bold text-white">{maxSpeed}</span>
            </div>
            <p className="text-purple-100 text-sm font-medium">Max Speed (km/h)</p>
          </div>
        </div>
      )}

      <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Controls & Preview */}
        <div className="lg:col-span-2 space-y-6">
          {/* Control Panel */}
          <div className="bg-slate-800/50 backdrop-blur-xl p-6 rounded-3xl shadow-2xl border border-slate-700/50">
            <h2 className="text-2xl font-bold mb-6 text-white flex items-center">
              <div className="bg-blue-500/20 p-2 rounded-xl mr-3">
                <Clock className="w-6 h-6 text-blue-400" />
              </div>
              Processing Controls
            </h2>

            <label className="block mb-6 group cursor-pointer">
              <div className="relative border-2 border-dashed border-slate-600 hover:border-blue-500 rounded-2xl p-8 transition-all duration-300 bg-slate-900/30 hover:bg-slate-900/50">
                <input
                  type="file"
                  accept="video/mp4,video/avi,video/mov,video/mkv"
                  onChange={handleFileChange}
                  disabled={isProcessing}
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                />
                <div className="flex flex-col items-center">
                  <div className="bg-blue-500/20 p-4 rounded-full mb-3 group-hover:scale-110 transition-transform">
                    <FileVideo className="w-8 h-8 text-blue-400" />
                  </div>
                  <p className="text-white font-semibold mb-1">
                    {file ? file.name : "Click to upload video"}
                  </p>
                  <p className="text-slate-400 text-sm">Supports MP4, AVI, MOV, MKV formats</p>
                </div>
              </div>
            </label>

            <div className="mb-6">
              <div className="flex items-center justify-between mb-2">
                <p className={`text-sm font-medium ${isProcessing ? 'text-blue-400' : 'text-slate-300'}`}>
                  {statusMessage}
                </p>
                <span className="text-sm font-bold text-blue-400">{progress}%</span>
              </div>
              <div className="w-full bg-slate-700 rounded-full h-3 overflow-hidden shadow-inner">
                <div
                  className={`h-3 rounded-full transition-all duration-300 ${
                    progress === 100
                      ? 'bg-gradient-to-r from-green-500 to-emerald-500'
                      : isProcessing
                        ? 'bg-gradient-to-r from-blue-500 to-cyan-500 animate-pulse'
                        : 'bg-slate-600'
                  }`}
                  style={{ width: `${progress}%` }}
                ></div>
              </div>
            </div>

            <div className="flex gap-3">
              <button
                onClick={handleProcessing}
                disabled={!file || isProcessing}
                className={`flex-1 flex justify-center items-center px-6 py-4 rounded-2xl font-bold text-white shadow-lg transition-all duration-300 transform hover:scale-[1.02] ${
                  !file || isProcessing
                    ? 'bg-slate-700 cursor-not-allowed opacity-50'
                    : 'bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 shadow-blue-500/50'
                }`}
              >
                {isProcessing ? (
                  <>
                    <Loader className="w-5 h-5 mr-2 animate-spin" />
                    Processing...
                  </>
                ) : (
                  <>
                    <Play className="w-5 h-5 mr-2" />
                    Start Analysis
                  </>
                )}
              </button>

              {downloadLink && (
                <a
                  href={downloadLink}
                  download
                  className="flex items-center justify-center px-6 py-4 rounded-2xl font-bold text-white bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-500 hover:to-emerald-500 shadow-lg shadow-green-500/50 transition-all duration-300 transform hover:scale-[1.02]"
                >
                  <Download className="w-5 h-5 mr-2" />
                  Download
                </a>
              )}
            </div>
          </div>

          {/* Video Preview */}
          <div className="bg-slate-800/50 backdrop-blur-xl p-6 rounded-3xl shadow-2xl border border-slate-700/50">
            <h2 className="text-2xl font-bold mb-4 text-white flex items-center">
              <div className="bg-purple-500/20 p-2 rounded-xl mr-3">
                <FileVideo className="w-6 h-6 text-purple-400" />
              </div>
              Video Preview
            </h2>
            <div className="aspect-video bg-slate-900 rounded-2xl overflow-hidden shadow-inner border border-slate-700">
              {previewUrl ? (
                <video controls src={previewUrl} className="w-full h-full object-cover"></video>
              ) : (
                <div className="flex flex-col items-center justify-center w-full h-full text-slate-500">
                  <Upload className="w-16 h-16 mb-4 opacity-50" />
                  <p className="text-lg font-medium">Upload a video to preview</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Right Column - Logs & Violations */}
        <div className="lg:col-span-1 space-y-6">
          {/* All Vehicle Logs */}
          <div className="bg-slate-800/50 backdrop-blur-xl p-6 rounded-3xl shadow-2xl border border-slate-700/50">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-white flex items-center">
                <div className="bg-green-500/20 p-2 rounded-xl mr-2">
                  <Activity className="w-5 h-5 text-green-400" />
                </div>
                Vehicle Logs
              </h2>
              <button
                onClick={() => convertToCSVAndDownload(logs, 'all_vehicle_logs.csv')}
                disabled={logs.length === 0}
                className="text-xs text-blue-400 hover:text-blue-300 disabled:opacity-30 flex items-center transition-colors font-medium"
              >
                <Download className="w-3 h-3 mr-1" /> CSV
              </button>
            </div>

            <div className="h-72 overflow-y-auto bg-slate-900/50 rounded-xl p-3 text-xs font-mono border border-slate-700 custom-scrollbar">
              {logs.length === 0 ? (
                <p className="text-slate-500 text-center py-8">Awaiting analysis...</p>
              ) : (
                logs.map((log, index) => (
                  <div key={log.id ?? index} className={`py-2 px-3 mb-2 rounded-lg flex items-start ${
                    log.overspeed
                      ? 'bg-red-500/10 border border-red-500/30'
                      : 'bg-green-500/10 border border-green-500/30'
                  }`}>
                    {log.overspeed ? (
                      <AlertTriangle className="w-4 h-4 text-red-400 mr-2 flex-shrink-0 mt-0.5" />
                    ) : (
                      <CheckCircle className="w-4 h-4 text-green-400 mr-2 flex-shrink-0 mt-0.5" />
                    )}
                    <div className="flex-1">
                      <div className={`font-bold ${log.overspeed ? 'text-red-400' : 'text-green-400'}`}>
                        ID:{log.id ?? 'N/A'} • {log.label ?? 'Vehicle'}
                      </div>
                      <div className="text-slate-400 text-[10px]">
                        {typeof log.speed === "number" ? log.speed.toFixed(2) : (log.speed ?? 0)} km/h • Frame {log.frame ?? 0}
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Overspeed Violations */}
          <div className="bg-gradient-to-br from-red-900/30 to-orange-900/30 backdrop-blur-xl p-6 rounded-3xl shadow-2xl border-2 border-red-500/30">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-white flex items-center">
                <div className="bg-red-500/30 p-2 rounded-xl mr-2">
                  <AlertTriangle className="w-5 h-5 text-red-400" />
                </div>
                Violations ({overspeedRecords.length})
              </h2>
              <button
                onClick={() => convertToCSVAndDownload(overspeedRecords, 'overspeed_violations.csv')}
                disabled={overspeedRecords.length === 0}
                className="text-xs text-red-400 hover:text-red-300 disabled:opacity-30 flex items-center transition-colors font-medium"
              >
                <Download className="w-3 h-3 mr-1" /> CSV
              </button>
            </div>

            <div className="h-72 overflow-y-auto custom-scrollbar">
              {overspeedRecords.length === 0 ? (
                <div className="text-center py-12">
                  <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-3 opacity-50" />
                  <p className="text-slate-400 font-medium">No violations detected</p>
                  <p className="text-slate-500 text-xs mt-1">All vehicles within speed limit</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {overspeedRecords.map((record, idx) => (
                    <div key={record.id ?? idx} className="p-4 bg-red-500/10 border-2 border-red-500/30 rounded-xl shadow-lg backdrop-blur-sm hover:bg-red-500/20 transition-all">
                      <div className="flex justify-between items-start mb-2">
                        <div>
                          <p className="font-bold text-red-400 text-sm">{record.label}</p>
                          <p className="text-xs text-slate-400">ID: {record.id}</p>
                        </div>
                        <div className="text-right">
                          <p className="text-2xl font-black text-red-400">
                            {typeof record.speed === "number" ? record.speed.toFixed(1) : record.speed}
                          </p>
                          <p className="text-xs text-slate-400">km/h</p>
                        </div>
                      </div>
                      <div className="flex items-center justify-between text-xs text-slate-500 pt-2 border-t border-red-500/20">
                        <span>Frame: {record.frame}</span>
                        <span className="text-red-400 font-semibold">⚠ VIOLATION</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      <style>{`
        .custom-scrollbar::-webkit-scrollbar {
            width: 6px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
            background: rgba(15, 23, 42, 0.5);
            border-radius: 10px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
            background: rgba(59, 130, 246, 0.5);
            border-radius: 10px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
            background: rgba(59, 130, 246, 0.7);
        }
      `}</style>
    </div>
  );
};

export default App;
