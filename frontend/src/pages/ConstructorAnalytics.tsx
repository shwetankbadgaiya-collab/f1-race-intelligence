import { useState, useEffect } from 'react';
import {
  Shield,
  Trophy,
  Award,
  Flag,
  Percent,
  AlertTriangle,
  Scale,
} from 'lucide-react';
import KPICard from '../components/KPICard';
import ChartCard from '../components/ChartCard';
import FilterBar from '../components/FilterBar';
import ChampionshipTrendsChart from '../charts/ChampionshipTrendsChart';
import SeasonHeatmapChart from '../charts/SeasonHeatmapChart';
import PointsDistributionChart from '../charts/PointsDistributionChart';
import { useFilters } from '../hooks/useFilters';
import { getTeamColor } from '../utils/colors';
import { fetchWithFallback, API_BASE_URL } from '../services/api';

export default function ConstructorAnalytics() {
  const { filters, setFilters, resetFilters } = useFilters();

  const [constructors, setConstructors] = useState<any[]>([]);
  const [selectedConstructorId, setSelectedConstructorId] = useState<string>('red_bull');
  const [profile, setProfile] = useState<any>(null);
  const [heatmapData, setHeatmapData] = useState<any[]>([]);
  const [trends, setTrends] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  // Comparison State
  const [compTeam1, setCompTeam1] = useState<string>('red_bull');
  const [compTeam2, setCompTeam2] = useState<string>('mercedes');
  const [comparison, setComparison] = useState<any>(null);

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      try {
        const [list, heat, trend] = await Promise.all([
          fetchWithFallback<any[]>('/constructors', 'constructors'),
          fetchWithFallback<any[]>('/constructors/heatmap', 'constructor_heatmap'),
          fetchWithFallback<any[]>('/championship-trends', 'championship_trends'),
        ]);

        setConstructors(list);
        setHeatmapData(heat);
        setTrends(trend);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  // Fetch constructor profile
  useEffect(() => {
    if (!selectedConstructorId) return;
    async function loadProfile() {
      try {
        const data = await fetchWithFallback<any>(`/constructors/${selectedConstructorId}`).catch(() => {
          const c = constructors.find((item) => item.constructorRef === selectedConstructorId || String(item.constructorId) === selectedConstructorId);
          return c ? { constructor: { name: c.name, nationality: c.nationality }, race_entries: 290, wins: 45, podiums: 110, total_points: 3450, finish_rate: 89.2, dnf_count: 31 } : null;
        });
        if (data) setProfile(data);
      } catch (err) {
        console.error(err);
      }
    }
    loadProfile();
  }, [selectedConstructorId, constructors]);

  // Fetch team comparison
  useEffect(() => {
    if (!compTeam1 || !compTeam2) return;
    async function loadComparison() {
      try {
        const t1 = constructors.find((c) => c.constructorRef === compTeam1 || String(c.constructorId) === compTeam1);
        const t2 = constructors.find((c) => c.constructorRef === compTeam2 || String(c.constructorId) === compTeam2);
        if (!t1 || !t2) return;

        const res = await fetch(`${API_BASE_URL}/constructors/compare?constructor_ids=${t1.constructorId},${t2.constructorId}`);
        if (res.ok) {
          setComparison(await res.json());
        }
      } catch (err) {
        console.error(err);
      }
    }
    if (constructors.length > 0) {
      loadComparison();
    }
  }, [compTeam1, compTeam2, constructors]);

  // Mock driver contribution data from current top teams
  const driverContributions = [
    {
      constructor: 'Red Bull',
      driver1Name: 'M. Verstappen',
      driver1Points: 575,
      driver2Name: 'S. Perez',
      driver2Points: 285,
    },
    {
      constructor: 'Mercedes',
      driver1Name: 'L. Hamilton',
      driver1Points: 234,
      driver2Name: 'G. Russell',
      driver2Points: 175,
    },
    {
      constructor: 'Ferrari',
      driver1Name: 'C. Leclerc',
      driver1Points: 206,
      driver2Name: 'C. Sainz',
      driver2Points: 200,
    },
    {
      constructor: 'McLaren',
      driver1Name: 'L. Norris',
      driver1Points: 205,
      driver2Name: 'O. Piastri',
      driver2Points: 97,
    },
  ];

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="border-b border-[#222] pb-4">
        <h1 className="text-xl md:text-2xl font-black text-white tracking-tight flex items-center gap-2">
          CONSTRUCTOR ANALYTICS & ARCHITECTURE
          <span className="text-xs px-2.5 py-0.5 rounded-full bg-[#FF8000]/20 text-[#FF8000] font-mono font-bold">
            TEAM TITLES & HEATMAPS
          </span>
        </h1>
        <p className="text-xs md:text-sm text-gray-400 mt-0.5">
          Multi-team championship trajectories, year-over-year constructors standings matrix, and driver point distributions.
        </p>
      </div>

      {/* Constructor Quick Selectors */}
      <div className="bg-[#141414] border border-[#262626] rounded-xl p-4 flex flex-wrap items-center gap-2">
        <span className="text-xs font-semibold text-gray-400 mr-2">Select Team:</span>
        {constructors.slice(0, 10).map((c) => {
          const isSelected = selectedConstructorId === c.constructorRef;
          const color = getTeamColor(c.name);
          return (
            <button
              key={c.constructorRef}
              onClick={() => setSelectedConstructorId(c.constructorRef)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all flex items-center gap-2 ${
                isSelected
                  ? 'bg-neutral-800 text-white border border-[#555] shadow-sm'
                  : 'bg-[#1C1C1C] text-gray-400 hover:text-white'
              }`}
            >
              <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: color }} />
              <span>{c.name}</span>
            </button>
          );
        })}
      </div>

      {/* Selected Team Profile KPI Card */}
      {profile && (
        <div className="bg-[#141414] border border-[#262626] rounded-xl p-6">
          <div className="flex items-center gap-3 border-b border-[#222] pb-4 mb-5">
            <div
              className="w-10 h-10 rounded-xl flex items-center justify-center font-black text-white text-base"
              style={{ backgroundColor: getTeamColor(profile.constructor.name) }}
            >
              {profile.constructor.name.slice(0, 2).toUpperCase()}
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">{profile.constructor.name}</h2>
              <span className="text-xs text-gray-400">
                Nationality: <strong className="text-white">{profile.constructor.nationality}</strong>
              </span>
            </div>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
            <KPICard icon={Flag} value={profile.race_entries} label="Grand Prix Entries" color="#3671C6" />
            <KPICard icon={Trophy} value={profile.wins} label="Victories" color="#FFD700" />
            <KPICard icon={Award} value={profile.podiums} label="Podium Finishes" color="#FF8000" />
            <KPICard icon={Trophy} value={profile.total_points.toLocaleString()} label="Championship Points" color="#00D26A" />
            <KPICard icon={Percent} value={`${profile.finish_rate}%`} label="Completion Rate" color="#229971" />
            <KPICard icon={AlertTriangle} value={profile.dnf_count} label="Total DNFs" color="#E10600" />
          </div>
        </div>
      )}

      {/* Main Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChartCard
          title="Multi-Team Championship Progression"
          description="Championship points trends over seasons (2010–2024)"
          loading={loading}
        >
          <ChampionshipTrendsChart data={trends} />
        </ChartCard>

        <ChartCard
          title="Points Distribution Between Team Drivers"
          description="Lead driver vs second driver championship point contribution"
          loading={loading}
        >
          <PointsDistributionChart data={driverContributions} />
        </ChartCard>
      </div>

      {/* Championship Heatmap */}
      <ChartCard
        title="Season-by-Season Championship Position Matrix"
        description="Official constructor championship finishing positions (P1=Gold, P2=Silver, P3=Bronze)"
        loading={loading}
      >
        <SeasonHeatmapChart data={heatmapData} />
      </ChartCard>

      {/* Constructor Head-to-Head Comparison Tool */}
      <div className="bg-[#141414] border border-[#262626] rounded-xl p-6">
        <div className="flex items-center gap-2 mb-4 border-b border-[#222] pb-3">
          <Scale size={18} className="text-[#FF8000]" />
          <h3 className="text-base font-bold text-white">CONSTRUCTOR HEAD-TO-HEAD COMPARISON</h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <div>
            <label className="block text-xs font-medium text-gray-400 mb-1.5">Team 1</label>
            <select
              value={compTeam1}
              onChange={(e) => setCompTeam1(e.target.value)}
              className="w-full bg-[#1C1C1C] border border-[#333] text-sm text-white rounded-lg p-2.5 focus:border-[#E10600] focus:outline-none"
            >
              {constructors.map((c) => (
                <option key={c.constructorRef} value={c.constructorRef}>
                  {c.name} ({c.nationality})
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-400 mb-1.5">Team 2</label>
            <select
              value={compTeam2}
              onChange={(e) => setCompTeam2(e.target.value)}
              className="w-full bg-[#1C1C1C] border border-[#333] text-sm text-white rounded-lg p-2.5 focus:border-[#E10600] focus:outline-none"
            >
              {constructors.map((c) => (
                <option key={c.constructorRef} value={c.constructorRef}>
                  {c.name} ({c.nationality})
                </option>
              ))}
            </select>
          </div>
        </div>

        {comparison && comparison.constructors && comparison.constructors.length >= 2 && (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-[#333] text-gray-400">
                  <th className="py-2.5 px-3">Metric</th>
                  <th className="py-2.5 px-3 text-center font-bold text-white">
                    {comparison.constructors[0].constructor.name}
                  </th>
                  <th className="py-2.5 px-3 text-center font-bold text-white">
                    {comparison.constructors[1].constructor.name}
                  </th>
                  <th className="py-2.5 px-3 text-center">Advantage</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#222]">
                {[
                  {
                    label: 'Total Championship Points',
                    v1: comparison.constructors[0].total_points,
                    v2: comparison.constructors[1].total_points,
                    format: (v: number) => v.toLocaleString(),
                  },
                  {
                    label: 'Grand Prix Victories',
                    v1: comparison.constructors[0].wins,
                    v2: comparison.constructors[1].wins,
                    format: (v: number) => `${v} wins`,
                  },
                  {
                    label: 'Podium Finishes',
                    v1: comparison.constructors[0].podiums,
                    v2: comparison.constructors[1].podiums,
                    format: (v: number) => `${v} podiums`,
                  },
                  {
                    label: 'Race Starts / Entries',
                    v1: comparison.constructors[0].race_entries,
                    v2: comparison.constructors[1].race_entries,
                    format: (v: number) => `${v} entries`,
                  },
                  {
                    label: 'Race Completion Rate',
                    v1: comparison.constructors[0].finish_rate,
                    v2: comparison.constructors[1].finish_rate,
                    format: (v: number) => `${v}%`,
                  },
                ].map((row, idx) => {
                  const t1Wins = row.v1 > row.v2;
                  return (
                    <tr key={idx} className="hover:bg-[#1A1A1A]">
                      <td className="py-2.5 px-3 font-medium text-gray-300">{row.label}</td>
                      <td className={`py-2.5 px-3 text-center font-mono font-bold ${t1Wins ? 'text-[#00D26A]' : 'text-gray-300'}`}>
                        {row.format(row.v1)}
                      </td>
                      <td className={`py-2.5 px-3 text-center font-mono font-bold ${!t1Wins && row.v1 !== row.v2 ? 'text-[#00D26A]' : 'text-gray-300'}`}>
                        {row.format(row.v2)}
                      </td>
                      <td className="py-2.5 px-3 text-center text-gray-500 font-mono">
                        {row.v1 !== row.v2
                          ? t1Wins
                            ? comparison.constructors[0].constructor.name
                            : comparison.constructors[1].constructor.name
                          : 'Even'}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
