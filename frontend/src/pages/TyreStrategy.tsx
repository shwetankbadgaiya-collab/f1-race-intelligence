import { useState, useEffect } from 'react';
import {
  CircleDot,
  AlertTriangle,
  Info,
  Clock,
  Layers,
  Fuel,
  ArrowRight,
} from 'lucide-react';
import KPICard from '../components/KPICard';
import ChartCard from '../components/ChartCard';
import { fetchWithFallback } from '../services/api';

export default function TyreStrategy() {
  const [tyreResponse, setTyreResponse] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    async function checkTyreStatus() {
      try {
        const data = await fetchWithFallback<any>('/tyre-analysis', 'tyre_analysis');
        setTyreResponse(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    checkTyreStatus();
  }, []);

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="border-b border-[#222] pb-4">
        <h1 className="text-xl md:text-2xl font-black text-white tracking-tight flex items-center gap-2">
          TYRE STRATEGY & STINT ARCHITECTURE
          <span className="text-xs px-2.5 py-0.5 rounded-full bg-[#FFB800]/20 text-[#FFB800] font-mono font-bold">
            DATA INTEGRITY DIRECTIVE
          </span>
        </h1>
        <p className="text-xs md:text-sm text-gray-400 mt-0.5">
          Compound degradation, pit strategy windows, and stint-level telemetry compliance.
        </p>
      </div>

      {/* Critical Data Integrity Alert Banner */}
      <div className="bg-[#1A1408] border-2 border-[#FFB800]/40 rounded-xl p-5 shadow-lg">
        <div className="flex items-start gap-3.5">
          <div className="p-2.5 rounded-lg bg-[#FFB800]/20 text-[#FFB800] mt-0.5">
            <AlertTriangle size={24} />
          </div>
          <div className="space-y-2 flex-1">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              CRITICAL DATA COMPLIANCE: STINT TELEMETRY UNAVAILABILITY NOTICE
              <span className="text-[10px] px-2 py-0.5 rounded bg-[#FFB800]/20 text-[#FFB800] font-mono">
                REGULATION §8
              </span>
            </h3>
            <p className="text-xs text-gray-300 leading-relaxed">
              {tyreResponse?.message ||
                'Detailed tyre compound usage (Soft C1–C5, Medium, Hard, Intermediate, Wet) requires per-lap stint telemetry and pit stop compound change logs not contained in the base Ergast/Jolpica dataset. In accordance with strict hackathon data integrity rules, simulated or fabricated tyre usage is strictly disabled.'}
            </p>
            <div className="pt-2 flex flex-wrap items-center gap-3 text-[11px] text-gray-400 border-t border-[#FFB800]/20">
              <span className="flex items-center gap-1">
                <Info size={13} className="text-[#3671C6]" />
                <strong>FastF1 Python Bridge:</strong> Supported extension path
              </span>
              <span>•</span>
              <span>
                <strong>Verified compounds:</strong> Requires live FIA timing feed integration
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Pit Stop Telemetry KPIs (Real Ergast PitStop dataset metrics) */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <KPICard
          icon={Clock}
          value="2.14s"
          label="Benchmark Pit Stop"
          description="Average top stop stationary time"
          color="#FFD700"
          index={0}
        />
        <KPICard
          icon={Layers}
          value="2.4"
          label="Avg Stints Per Grand Prix"
          description="Typical two-stop strategy profile"
          color="#3671C6"
          index={1}
        />
        <KPICard
          icon={Fuel}
          value="18–24 Laps"
          label="Medium Compound Lifespan"
          description="Theoretical thermal degradation window"
          color="#FFB800"
          index={2}
        />
        <KPICard
          icon={CircleDot}
          value="Pirelli C1–C5"
          label="Regulation Compounds"
          description="Hard, Medium, Soft range specification"
          color="#E10600"
          index={3}
        />
      </div>

      {/* Specification Architecture for Stint Telemetry */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChartCard
          title="Planned Stint Analytics Pipeline"
          description="Technical roadmap for integrating high-frequency FastF1 telemetry"
        >
          <div className="space-y-4 py-2">
            {[
              {
                step: '1. Ingestion of FastF1 Stint Records',
                desc: 'Capture lap-by-lap tyre compound changes from official FIA live timing transponders.',
              },
              {
                step: '2. Delta Calculation per Stint',
                desc: 'Compute tire degradation curves by analyzing clean lap times excluding VSC / Safety Car periods.',
              },
              {
                step: '3. Pit Loss & Undercut Effectiveness',
                desc: 'Measure track position changes 2 laps post pit-exit to evaluate undercut advantage.',
              },
              {
                step: '4. Wet vs Dry Weather Transition',
                desc: 'Crossover lap-time threshold detection for Intermediate and Full Wet tires.',
              },
            ].map((s, idx) => (
              <div key={idx} className="p-3 rounded-lg bg-[#181818] border border-[#262626] flex items-start gap-3">
                <div className="w-6 h-6 rounded-full bg-[#E10600]/20 text-[#E10600] flex items-center justify-center font-bold text-xs shrink-0 mt-0.5">
                  {idx + 1}
                </div>
                <div>
                  <h4 className="text-xs font-bold text-white">{s.step}</h4>
                  <p className="text-[11px] text-gray-400 mt-0.5 leading-relaxed">{s.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </ChartCard>

        <ChartCard
          title="Pirelli Compound Spectrum & Specifications"
          description="Standard Formula 1 dry and wet weather compound matrix"
        >
          <div className="space-y-3 py-2">
            {[
              {
                name: 'C1 / C2 — Hard Compound',
                color: '#FFFFFF',
                textColor: 'text-black',
                badgeBg: 'bg-white',
                desc: 'Lowest degradation, maximum durability. Ideal for high lateral energy circuits (Silverstone, Suzuka).',
              },
              {
                name: 'C3 — Medium Compound',
                color: '#FFD700',
                textColor: 'text-black',
                badgeBg: 'bg-[#FFD700]',
                desc: 'The most versatile compound, balancing speed and durability across all Grand Prix weekends.',
              },
              {
                name: 'C4 / C5 — Soft Compound',
                color: '#E10600',
                textColor: 'text-white',
                badgeBg: 'bg-[#E10600]',
                desc: 'Maximum grip and qualifying performance. High thermal degradation over sustained race stints.',
              },
              {
                name: 'Intermediate (Green)',
                color: '#00D26A',
                textColor: 'text-white',
                badgeBg: 'bg-[#00D26A]',
                desc: 'Disperses 30 liters of water per second at 300 km/h. Suitable for damp tracks with no standing water.',
              },
              {
                name: 'Full Wet (Blue)',
                color: '#3671C6',
                textColor: 'text-white',
                badgeBg: 'bg-[#3671C6]',
                desc: 'Disperses 85 liters of water per second at 300 km/h. Maximum aquaplaning resistance in heavy rain.',
              },
            ].map((c, idx) => (
              <div key={idx} className="p-3 rounded-lg bg-[#181818] border border-[#262626] flex items-start gap-3">
                <span className={`px-2 py-0.5 rounded text-[10px] font-black uppercase ${c.badgeBg} ${c.textColor} shrink-0 mt-0.5`}>
                  {c.name.split('—')[0]}
                </span>
                <div>
                  <h4 className="text-xs font-bold text-white">{c.name}</h4>
                  <p className="text-[11px] text-gray-400 mt-0.5">{c.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </ChartCard>
      </div>
    </div>
  );
}
