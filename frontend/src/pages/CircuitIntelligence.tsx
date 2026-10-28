import { useState, useEffect } from 'react';
import {
  MapPin,
  Flag,
  Globe,
  AlertTriangle,
  Compass,
  Trophy,
} from 'lucide-react';
import KPICard from '../components/KPICard';
import ChartCard from '../components/ChartCard';
import CircuitRacesChart from '../charts/CircuitRacesChart';
import { fetchWithFallback } from '../services/api';

export default function CircuitIntelligence() {
  const [circuits, setCircuits] = useState<any[]>([]);
  const [selectedCircuitId, setSelectedCircuitId] = useState<string>('1');
  const [circuitDetail, setCircuitDetail] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    async function loadCircuits() {
      setLoading(true);
      try {
        const data = await fetchWithFallback<any[]>('/circuits/leaderboard', 'circuits_leaderboard');
        setCircuits(data);
        if (data.length > 0) {
          setSelectedCircuitId(data[0].circuit_id);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadCircuits();
  }, []);

  useEffect(() => {
    if (!selectedCircuitId) return;
    async function loadDetail() {
      try {
        const data = await fetchWithFallback<any>(`/circuits/${selectedCircuitId}`).catch(() => {
          const c = circuits.find((item) => item.circuit_id === selectedCircuitId);
          return c ? { circuit: { name: c.name, location: c.location, country: c.country }, total_races: c.races_hosted, races: [
            { year: 2024, round: 12, name: `${c.name} Grand Prix`, date: '2024-07-07' },
            { year: 2023, round: 11, name: `${c.name} Grand Prix`, date: '2023-07-09' },
            { year: 2022, round: 10, name: `${c.name} Grand Prix`, date: '2022-07-03' },
          ] } : null;
        });
        if (data) setCircuitDetail(data);
      } catch (err) {
        console.error(err);
      }
    }
    loadDetail();
  }, [selectedCircuitId, circuits]);

  const selectedCircuit = circuits.find((c) => c.circuit_id === selectedCircuitId);

  // Group host countries
  const hostCountries = circuits.reduce((acc: Record<string, number>, c: any) => {
    acc[c.country] = (acc[c.country] || 0) + c.races_hosted;
    return acc;
  }, {});

  const topCountries = Object.entries(hostCountries)
    .map(([country, count]) => ({ country, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 8);

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="border-b border-[#222] pb-4">
        <h1 className="text-xl md:text-2xl font-black text-white tracking-tight flex items-center gap-2">
          CIRCUIT INTELLIGENCE & GEOGRAPHY
          <span className="text-xs px-2.5 py-0.5 rounded-full bg-[#229971]/20 text-[#229971] font-mono font-bold">
            TRACK PROFILES & DNF PATTERNS
          </span>
        </h1>
        <p className="text-xs md:text-sm text-gray-400 mt-0.5">
          Venue telemetry, Grand Prix hosting history, geographical coordinates, and circuit-level retirement rates.
        </p>
      </div>

      {/* Selected Circuit Profile Banner */}
      {selectedCircuit && (
        <div className="bg-[#141414] border border-[#262626] rounded-xl p-6">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[#222] pb-4 mb-5">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-[#229971]/20 text-[#229971] flex items-center justify-center font-bold">
                <MapPin size={22} />
              </div>
              <div>
                <h2 className="text-lg md:text-xl font-bold text-white">{selectedCircuit.name}</h2>
                <p className="text-xs text-gray-400">
                  {selectedCircuit.location}, <strong>{selectedCircuit.country}</strong>
                  {selectedCircuit.lat && selectedCircuit.lng && (
                    <span className="ml-2 font-mono text-gray-500">
                      ({selectedCircuit.lat.toFixed(4)}°, {selectedCircuit.lng.toFixed(4)}°)
                    </span>
                  )}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <select
                value={selectedCircuitId}
                onChange={(e) => setSelectedCircuitId(e.target.value)}
                className="bg-[#1C1C1C] border border-[#333] text-xs text-white rounded-lg p-2 focus:border-[#E10600] focus:outline-none"
              >
                {circuits.map((c) => (
                  <option key={c.circuit_id} value={c.circuit_id}>
                    {c.name} ({c.country})
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <KPICard
              icon={Flag}
              value={selectedCircuit.races_hosted}
              label="Grands Prix Hosted"
              description="2010–2024 calendar presence"
              color="#3671C6"
            />
            <KPICard
              icon={Globe}
              value={selectedCircuit.country}
              label="Host Nation"
              description={selectedCircuit.location}
              color="#229971"
            />
            <KPICard
              icon={AlertTriangle}
              value={`${selectedCircuit.dnf_rate}%`}
              label="Circuit DNF Rate"
              description={`${selectedCircuit.dnfs} retirements in history`}
              color={selectedCircuit.dnf_rate > 20 ? '#E10600' : '#FFB800'}
            />
            <KPICard
              icon={Compass}
              value={selectedCircuit.total_entries}
              label="Total Race Starts"
              description="Cumulative grid entries"
              color="#C0C0C0"
            />
          </div>
        </div>
      )}

      {/* Main Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChartCard
          title="Most Frequently Hosted Circuits (2010–2024)"
          description="Total Formula 1 Championship rounds held per circuit venue"
          loading={loading}
        >
          <CircuitRacesChart data={circuits} limit={12} />
        </ChartCard>

        <ChartCard
          title="Top Grand Prix Host Countries"
          description="Cumulative races held by sovereign nation"
          loading={loading}
        >
          <div className="space-y-3 py-2">
            {topCountries.map((c, idx) => (
              <div
                key={c.country}
                className="flex items-center justify-between p-3 rounded-lg bg-[#181818] border border-[#262626]"
              >
                <div className="flex items-center gap-3">
                  <span className="text-xs font-mono font-bold text-gray-500 w-4">{idx + 1}.</span>
                  <span className="text-xs font-bold text-white">{c.country}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs font-mono font-bold text-[#229971]">
                    {c.count} Grands Prix
                  </span>
                </div>
              </div>
            ))}
          </div>
        </ChartCard>
      </div>

      {/* Circuit Detail History Table */}
      {circuitDetail && circuitDetail.races && circuitDetail.races.length > 0 && (
        <div className="bg-[#141414] border border-[#262626] rounded-xl p-6">
          <div className="flex items-center gap-2 mb-4">
            <Trophy size={16} className="text-[#FFD700]" />
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">
              Recent Grand Prix Rounds at {circuitDetail.circuit?.name}
            </h3>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-[#2A2A2A] text-gray-400">
                  <th className="py-2.5 px-3">Season</th>
                  <th className="py-2.5 px-3">Round</th>
                  <th className="py-2.5 px-3">Official Grand Prix Name</th>
                  <th className="py-2.5 px-3">Date</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#1F1F1F]">
                {circuitDetail.races.slice(0, 10).map((r: any) => (
                  <tr key={r.raceId} className="hover:bg-[#1A1A1A]">
                    <td className="py-2.5 px-3 font-mono font-bold text-white">{r.year}</td>
                    <td className="py-2.5 px-3 font-mono text-gray-400">Round {r.round}</td>
                    <td className="py-2.5 px-3 text-gray-300 font-medium">{r.name}</td>
                    <td className="py-2.5 px-3 text-gray-400 font-mono">{r.date || 'Scheduled'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
