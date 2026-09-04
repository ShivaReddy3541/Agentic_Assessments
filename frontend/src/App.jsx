import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import DocumentStudio from './pages/DocumentStudio';
import ResearchHub from './pages/ResearchHub';
import SecurityAnalyzer from './pages/SecurityAnalyzer';
import WorkflowStudio from './pages/WorkflowStudio';
import ReportsLibrary from './pages/ReportsLibrary';
import { api } from './services/api';
import { Shield, Sparkles } from 'lucide-react';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [stats, setStats] = useState(null);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const data = await api.getStats();
      setStats(data);
    } catch (err) {
      console.error('Failed to fetch system stats', err);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#f4f6f1] text-slate-950">
      {/* Top Navbar */}
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} stats={stats} />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'dashboard' && (
          <Dashboard setActiveTab={setActiveTab} stats={stats} refreshStats={fetchStats} />
        )}
        {activeTab === 'documents' && <DocumentStudio refreshStats={fetchStats} />}
        {activeTab === 'research' && <ResearchHub refreshStats={fetchStats} />}
        {activeTab === 'security' && <SecurityAnalyzer refreshStats={fetchStats} />}
        {activeTab === 'workflow' && (
          <WorkflowStudio refreshStats={fetchStats} setActiveTab={setActiveTab} />
        )}
        {activeTab === 'reports' && <ReportsLibrary />}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-200 py-6 bg-[#e9ede5] text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <Shield className="w-4 h-4 text-lime-700" />
            <span className="font-semibold text-slate-700">
              ShivaReddy3541 / Agentic_Assessments
            </span>
          </div>
          <div className="flex items-center gap-4 text-[11px]">
            <span>Intelligence workspace</span>
            <span>•</span>
            <span className="text-lime-700">4 systems online</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
