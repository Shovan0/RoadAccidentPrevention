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
  BarChart3,
  LogOut,
  User,
  Home,
  History as HistoryIcon,
  Info,
  Menu,
  X,
  Shield,
  Eye,
  Trash2,
  Calendar,
} from 'lucide-react';

const API_ENDPOINT = 'http://127.0.0.1:5000';


// Utility function to convert data to CSV
const convertToCSVAndDownload = (data, filename) => {
  if (!data || data.length === 0) return;
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

// Login Page Component
const LoginPage = ({ onLogin }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await fetch(`${API_ENDPOINT}/api/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      });

      const data = await response.json();

      if (response.ok) {
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('username', data.username);
        localStorage.setItem('role', data.role);
        onLogin(data);
      } else {
        setError(data.error || 'Login failed');
      }
    } catch (err) {
      setError('Connection error. Please check if the server is running.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 flex items-center justify-center p-4">
      <div className="max-w-md w-full">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center bg-gradient-to-r from-blue-500 to-cyan-500 p-4 rounded-3xl shadow-2xl mb-4">
            <Shield className="w-12 h-12 text-white" />
          </div>
          <h1 className="text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-cyan-400 mb-2">
            Traffic Monitor
          </h1>
          <p className="text-blue-300">Secure Access Portal</p>
        </div>

        <div className="bg-slate-800/50 backdrop-blur-xl p-8 rounded-3xl shadow-2xl border border-slate-700/50">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Username</label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full px-4 py-3 bg-slate-900/50 border border-slate-600 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Enter username"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-3 bg-slate-900/50 border border-slate-600 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Enter password"
                required
              />
            </div>

            {error && (
              <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-3 flex items-center text-red-400 text-sm">
                <AlertTriangle className="w-5 h-5 mr-2 flex-shrink-0" />
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 text-white font-bold py-3 rounded-xl shadow-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
            >
              {loading ? (
                <>
                  <Loader className="w-5 h-5 mr-2 animate-spin" />
                  Signing in...
                </>
              ) : (
                'Sign In'
              )}
            </button>
          </form>

          <div className="mt-6 p-4 bg-blue-500/10 rounded-xl border border-blue-500/20">
            <p className="text-xs text-blue-300 font-medium mb-2">Demo Credentials:</p>
            <p className="text-xs text-slate-400">Admin: admin / admin123</p>
            <p className="text-xs text-slate-400">User: user / user123</p>
          </div>
        </div>
      </div>
    </div>
  );
};

// Navigation Component
const Navigation = ({ currentPage, setCurrentPage, user, onLogout }) => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navItems = [
    { id: 'home', label: 'Home', icon: Home },
    { id: 'monitor', label: 'Live Monitor', icon: Eye },
    { id: 'history', label: 'History', icon: HistoryIcon },
    { id: 'about', label: 'About', icon: Info },
  ];

  if (user?.role === 'admin') {
    navItems.splice(1, 0, { id: 'admin', label: 'Admin', icon: Shield });
  }

  return (
    <nav className="bg-slate-800/80 backdrop-blur-xl border-b border-slate-700/50 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center">
            <div className="bg-gradient-to-r from-blue-500 to-cyan-500 p-2 rounded-xl">
              <Activity className="w-6 h-6 text-white" />
            </div>
            <span className="ml-3 text-xl font-bold text-white hidden sm:block">Traffic AI</span>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <button
                  key={item.id}
                  onClick={() => setCurrentPage(item.id)}
                  className={`flex items-center px-4 py-2 rounded-xl font-medium transition-all ${
                    currentPage === item.id
                      ? 'bg-blue-600 text-white shadow-lg'
                      : 'text-slate-300 hover:bg-slate-700 hover:text-white'
                  }`}
                >
                  <Icon className="w-4 h-4 mr-2" />
                  {item.label}
                </button>
              );
            })}
          </div>

          <div className="flex items-center space-x-3">
            <div className="hidden sm:flex items-center bg-slate-700/50 px-3 py-2 rounded-xl">
              <User className="w-4 h-4 text-blue-400 mr-2" />
              <span className="text-sm text-white font-medium">{user?.username}</span>
              {user?.role === 'admin' && (
                <span className="ml-2 bg-blue-600 text-white text-xs px-2 py-1 rounded-full">Admin</span>
              )}
            </div>
            <button
              onClick={onLogout}
              className="flex items-center px-4 py-2 bg-red-600 hover:bg-red-500 text-white rounded-xl font-medium transition-all"
            >
              <LogOut className="w-4 h-4 mr-2" />
              <span className="hidden sm:inline">Logout</span>
            </button>
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 text-slate-300 hover:bg-slate-700 rounded-xl"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <div className="md:hidden py-4 space-y-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <button
                  key={item.id}
                  onClick={() => {
                    setCurrentPage(item.id);
                    setMobileMenuOpen(false);
                  }}
                  className={`w-full flex items-center px-4 py-3 rounded-xl font-medium transition-all ${
                    currentPage === item.id ? 'bg-blue-600 text-white' : 'text-slate-300 hover:bg-slate-700'
                  }`}
                >
                  <Icon className="w-5 h-5 mr-3" />
                  {item.label}
                </button>
              );
            })}
          </div>
        )}
      </div>
    </nav>
  );
};

// Admin Dashboard Component
const AdminDashboard = ({ token }) => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const fetchStats = async () => {
    try {
      const response = await fetch(`${API_ENDPOINT}/api/stats`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (err) {
      console.error('Failed to fetch stats:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader className="w-8 h-8 text-blue-500 animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-white flex items-center">
          <Shield className="w-8 h-8 mr-3 text-blue-400" />
          Admin Dashboard
        </h1>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-gradient-to-br from-blue-600 to-blue-700 rounded-2xl p-6 shadow-xl">
          <div className="flex items-center justify-between mb-3">
            <FileVideo className="w-10 h-10 text-white opacity-80" />
            <span className="text-4xl font-bold text-white">{stats?.total_videos || 0}</span>
          </div>
          <p className="text-blue-100 font-medium">Total Videos</p>
        </div>

        <div className="bg-gradient-to-br from-green-600 to-green-700 rounded-2xl p-6 shadow-xl">
          <div className="flex items-center justify-between mb-3">
            <Car className="w-10 h-10 text-white opacity-80" />
            <span className="text-4xl font-bold text-white">{stats?.total_vehicles || 0}</span>
          </div>
          <p className="text-green-100 font-medium">Total Vehicles</p>
        </div>

        <div className="bg-gradient-to-br from-red-600 to-red-700 rounded-2xl p-6 shadow-xl">
          <div className="flex items-center justify-between mb-3">
            <AlertTriangle className="w-10 h-10 text-white opacity-80" />
            <span className="text-4xl font-bold text-white">{stats?.total_violations || 0}</span>
          </div>
          <p className="text-red-100 font-medium">Total Violations</p>
        </div>

        <div className="bg-gradient-to-br from-purple-600 to-purple-700 rounded-2xl p-6 shadow-xl">
          <div className="flex items-center justify-between mb-3">
            <TrendingUp className="w-10 h-10 text-white opacity-80" />
            <span className="text-4xl font-bold text-white">{stats?.violation_rate || 0}%</span>
          </div>
          <p className="text-purple-100 font-medium">Violation Rate</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-slate-800/50 backdrop-blur-xl p-6 rounded-3xl shadow-2xl border border-slate-700/50">
          <h2 className="text-xl font-bold text-white mb-4 flex items-center">
            <BarChart3 className="w-6 h-6 mr-2 text-blue-400" />
            Speed Statistics
          </h2>
          <div className="space-y-4">
            <div className="flex justify-between items-center p-4 bg-slate-700/30 rounded-xl">
              <span className="text-slate-300">Average Speed</span>
              <span className="text-2xl font-bold text-blue-400">{stats?.avg_speed || 0} km/h</span>
            </div>
            <div className="flex justify-between items-center p-4 bg-slate-700/30 rounded-xl">
              <span className="text-slate-300">Maximum Speed</span>
              <span className="text-2xl font-bold text-red-400">{stats?.max_speed || 0} km/h</span>
            </div>
          </div>
        </div>

        <div className="bg-slate-800/50 backdrop-blur-xl p-6 rounded-3xl shadow-2xl border border-slate-700/50">
          <h2 className="text-xl font-bold text-white mb-4 flex items-center">
            <Calendar className="w-6 h-6 mr-2 text-green-400" />
            Recent Activity
          </h2>
          <div className="space-y-4">
            <div className="flex justify-between items-center p-4 bg-slate-700/30 rounded-xl">
              <span className="text-slate-300">Videos (Last 7 Days)</span>
              <span className="text-2xl font-bold text-green-400">{stats?.recent_activity || 0}</span>
            </div>
            <div className="p-4 bg-blue-500/10 border border-blue-500/30 rounded-xl">
              <p className="text-sm text-blue-300">
                System is actively monitoring traffic. All data is being logged and analyzed in real-time.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// History Page Component
const HistoryPage = ({ token }) => {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedRecord, setSelectedRecord] = useState(null);

  useEffect(() => {
    fetchHistory();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const fetchHistory = async () => {
    try {
      const response = await fetch(`${API_ENDPOINT}/api/history`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (response.ok) {
        const data = await response.json();
        setHistory(data);
      }
    } catch (err) {
      console.error('Failed to fetch history:', err);
    } finally {
      setLoading(false);
    }
  };

  const deleteRecord = async (id) => {
    if (!window.confirm('Are you sure you want to delete this record?')) return;

    try {
      const response = await fetch(`${API_ENDPOINT}/api/history/${id}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
      });
      if (response.ok) {
        setHistory(history.filter((h) => h.id !== id));
        setSelectedRecord(null);
      }
    } catch (err) {
      console.error('Failed to delete record:', err);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader className="w-8 h-8 text-blue-500 animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-white flex items-center">
        <HistoryIcon className="w-8 h-8 mr-3 text-blue-400" />
        Processing History
      </h1>

      {history.length === 0 ? (
        <div className="bg-slate-800/50 backdrop-blur-xl p-12 rounded-3xl shadow-2xl border border-slate-700/50 text-center">
          <HistoryIcon className="w-16 h-16 text-slate-600 mx-auto mb-4" />
          <p className="text-slate-400 text-lg">No processing history yet</p>
          <p className="text-slate-500 text-sm mt-2">Upload and process videos to see them here</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {history.map((record) => (
            <div
              key={record.id}
              className="bg-slate-800/50 backdrop-blur-xl p-6 rounded-3xl shadow-2xl border border-slate-700/50 hover:border-blue-500/50 transition-all"
            >
              <div className="flex justify-between items-start mb-4">
                <div className="flex-1">
                  <h3 className="text-lg font-bold text-white mb-1">{record.original_filename}</h3>
                  <p className="text-sm text-slate-400">{new Date(record.timestamp).toLocaleString()}</p>
                  <p className="text-xs text-slate-500 mt-1">By: {record.user}</p>
                </div>
                <button
                  onClick={() => deleteRecord(record.id)}
                  className="p-2 text-red-400 hover:bg-red-500/10 rounded-xl transition-all"
                >
                  <Trash2 className="w-5 h-5" />
                </button>
              </div>

              <div className="grid grid-cols-3 gap-3 mb-4">
                <div className="bg-blue-500/10 border border-blue-500/30 rounded-xl p-3 text-center">
                  <p className="text-2xl font-bold text-blue-400">{record.total_vehicles}</p>
                  <p className="text-xs text-slate-400">Vehicles</p>
                </div>
                <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-3 text-center">
                  <p className="text-2xl font-bold text-red-400">{record.total_violations}</p>
                  <p className="text-xs text-slate-400">Violations</p>
                </div>
                <div className="bg-green-500/10 border border-green-500/30 rounded-xl p-3 text-center">
                  <p className="text-2xl font-bold text-green-400">{record.overspeed_limit}</p>
                  <p className="text-xs text-slate-400">Limit (km/h)</p>
                </div>
              </div>

              <div className="flex gap-2">
                <button
                  onClick={() => setSelectedRecord(record)}
                  className="flex-1 flex items-center justify-center px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-xl font-medium transition-all"
                >
                  <Eye className="w-4 h-4 mr-2" />
                  View Details
                </button>
                {record.download_name && (
                  <button
                    onClick={async () => {
                      try {
                        const response = await fetch(`${API_ENDPOINT}/download/${record.download_name}`, {
                          headers: { Authorization: `Bearer ${token}` },
                        });
                        const blob = await response.blob();
                        const url = window.URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = record.download_name;
                        document.body.appendChild(a);
                        a.click();
                        window.URL.revokeObjectURL(url);
                        document.body.removeChild(a);
                      } catch (err) {
                        console.error('Download failed:', err);
                      }
                    }}
                    className="flex items-center justify-center px-4 py-2 bg-green-600 hover:bg-green-500 text-white rounded-xl font-medium transition-all"
                  >
                    <Download className="w-4 h-4" />
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Detail Modal */}
      {selectedRecord && (
        <div
          className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4"
          onClick={() => setSelectedRecord(null)}
        >
          <div
            className="bg-slate-800 rounded-3xl shadow-2xl border border-slate-700 max-w-4xl w-full max-h-[90vh] overflow-y-auto custom-scrollbar"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="sticky top-0 bg-slate-800 border-b border-slate-700 p-6 flex justify-between items-center">
              <h2 className="text-2xl font-bold text-white">Record Details</h2>
              <button onClick={() => setSelectedRecord(null)} className="p-2 hover:bg-slate-700 rounded-xl">
                <X className="w-6 h-6 text-slate-400" />
              </button>
            </div>
            <div className="p-6 space-y-6">
              <div>
                <h3 className="text-lg font-bold text-white mb-3">Vehicle Logs</h3>
                <div className="space-y-2 max-h-96 overflow-y-auto custom-scrollbar">
                  {selectedRecord.all_logs?.map((log, idx) => (
                    <div
                      key={idx}
                      className={`p-3 rounded-xl flex items-center justify-between ${
                        log.overspeed
                          ? 'bg-red-500/10 border border-red-500/30'
                          : 'bg-green-500/10 border border-green-500/30'
                      }`}
                    >
                      <div className="flex items-center">
                        {log.overspeed ? (
                          <AlertTriangle className="w-5 h-5 text-red-400 mr-3" />
                        ) : (
                          <CheckCircle className="w-5 h-5 text-green-400 mr-3" />
                        )}
                        <div>
                          <p
                            className={`font-bold ${
                              log.overspeed ? 'text-red-400' : 'text-green-400'
                            }`}
                          >
                            ID: {log.id} • {log.label}
                          </p>
                          <p className="text-xs text-slate-400">Frame: {log.frame}</p>
                        </div>
                      </div>
                      <p
                        className={`text-xl font-bold ${
                          log.overspeed ? 'text-red-400' : 'text-green-400'
                        }`}
                      >
                        {log.speed} km/h
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// About Page Component
const AboutPage = () => {
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-white flex items-center">
        <Info className="w-8 h-8 mr-3 text-blue-400" />
        About This System
      </h1>

      <div className="bg-slate-800/50 backdrop-blur-xl p-8 rounded-3xl shadow-2xl border border-slate-700/50">
        <h2 className="text-2xl font-bold text-white mb-4">AI Traffic Speed Detection System</h2>
        <p className="text-slate-300 leading-relaxed mb-6">
          This advanced traffic monitoring system uses YOLOv8 neural networks to detect and track vehicles in
          real-time, calculating their speeds and identifying violations. The system provides comprehensive
          analytics and reporting capabilities for traffic management authorities.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <div className="bg-blue-500/10 border border-blue-500/30 rounded-xl p-6">
            <Zap className="w-10 h-10 text-blue-400 mb-3" />
            <h3 className="text-lg font-bold text-white mb-2">Real-time Detection</h3>
            <p className="text-slate-400 text-sm">
              Advanced AI algorithms process video feeds in real-time, detecting multiple vehicle types
              simultaneously.
            </p>
          </div>

          <div className="bg-green-500/10 border border-green-500/30 rounded-xl p-6">
            <BarChart3 className="w-10 h-10 text-green-400 mb-3" />
            <h3 className="text-lg font-bold text-white mb-2">Analytics Dashboard</h3>
            <p className="text-slate-400 text-sm">
              Comprehensive statistics and historical data analysis for informed decision-making.
            </p>
          </div>

          <div className="bg-purple-500/10 border border-purple-500/30 rounded-xl p-6">
            <Shield className="w-10 h-10 text-purple-400 mb-3" />
            <h3 className="text-lg font-bold text-white mb-2">Secure Platform</h3>
            <p className="text-slate-400 text-sm">
              Role-based access control ensures data security and proper authorization.
            </p>
          </div>

          <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-6">
            <AlertTriangle className="w-10 h-10 text-red-400 mb-3" />
            <h3 className="text-lg font-bold text-white mb-2">Violation Detection</h3>
            <p className="text-slate-400 text-sm">
              Automatic identification and logging of speed violations with detailed records.
            </p>
          </div>
        </div>

        <div className="bg-slate-700/30 rounded-xl p-6">
          <h3 className="text-lg font-bold text-white mb-3">Technical Specifications</h3>
          <ul className="space-y-2 text-slate-300 text-sm">
            <li className="flex items-center">
              <CheckCircle className="w-4 h-4 text-green-400 mr-2" />
              Real-time Speed Calculation
            </li>
            <li className="flex items-center">
              <CheckCircle className="w-4 h-4 text-green-400 mr-2" />
              Support for Multiple Video Formats (MP4, AVI, MOV, MKV)
            </li>
            <li className="flex items-center">
              <CheckCircle className="w-4 h-4 text-green-400 mr-2" />
              CSV Export for Data Analysis
            </li>
            <li className="flex items-center">
              <CheckCircle className="w-4 h-4 text-green-400 mr-2" />
              Historical Data Management
            </li>
            {/* Added these two lines properly inside the UL */}
            <li className="flex items-center">
              <CheckCircle className="w-4 h-4 text-green-400 mr-2" />
              YOLOv8 Object Detection Model
            </li>
            <li className="flex items-center">
              <CheckCircle className="w-4 h-4 text-green-400 mr-2" />
              ByteTrack Multi-object Tracking
            </li>
          </ul>
        </div>

        <div className="mt-6 pt-6 border-t border-slate-700">
          <p className="text-slate-400 text-sm text-center">
            © 2024 AI Traffic Speed Detection System. Powered by YOLOv8 and React.
          </p>
        </div>
      </div>
    </div>
  );
};

// Main Processing Page Component - Now receives and updates shared state
const ProcessingPage = ({ token, processingState, setProcessingState }) => {
  const { file, previewUrl, isProcessing, progress, logs, statusMessage, downloadLink } = processingState;

  const overspeedRecords = useMemo(() => logs.filter((log) => log.overspeed), [logs]);
  const avgSpeed = useMemo(() => {
    if (logs.length === 0) return 0;
    const total = logs.reduce((sum, log) => sum + (log.speed || 0), 0);
    return (total / logs.length).toFixed(1);
  }, [logs]);
  const maxSpeed = useMemo(() => {
    if (logs.length === 0) return 0;
    return Math.max(...logs.map((log) => log.speed || 0)).toFixed(1);
  }, [logs]);

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    if (selectedFile) {
      setProcessingState({
        file: selectedFile,
        previewUrl: URL.createObjectURL(selectedFile),
        progress: 0,
        logs: [],
        isProcessing: false,
        downloadLink: null,
        statusMessage: `Video loaded: ${selectedFile.name}`,
      });
    }
  };

  const handleProcessing = useCallback(async () => {
    if (!file) {
      setProcessingState((prev) => ({
        ...prev,
        statusMessage: 'Please upload a video file first.',
      }));
      return;
    }

    setProcessingState((prev) => ({
      ...prev,
      isProcessing: true,
      logs: [],
      progress: 5,
      downloadLink: null,
      statusMessage: 'Processing video with AI detection...',
    }));

    const formData = new FormData();
    formData.append('video', file);

    try {
      const response = await fetch(`${API_ENDPOINT}/upload-and-process`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(errorData?.error || `Server responded with status ${response.status}`);
      }

      const result = await response.json();
      const serverOrigin = new URL(API_ENDPOINT).origin;
      const fullDownloadUrl = result.output_video_url ? serverOrigin + result.output_video_url : null;

      setProcessingState((prev) => ({
        ...prev,
        progress: 100,
        statusMessage: '✅ Processing complete! Analysis ready.',
        logs: result.all_logs || [],
        downloadLink: fullDownloadUrl,
        isProcessing: false,
      }));
    } catch (error) {
      console.error('Processing failed:', error);
      setProcessingState((prev) => ({
        ...prev,
        statusMessage: `❌ Error: ${error.message}`,
        progress: 0,
        isProcessing: false,
      }));
    }
  }, [file, token, setProcessingState]);

  return (
    <div className="space-y-6">
      {/* Statistics Cards */}
      {logs.length > 0 && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
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

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
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
                    {file ? file.name : 'Click to upload video'}
                  </p>
                  <p className="text-slate-400 text-sm">Supports MP4, AVI, MOV, MKV formats</p>
                </div>
              </div>
            </label>

            <div className="mb-6">
              <div className="flex items-center justify-between mb-2">
                <p
                  className={`text-sm font-medium ${
                    isProcessing ? 'text-blue-400' : 'text-slate-300'
                  }`}
                >
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
                <button
                  onClick={async () => {
                    try {
                      const response = await fetch(downloadLink, {
                        headers: { Authorization: `Bearer ${token}` },
                      });
                      const blob = await response.blob();
                      const url = window.URL.createObjectURL(blob);
                      const a = document.createElement('a');
                      a.href = url;
                      a.download = downloadLink.split('/').pop();
                      document.body.appendChild(a);
                      a.click();
                      window.URL.revokeObjectURL(url);
                      document.body.removeChild(a);
                    } catch (err) {
                      console.error('Download failed:', err);
                    }
                  }}
                  className="flex items-center justify-center px-6 py-4 rounded-2xl font-bold text-white bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-500 hover:to-emerald-500 shadow-lg shadow-green-500/50 transition-all duration-300 transform hover:scale-[1.02]"
                >
                  <Download className="w-5 h-5 mr-2" />
                  Download
                </button>
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
                  <div
                    key={index}
                    className={`py-2 px-3 mb-2 rounded-lg flex items-start ${
                      log.overspeed
                        ? 'bg-red-500/10 border border-red-500/30'
                        : 'bg-green-500/10 border border-green-500/30'
                    }`}
                  >
                    {log.overspeed ? (
                      <AlertTriangle className="w-4 h-4 text-red-400 mr-2 flex-shrink-0 mt-0.5" />
                    ) : (
                      <CheckCircle className="w-4 h-4 text-green-400 mr-2 flex-shrink-0 mt-0.5" />
                    )}
                    <div className="flex-1">
                      <div
                        className={`font-bold ${
                          log.overspeed ? 'text-red-400' : 'text-green-400'
                        }`}
                      >
                        ID:{log.id} • {log.label}
                      </div>
                      <div className="text-slate-400 text-[10px]">
                        {typeof log.speed === 'number'
                          ? log.speed.toFixed(2)
                          : log.speed}{' '}
                        km/h • Frame {log.frame}
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
                  {overspeedRecords.map((record) => (
                    <div
                      key={record.id}
                      className="p-4 bg-red-500/10 border-2 border-red-500/30 rounded-xl shadow-lg backdrop-blur-sm hover:bg-red-500/20 transition-all"
                    >
                      <div className="flex justify-between items-start mb-2">
                        <div>
                          <p className="font-bold text-red-400 text-sm">{record.label}</p>
                          <p className="text-xs text-slate-400">ID: {record.id}</p>
                        </div>
                        <div className="text-right">
                          <p className="text-2xl font-black text-red-400">
                            {typeof record.speed === 'number'
                              ? record.speed.toFixed(1)
                              : record.speed}
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
    </div>
  );
};

// Main App Component
const App = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [currentPage, setCurrentPage] = useState('home');
  const [loading, setLoading] = useState(true);

  // Shared processing state that persists across page navigation
  const [processingState, setProcessingState] = useState({
    file: null,
    previewUrl: null,
    isProcessing: false,
    progress: 0,
    logs: [],
    statusMessage: 'Ready to process traffic video',
    downloadLink: null,
  });

  useEffect(() => {
    // Check if user is already logged in
    const token = localStorage.getItem('token');
    const username = localStorage.getItem('username');

    if (token && username) {
      // Verify token
      fetch(`${API_ENDPOINT}/api/verify-token`, {
        headers: { Authorization: `Bearer ${token}` },
      })
        .then((res) => res.json())
        .then((data) => {
          if (data?.username && data?.role) {
            setUser({ username: data.username, role: data.role });
            setIsAuthenticated(true);
          } else {
            localStorage.removeItem('token');
            localStorage.removeItem('username');
            localStorage.removeItem('role');
          }
        })
        .catch(() => {
          // Token invalid, clear storage
          localStorage.removeItem('token');
          localStorage.removeItem('username');
          localStorage.removeItem('role');
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const handleLogin = (userData) => {
    setUser({ username: userData.username, role: userData.role });
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    localStorage.removeItem('role');
    setIsAuthenticated(false);
    setUser(null);
    setCurrentPage('home');
    // Reset processing state on logout
    setProcessingState({
      file: null,
      previewUrl: null,
      isProcessing: false,
      progress: 0,
      logs: [],
      statusMessage: 'Ready to process traffic video',
      downloadLink: null,
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 flex items-center justify-center">
        <Loader className="w-12 h-12 text-blue-500 animate-spin" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <LoginPage onLogin={handleLogin} />;
  }

  const token = localStorage.getItem('token');

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
      <Navigation
        currentPage={currentPage}
        setCurrentPage={setCurrentPage}
        user={user}
        onLogout={handleLogout}
      />

      <div className="max-w-7xl mx-auto p-4 sm:p-8">
        {currentPage === 'home' && (
          <>
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
                  <span className="flex items-center gap-1">
                    <Zap className="w-4 h-4" /> Real-time Analysis
                  </span>
                  <span className="flex items-center gap-1">
                    <Car className="w-4 h-4" /> Multi-vehicle Tracking
                  </span>
                  <span className="flex items-center gap-1">
                    <BarChart3 className="w-4 h-4" /> Statistical Insights
                  </span>
                </div>
              </div>
            </header>
            <ProcessingPage
              token={token}
              processingState={processingState}
              setProcessingState={setProcessingState}
            />
          </>
        )}

        {currentPage === 'admin' && user?.role === 'admin' && <AdminDashboard token={token} />}

        {currentPage === 'monitor' && (
          <ProcessingPage
            token={token}
            processingState={processingState}
            setProcessingState={setProcessingState}
          />
        )}

        {currentPage === 'history' && <HistoryPage token={token} />}

        {currentPage === 'about' && <AboutPage />}
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
