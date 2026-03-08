import React, { useState, useEffect } from 'react';
import Navigation from './components/Navigation';
import LoginPage from './pages/LoginPage';
import ProcessingPage from './pages/ProcessingPage';
import LiveMonitorPage from './pages/LiveMonitorPage';
import HistoryPage from './pages/HistoryPage';
import AdminDashboard from './pages/AdminDashboard';
import AboutPage from './pages/AboutPage';

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
