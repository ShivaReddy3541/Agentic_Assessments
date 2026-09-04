import React, { useState } from 'react';
import { Copy, Check, Terminal, Search } from 'lucide-react';

export default function LogViewer({ logs = '', title = 'Raw Security Telemetry' }) {
  const [copied, setCopied] = useState(false);
  const [filter, setFilter] = useState('');

  const lines = logs.split('\n').filter((l) => l.trim().length > 0);
  const filteredLines = filter
    ? lines.filter((l) => l.toLowerCase().includes(filter.toLowerCase()))
    : lines;

  const handleCopy = () => {
    navigator.clipboard.writeText(logs);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="rounded-2xl border border-white/10 bg-[#06090F] overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-2.5 bg-white/5 border-b border-white/10">
        <div className="flex items-center gap-2">
          <Terminal className="w-4 h-4 text-cyan-400" />
          <span className="text-xs font-semibold text-slate-300">{title}</span>
          <span className="text-[10px] px-1.5 py-0.5 rounded bg-white/10 text-slate-400 font-mono">
            {lines.length} lines
          </span>
        </div>

        <div className="flex items-center gap-2">
          {/* Search Filter */}
          <div className="relative">
            <Search className="w-3 h-3 text-slate-500 absolute left-2 top-2.5" />
            <input
              type="text"
              placeholder="Filter logs..."
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="pl-7 pr-2 py-1 text-xs rounded-lg bg-black/40 border border-white/10 text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500 w-32 sm:w-44"
            />
          </div>

          <button
            onClick={handleCopy}
            className="p-1.5 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 text-slate-400 hover:text-white transition-colors"
            title="Copy Logs"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
          </button>
        </div>
      </div>

      {/* Log lines container */}
      <div className="p-3 font-mono text-xs max-h-72 overflow-y-auto space-y-1 select-text">
        {filteredLines.length > 0 ? (
          filteredLines.map((line, idx) => {
            const isAlert =
              line.includes('Failed') ||
              line.includes('DROP') ||
              line.includes('PwnKit') ||
              line.includes('UNION SELECT') ||
              line.includes('C2_BEACONING') ||
              line.includes('mimikatz');
            const isSuccess = line.includes('Accepted') || line.includes('200');

            return (
              <div
                key={idx}
                className={`flex gap-3 px-2 py-0.5 rounded hover:bg-white/5 transition-colors ${
                  isAlert
                    ? 'text-rose-300 bg-rose-950/20'
                    : isSuccess
                    ? 'text-emerald-300 bg-emerald-950/10'
                    : 'text-slate-400'
                }`}
              >
                <span className="text-slate-600 select-none w-7 text-right shrink-0">
                  {idx + 1}
                </span>
                <span className="break-all whitespace-pre-wrap">{line}</span>
              </div>
            );
          })
        ) : (
          <div className="text-center py-6 text-slate-600 text-xs italic">
            No matching log entries found
          </div>
        )}
      </div>
    </div>
  );
}
