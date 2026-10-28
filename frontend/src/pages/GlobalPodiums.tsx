import { useState, useEffect } from 'react';
import {
  Award,
  Trophy,
  Globe,
  Medal,
  Search,
  Download,
} from 'lucide-react';
import KPICard from '../components/KPICard';
import ChartCard from '../components/ChartCard';
import FilterBar from '../components/FilterBar';
import PodiumDistributionChart from '../charts/PodiumDistributionChart';
import { useFilters } from '../hooks/useFilters';
import { fetchWithFallback, API_BASE_URL } from '../services/api';

export default function GlobalPodiums() {
  const { filters, setFilters, resetFilters } = useFilters();

  const [driverPodiums, setDriverPodiums] = useState<any[]>([]);
  const [teamPodiums, setTeamPodiums] = useState<any[]>([]);
  const [nationalities, setNationalities] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [searchQuery, setSearchQuery] = useState<string>('');

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      try {
        const queryParams = new URLSearchParams();
        if (filters.season) queryParams.set('season', String(filters.season));

        const queryStr = queryParams.toString() ? `?${queryParams.toString()}` : '';

        const [dData, tData, nData] = await Promise.all([
          fetchWithFallback<any[]>(`/podiums/leaderboard${queryStr}${queryStr ? '&' : '?'}limit=50`, 'podiums_leaderboard'),
          fetchWithFallback<any[]>(`/podiums/constructors${queryStr}`, 'podiums_constructors'),
          fetchWithFallback<any[]>(`/podiums/nationalities${queryStr}`, 'podiums_nationalities'),
        ]);

        setDriverPodiums(dData);
        setTeamPodiums(tData);
        setNationalities(nData);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [filters.season]);

  const handleExport = () => {
    window.open(`${API_BASE_URL}/export/results`, '_blank');
  };

  const filteredDriverPodiums = driverPodiums.filter((d) =>
    `${d.driver_name} ${d.constructor_name || ''} ${d.nationality || ''}`
      .toLowerCase()
      .includes(searchQuery.toLowerCase())
  );

  const totalPodiumsCount = driverPodiums.reduce((acc, d) => acc + (d.total_podiums || 0), 0);

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="border-b border-[#222] pb-4">
        <h1 className="text-xl md:text-2xl font-black text-white tracking-tight flex items-center gap-2">
          GLOBAL PODIUM INTELLIGENCE
          <span className="text-xs px-2.5 py-0.5 rounded-full bg-[#FFD700]/20 text-[#FFD700] font-mono font-bold">
            P1 / P2 / P3 RECORDS
          </span>
        </h1>
        <p className="text-xs md:text-sm text-gray-400 mt-0.5">
          Comprehensive podium classification, driver leaderboards, constructor distribution, and nationality achievements.
        </p>
      </div>

      <FilterBar
        filters={filters}
        onChange={setFilters}
        onReset={resetFilters}
        onExport={handleExport}
        hideConstructor
        hideDriver
      />

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <KPICard
          icon={Trophy}
          value={driverPodiums[0]?.driver_name || '—'}
          label="All-Time Podium Leader"
          description={`${driverPodiums[0]?.total_podiums || 0} top 3 finishes`}
          color="#FFD700"
          index={0}
        />
        <KPICard
          icon={Award}
          value={teamPodiums[0]?.name || '—'}
          label="Leading Constructor"
          description={`${teamPodiums[0]?.total_podiums || 0} team podiums`}
          color="#FF8000"
          index={1}
        />
        <KPICard
          icon={Globe}
          value={nationalities[0]?.nationality || '—'}
          label="Top Sovereign Nation"
          description={`${nationalities[0]?.podiums || 0} podium finishes`}
          color="#3671C6"
          index={2}
        />
        <KPICard
          icon={Medal}
          value={driverPodiums.length}
          label="Different Podium Finishers"
          description="Drivers on the podium"
          color="#00D26A"
          index={3}
        />
      </div>

      {/* Main Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChartCard
          title="Constructor Podium Distribution (P1, P2, P3)"
          description="First, second, and third-place trophies by Formula 1 constructor"
          loading={loading}
        >
          <PodiumDistributionChart data={teamPodiums} limit={8} />
        </ChartCard>

        <ChartCard
          title="Podiums by Driver Nationality"
          description="Total podium appearances grouped by driver country of origin"
          loading={loading}
        >
          <div className="space-y-3 py-2">
            {nationalities.slice(0, 7).map((nat, idx) => (
              <div
                key={nat.nationality}
                className="flex items-center justify-between p-3 rounded-lg bg-[#181818] border border-[#262626]"
              >
                <div className="flex items-center gap-3">
                  <span className="text-xs font-mono font-bold text-gray-500 w-4">{idx + 1}.</span>
                  <span className="text-xs font-bold text-white">{nat.nationality}</span>
                </div>
                <div className="flex items-center gap-4 text-xs font-mono">
                  <span className="text-[#FFD700] font-bold">{nat.wins} Wins</span>
                  <span className="text-gray-300 font-bold">{nat.podiums} Podiums</span>
                </div>
              </div>
            ))}
          </div>
        </ChartCard>
      </div>

      {/* Searchable Driver Podium Records Table */}
      <div className="bg-[#141414] border border-[#262626] rounded-xl p-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-4">
          <div className="flex items-center gap-2">
            <Trophy size={16} className="text-[#FFD700]" />
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">
              Formula 1 Driver Podium Leaderboard
            </h3>
          </div>
          <div className="relative w-full md:w-64">
            <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
            <input
              type="text"
              placeholder="Search driver or team..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-[#1C1C1C] border border-[#333] rounded-lg pl-8 pr-3 py-1.5 text-xs text-white focus:outline-none focus:border-[#E10600]"
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-[#2A2A2A] text-gray-400">
                <th className="py-2.5 px-3">Rank</th>
                <th className="py-2.5 px-3">Driver</th>
                <th className="py-2.5 px-3">Nationality</th>
                <th className="py-2.5 px-3 text-center">P1 (Wins)</th>
                <th className="py-2.5 px-3 text-center">P2 (2nd)</th>
                <th className="py-2.5 px-3 text-center">P3 (3rd)</th>
                <th className="py-2.5 px-3 text-center">Total Podiums</th>
                <th className="py-2.5 px-3 text-center">Podium %</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#1F1F1F]">
              {filteredDriverPodiums.map((d, idx) => (
                <tr key={d.driver_id || idx} className="hover:bg-[#1A1A1A]">
                  <td className="py-2.5 px-3 font-mono text-gray-500 font-bold">{idx + 1}</td>
                  <td className="py-2.5 px-3 font-bold text-white">{d.driver_name}</td>
                  <td className="py-2.5 px-3 text-gray-400">{d.nationality}</td>
                  <td className="py-2.5 px-3 text-center font-mono font-bold text-[#FFD700]">
                    {d.wins}
                  </td>
                  <td className="py-2.5 px-3 text-center font-mono text-[#C0C0C0] font-bold">
                    {d.seconds}
                  </td>
                  <td className="py-2.5 px-3 text-center font-mono text-[#CD7F32] font-bold">
                    {d.thirds}
                  </td>
                  <td className="py-2.5 px-3 text-center font-mono font-black text-white text-sm">
                    {d.total_podiums}
                  </td>
                  <td className="py-2.5 px-3 text-center font-mono text-[#00D26A]">
                    {d.podium_rate ? `${d.podium_rate}%` : '—'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
