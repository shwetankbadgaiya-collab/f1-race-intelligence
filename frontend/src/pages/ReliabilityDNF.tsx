import { useState, useEffect } from 'react';
import {
  AlertTriangle,
  CheckCircle2,
  Flame,
  Wrench,
  Percent,
} from 'lucide-react';
import KPICard from '../components/KPICard';
import ChartCard from '../components/ChartCard';
import FilterBar from '../components/FilterBar';
import DNFTrendsChart from '../charts/DNFTrendsChart';
import FailureCategoryChart from '../charts/FailureCategoryChart';
import { useFilters } from '../hooks/useFilters';
import { fetchWithFallback } from '../services/api';

export default function ReliabilityDNF() {
  const { filters, setFilters, resetFilters } = useFilters();

  const [trends, setTrends] = useState<any[]>([]);
  const [reasons, setReasons] = useState<any[]>([]);
  const [teamReliability, setTeamReliability] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      try {
        const queryParams = new URLSearchParams();
        if (filters.season) queryParams.set('season', String(filters.season));

        const queryStr = queryParams.toString() ? `?${queryParams.toString()}` : '';

        const [tData, rData, cData] = await Promise.all([
          fetchWithFallback<any[]>(`/reliability/trends${queryStr}`, 'reliability_trends'),
          fetchWithFallback<any[]>(`/reliability/dnf-reasons${queryStr}`, 'dnf_reasons'),
          fetchWithFallback<any[]>(`/reliability/constructors${queryStr}`, 'reliability_constructors'),
        ]);

        setTrends(tData);
        setReasons(rData);
        setTeamReliability(cData);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [filters.season]);

  const totalEntries = trends.reduce((acc, t) => acc + (t.total_entries || 0), 0);
  const totalDnfs = trends.reduce((acc, t) => acc + (t.dnfs || 0), 0);
  const overallDnfRate = totalEntries > 0 ? ((totalDnfs / totalEntries) * 100).toFixed(1) : '0';
  const overallCompletionRate = totalEntries > 0 ? (100 - Number(overallDnfRate)).toFixed(1) : '100';

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="border-b border-[#222] pb-4">
        <h1 className="text-xl md:text-2xl font-black text-white tracking-tight flex items-center gap-2">
          RELIABILITY & RETIREMENT TELEMETRY
          <span className="text-xs px-2.5 py-0.5 rounded-full bg-[#E10600]/20 text-[#E10600] font-mono font-bold">
            DNF & FAILURE CATEGORIES
          </span>
        </h1>
        <p className="text-xs md:text-sm text-gray-400 mt-0.5">
          Power unit reliability, collision rates, mechanical failure distributions, and team completion percentages.
        </p>
      </div>

      <FilterBar
        filters={filters}
        onChange={setFilters}
        onReset={resetFilters}
        hideConstructor
        hideDriver
      />

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <KPICard
          icon={CheckCircle2}
          value={`${overallCompletionRate}%`}
          label="Race Completion Rate"
          description={`${totalEntries - totalDnfs} classified starts`}
          color="#00D26A"
          index={0}
        />
        <KPICard
          icon={AlertTriangle}
          value={`${overallDnfRate}%`}
          label="Average DNF Rate"
          description="Retirements per race start"
          color="#FFB800"
          index={1}
        />
        <KPICard
          icon={Flame}
          value={totalDnfs}
          label="Total Recorded DNFs"
          description="Mechanical & incident retirements"
          color="#E10600"
          index={2}
        />
        <KPICard
          icon={Wrench}
          value={reasons.length}
          label="Distinct Failure Modes"
          description="Cataloged telemetry statuses"
          color="#3671C6"
          index={3}
        />
      </div>

      {/* Main Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChartCard
          title="Season-by-Season DNF Rates & Trends"
          description="Annual retirement count and percentage progression"
          loading={loading}
        >
          <DNFTrendsChart data={trends} />
        </ChartCard>

        <ChartCard
          title="Recorded Technical & Incident Failure Reasons"
          description="Categorized failure frequencies (Engine, Transmission, Accident, Brakes)"
          loading={loading}
        >
          <FailureCategoryChart data={reasons} />
        </ChartCard>
      </div>

      {/* Constructor Reliability Ranking Table */}
      <div className="bg-[#141414] border border-[#262626] rounded-xl p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Wrench size={16} className="text-[#00D26A]" />
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">
              Constructor Reliability & Completion Leaderboard
            </h3>
          </div>
          <span className="text-xs text-gray-400 font-mono">Ranked by Completion %</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-[#2A2A2A] text-gray-400">
                <th className="py-2.5 px-3">Constructor</th>
                <th className="py-2.5 px-3 text-center">Total Starts</th>
                <th className="py-2.5 px-3 text-center">Classified Finishes</th>
                <th className="py-2.5 px-3 text-center">Total DNFs</th>
                <th className="py-2.5 px-3 text-center">Completion Rate</th>
                <th className="py-2.5 px-3 text-center">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#1F1F1F]">
              {teamReliability.map((team) => (
                <tr key={team.constructor_id} className="hover:bg-[#1A1A1A]">
                  <td className="py-2.5 px-3 font-semibold text-white">{team.name}</td>
                  <td className="py-2.5 px-3 text-center font-mono text-gray-300">
                    {team.total_entries}
                  </td>
                  <td className="py-2.5 px-3 text-center font-mono text-[#00D26A] font-bold">
                    {team.classified}
                  </td>
                  <td className="py-2.5 px-3 text-center font-mono text-[#E10600]">
                    {team.dnf_count}
                  </td>
                  <td className="py-2.5 px-3 text-center font-mono font-bold text-white">
                    {team.finish_rate}%
                  </td>
                  <td className="py-2.5 px-3 text-center">
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        team.finish_rate >= 85
                          ? 'bg-[#00D26A]/20 text-[#00D26A]'
                          : team.finish_rate >= 75
                          ? 'bg-[#FFB800]/20 text-[#FFB800]'
                          : 'bg-[#E10600]/20 text-[#E10600]'
                      }`}
                    >
                      {team.finish_rate >= 85 ? 'High' : team.finish_rate >= 75 ? 'Moderate' : 'At Risk'}
                    </span>
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
