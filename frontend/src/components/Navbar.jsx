import React from 'react';
import {
  Shield,
  FileText,
  Search,
  AlertTriangle,
  GitMerge,
  FileSpreadsheet,
  Activity,
  Cpu,
  Layers,
} from 'lucide-react';

export default function Navbar({ activeTab, setActiveTab, stats }) {
  const navItems = [
    { id: 'dashboard', label: 'Command', icon: Activity },
    { id: 'documents', label: 'Knowledge Base', icon: FileText, badge: stats?.document_count },
    { id: 'research', label: 'Signal Search', icon: Search, badge: stats?.research_count },
    { id: 'security', label: 'Threat Desk', icon: AlertTriangle, badge: stats?.security_analysis_count },
    { id: 'workflow', label: 'Mission Control', icon: GitMerge, badge: 'CORE' },
    { id: 'reports', label: 'Briefings', icon: FileSpreadsheet, badge: stats?.report_count },
  ];

  return (
    <header className="sticky top-0 z-50 border-b border-slate-200 bg-[#f4f6f1]/90 backdrop-blur-xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand Logo */}
          <div className="flex items-center gap-3 cursor-pointer" onClick={() => setActiveTab('dashboard')}>
            <div className="relative">
              <div className="w-10 h-10 rounded-lg bg-slate-950 flex items-center justify-center shadow-lg">
                <Shield className="w-5 h-5 text-lime-300" />
              </div>
              <div className="absolute -bottom-1 -right-1 w-3.5 h-3.5 rounded-full bg-lime-400 border-2 border-[#f4f6f1] animate-pulse"></div>
            </div>
            <div>
              <span className="text-lg font-black tracking-tight text-slate-950">
                Agentic_Assessments
              </span>
              <span className="block text-[10px] tracking-wider uppercase font-bold text-lime-700">
                ShivaReddy3541 / intelligence ops
              </span>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="hidden md:flex items-center gap-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-semibold transition-all duration-200 ${
                    isActive
                      ? 'bg-slate-950 text-lime-300 border border-slate-950 shadow-lg'
                      : 'text-slate-600 hover:text-slate-950 hover:bg-white/70 border border-transparent'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'text-lime-300' : 'text-slate-500'}`} />
                  {item.label}
                  {item.badge !== undefined && (
                    <span
                      className={`ml-1 text-[10px] px-1.5 py-0.2 rounded-md ${
                        isActive
                          ? 'bg-lime-400/20 text-lime-300'
                          : 'bg-slate-200 text-slate-500'
                      }`}
                    >
                      {item.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </nav>

          {/* LLM Status Badge */}
          <div className="flex items-center gap-3">
            <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white/70 border border-slate-200 text-xs text-slate-700">
              <Cpu className="w-3.5 h-3.5 text-lime-700" />
              <span className="capitalize">{stats?.llm_provider || 'Gemini'}</span>
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
            </div>
          </div>
        </div>

        {/* Mobile Navigation */}
        <div className="flex md:hidden overflow-x-auto py-2 gap-1 border-t border-white/5 scrollbar-none">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap ${
                  isActive
                    ? 'bg-slate-950 text-lime-300 border border-slate-950'
                    : 'text-slate-600 hover:text-slate-950 bg-white/70'
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                {item.label}
              </button>
            );
          })}
        </div>
      </div>
    </header>
  );
}
