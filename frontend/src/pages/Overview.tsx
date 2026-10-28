import { useEffect, useState } from 'react';
import {
  Flag,
  Users,
  Shield,
  MapPin,
  Award,
  CheckCircle2,
  AlertTriangle,
  Trophy,
} from 'lucide-react';
import KPICard from '../components/KPICard';
import ChartCard from '../components/ChartCard';
import FilterBar from '../components/FilterBar';
import InsightsPanel from '../components/InsightsPanel';
import ChampionshipTrendsChart from '../charts/ChampionshipTrendsChart';
import DriverLeaderboardChart from '../charts/DriverLeaderboardChart';
import RaceCompletionChart from '../charts/RaceCompletionChart';
import PodiumDistributionChart from '../charts/PodiumDistributionChart';
import { useFilters } from '../hooks/useFilters';
import { exportToCsv } from '../utils/export';
import { fetchWithFallback, API_BASE_URL } from '../services/api';

interface OverviewStats {
  total_races: number;
  total_drivers: number;
  total_constructors: number;
  total_circuits: number;
  total_podiums: number;
  classified_finishes: number;
  unclassified_finishes: number;
  season_range?: string;
}

export default function Overview() {
  const { filters, setFilters, resetFilters } = useFilters();

  const [stats, setStats] = useState<OverviewStats | null>(null);
  const [trends, setTrends] = useState<any[]>([]);
  const [drivers, setDrivers] = useState<any[]>([]);
  const [podiums, setPodiums] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      setError(null);
      try {
        const queryParams = new URLSearchParams();
        if (filters.season) queryParams.set('season', String(filters.season));

        const queryStr = queryParams.toString() ? `?${queryParams.toString()}` : '';

        const [ovData, trendData, leadData, podData] = await Promise.all([
          fetchWithFallback<OverviewStats>(`/overview${queryStr}`, 'overview'),
          fetchWithFallback<any[]>(`/championship-trends${queryStr}`, 'championship_trends'),
          fetchWithFallback<any[]>(`/drivers/leaderboard${queryStr}${queryStr ? '&' : '?'}limit=10`, 'driver_leaderboard'),
          fetchWithFallback<any[]>(`/podiums/leaderboard${queryStr}${queryStr ? '&' : '?'}limit=8`, 'podiums_leaderboard'),
        ]);

        setStats(ovData);
        setTrends(trendData);
        setDrivers(leadData);
        setPodiums(podData);
      } catch (err: any) {
        setError(err.message || 'Error loading analytics telemetry');
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, [filters.season]);

  const handleExport = () => {
    window.open(`${API_BASE_URL}/export/results`, '_blank');
  };

  const topDriver = drivers.length > 0 ? drivers[0] : null;

  return (
    <div className="space-y-6">
      {/* Title & Context */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-2 border-b border-[#222] pb-4">
        <div>
          <h1 className="text-xl md:text-2xl font-black text-white tracking-tight flex items-center gap-2">
            RACE INTELLIGENCE OVERVIEW
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-[#E10600]/20 text-[#E10600] font-mono font-bold">
              2010–2026
            </span>
          </h1>
          <p className="text-xs md:text-sm text-gray-400 mt-0.5">
            Macro telemetry, championship trajectories, completion rates & driver performance records.
          </p>
        </div>
      </div>

      {/* Global Filter Bar */}
      <FilterBar
        filters={filters}
        onChange={setFilters}
        onReset={resetFilters}
        onExport={handleExport}
        hideConstructor
        hideDriver
      />

      {/* AI / Automated Insights Banner */}
      <InsightsPanel />

      {/* KPI Cards Row */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
        <KPICard
          icon={Flag}
          value={stats?.total_races || (loading ? '—' : 0)}
          label="Grands Prix"
          description="Races in dataset"
          color="#E10600"
          index={0}
        />
        <KPICard
          icon={Users}
          value={stats?.total_drivers || (loading ? '—' : 0)}
          label="Drivers"
          description="Participated"
          color="#3671C6"
          index={1}
        />
        <KPICard
          icon={Shield}
          value={stats?.total_constructors || (loading ? '—' : 0)}
          label="Constructors"
          description="Teams entered"
          color="#FF8000"
          index={2}
        />
        <KPICard
          icon={MapPin}
          value={stats?.total_circuits || (loading ? '—' : 0)}
          label="Circuits"
          description="Distinct venues"
          color="#229971"
          index={3}
        />
        <KPICard
          icon={Award}
          value={stats?.total_podiums || (loading ? '—' : 0)}
          label="Podiums"
          description="Top 3 finishes"
          color="#FFD700"
          index={4}
        />
        <KPICard
          icon={CheckCircle2}
          value={
            stats
              ? `${(
                  (stats.classified_finishes /
                    (stats.classified_finishes + stats.unclassified_finishes)) *
                  100
                ).toFixed(1)}%`
              : loading
              ? '—'
              : '0%'
          }
          label="Finish Rate"
          description={`${stats?.classified_finishes || 0} classified`}
          color="#00D26A"
          index={5}
        />
      </div>

      {/* Season Highlights Banner if available */}
      {topDriver && (
        <div className="bg-[#141414] border border-[#262626] rounded-xl p-4 flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-lg bg-[#FFD700]/15 text-[#FFD700]">
              <Trophy size={22} />
            </div>
            <div>
              <span className="text-[10px] uppercase font-bold tracking-widest text-[#FFD700]">
                {filters.season ? `${filters.season} Season Leader` : 'Historical Leading Performer'}
              </span>
              <h3 className="text-base font-bold text-white">
                {topDriver.driver_name}{' '}
                <span className="text-xs font-normal text-gray-400">
                  ({topDriver.constructor_name})
                </span>
              </h3>
            </div>
          </div>
          <div className="flex items-center gap-6 text-xs">
            <div>
              <span className="text-gray-500 block text-[10px] uppercase">Championship Points</span>
              <span className="text-white font-mono font-bold text-sm">
                {topDriver.points.toLocaleString()} pts
              </span>
            </div>
            <div>
              <span className="text-gray-500 block text-[10px] uppercase">Victories</span>
              <span className="text-[#00D26A] font-mono font-bold text-sm">
                {topDriver.wins} Wins
              </span>
            </div>
            <div>
              <span className="text-gray-500 block text-[10px] uppercase">Podiums</span>
              <span className="text-[#FFD700] font-mono font-bold text-sm">
                {topDriver.podiums} Podiums
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Main Visualizations Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* A. Championship Points Trend */}
        <ChartCard
          title="Constructor Championship Points Trend"
          description="Comparative trajectory for Red Bull, Mercedes, Ferrari, McLaren (2010–2024)"
          loading={loading}
          error={error}
          isEmpty={trends.length === 0}
        >
          <ChampionshipTrendsChart data={trends} />
        </ChartCard>

        {/* B. Driver Performance Leaderboard */}
        <ChartCard
          title="Driver Performance Leaderboard"
          description="Drivers ranked by championship points, wins, and podium finishes"
          loading={loading}
          error={error}
          isEmpty={drivers.length === 0}
        >
          <DriverLeaderboardChart data={drivers} limit={10} />
        </ChartCard>

        {/* C. Race Completion Overview */}
        <ChartCard
          title="Race Completion & Reliability Telemetry"
          description="Classified race finishes vs technical retirements and accident DNFs"
          loading={loading}
          error={error}
          isEmpty={!stats}
        >
          <RaceCompletionChart
            classified={stats?.classified_finishes || 0}
            dnf={stats?.unclassified_finishes || 0}
          />
        </ChartCard>

        {/* D. Podium Distribution */}
        <ChartCard
          title="Podium Finishes Distribution"
          description="First, second, and third place podium appearances"
          loading={loading}
          error={error}
          isEmpty={podiums.length === 0}
        >
          <PodiumDistributionChart data={podiums} limit={8} />
        </ChartCard>
      </div>
    </div>
  );
}
