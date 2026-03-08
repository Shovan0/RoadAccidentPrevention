import React, { useState, useEffect } from 'react';
import { Shield, FileVideo, Car, AlertTriangle, Activity } from 'lucide-react';
import { API_ENDPOINT } from '../constants';
import StatBox from '../components/StatBox';

const AdminDashboard = ({ token }) => {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    fetch(`${API_ENDPOINT}/api/stats`, { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.json())
      .then(setStats)
      .catch(() => setStats({ total_videos: 0, total_vehicles: 0, total_violations: 0, avg_speed: 0 }));
  }, [token]);

  if (!stats) return <div className="text-white p-10 text-center">Loading stats...</div>;

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-white flex items-center gap-3"><Shield className="text-blue-400" /> Admin Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatBox label="Total Videos" value={stats.total_videos} icon={<FileVideo />} color="blue" />
        <StatBox label="Total Vehicles" value={stats.total_vehicles} icon={<Car />} color="green" />
        <StatBox label="Violations" value={stats.total_violations} icon={<AlertTriangle />} color="red" />
        <StatBox label="Avg Speed" value={`${stats.avg_speed} km/h`} icon={<Activity />} color="purple" />
      </div>
    </div>
  );
};

export default AdminDashboard;
