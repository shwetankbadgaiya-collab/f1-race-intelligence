import { useState, useEffect } from 'react';
import { Sparkles, TrendingUp, AlertCircle, CheckCircle, ChevronDown, ChevronUp } from 'lucide-react';
import { fetchWithFallback } from '../services/api';
import type { Insight } from '../types';

interface InsightItemData {
  category: string;
  title: string;
  description: string;
  metric_value?: number;
  comparison_value?: number;
  season_range?: string;
  severity: string;
}

export default function InsightsPanel() {
  const [insights, setInsights] = useState<InsightItemData[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [collapsed, setCollapsed] = useState<boolean>(false);

  useEffect(() => {
    async function loadInsights() {
      try {
        const data = await fetchWithFallback<InsightItemData[]>('/insights', 'insights');
        setInsights(data);
      } catch {
        // Fallback or offline
      } finally {
        setLoading(false);
      }
    }
    loadInsights();
  }, []);

  if (loading && insights.length === 0) return null;
  if (!loading && insights.length === 0) return null;

  const getSeverityBadge = (sev: string) => {
    switch (sev) {
      case 'positive':
        return {
          icon: <CheckCircle size={14} className="text-[#00D26A]" />,
          border: 'border-[#00D26A]/30',
          bg: 'bg-[#00D26A]/10',
          text: 'text-[#00D26A]',
        };
      case 'warning':
      case 'negative':
        return {
          icon: <AlertCircle size={14} className="text-[#FFB800]" />,
          border: 'border-[#FFB800]/30',
          bg: 'bg-[#FFB800]/10',
          text: 'text-[#FFB800]',
        };
      default:
        return {
          icon: <TrendingUp size={14} className="text-[#3671C6]" />,
          border: 'border-[#3671C6]/30',
          bg: 'bg-[#3671C6]/10',
          text: 'text-[#3671C6]',
        };
    }
  };

  return (
    <div className="bg-[#141414] border border-[#262626] rounded-xl p-4 mb-6 shadow-md transition-all">
      <div
        className="flex items-center justify-between cursor-pointer select-none"
        onClick={() => setCollapsed(!collapsed)}
      >
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-[#E10600]/15 text-[#E10600]">
            <Sparkles size={16} />
          </div>
          <div>
            <h4 className="text-xs font-bold text-white tracking-wider uppercase flex items-center gap-2">
              Automated Race Intelligence Insights
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-[#E10600]/20 text-[#E10600] font-mono">
                {insights.length} OBSERVATIONS
              </span>
            </h4>
            <p className="text-[11px] text-gray-400">
              Deterministic observations derived directly from race telemetry & standings
            </p>
          </div>
        </div>
        <button className="text-gray-400 hover:text-white p-1">
          {collapsed ? <ChevronDown size={16} /> : <ChevronUp size={16} />}
        </button>
      </div>

      {!collapsed && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 mt-4 pt-3 border-t border-[#222]">
          {insights.slice(0, 6).map((item, idx) => {
            const badge = getSeverityBadge(item.severity);
            return (
              <div
                key={idx}
                className={`p-3 rounded-lg border ${badge.border} ${badge.bg} flex flex-col justify-between`}
              >
                <div>
                  <div className="flex items-center gap-2 mb-1.5">
                    {badge.icon}
                    <span className="text-xs font-bold text-white line-clamp-1">{item.title}</span>
                  </div>
                  <p className="text-[11px] text-gray-300 leading-relaxed mb-2">{item.description}</p>
                </div>
                <div className="flex items-center justify-between text-[10px] text-gray-400 pt-1.5 border-t border-white/5">
                  <span className="uppercase tracking-wider font-semibold text-gray-500">
                    {item.category}
                  </span>
                  {item.season_range && (
                    <span className="font-mono text-gray-400">{item.season_range}</span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
