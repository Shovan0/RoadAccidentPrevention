import React from 'react';
import { Info, Activity, Shield, Zap } from 'lucide-react';

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
          <Activity className="text-green-400" /> Core Capabilities
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
          <Shield className="text-purple-400" /> Technical Stack
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
        <Zap className="text-yellow-400" size={28} /> Future Roadmap & Innovations
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

export default AboutPage;
