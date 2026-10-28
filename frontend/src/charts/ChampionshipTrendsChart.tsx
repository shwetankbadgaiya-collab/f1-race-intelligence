import { useState, useMemo } from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
} from 'recharts';
import { getTeamColor } from '../utils/colors';

interface TrendItem {
  season: number;
  constructor: string;
  points: number;
  position?: number;
  wins?: number;
}

interface ChampionshipTrendsChartProps {
  data: TrendItem[];
}

export default function ChampionshipTrendsChart({ data }: ChampionshipTrendsChartProps) {
  // Pivot data so each season has a single object with key-value pairs for each constructor
  const { chartData, constructors } = useMemo(() => {
    const constSet = new Set<string>();
    const seasonMap: Record<number, Record<string, number>> = {};

    data.forEach((item) => {
      constSet.add(item.constructor);
      if (!seasonMap[item.season]) {
        seasonMap[item.season] = { season: item.season };
      }
      seasonMap[item.season][item.constructor] = item.points;
    });

    const sortedSeasons = Object.keys(seasonMap)
      .map(Number)
      .sort((a, b) => a - b);

    const formatted = sortedSeasons.map((s) => seasonMap[s]);
    return {
      chartData: formatted,
      constructors: Array.from(constSet),
    };
  }, [data]);

  // Default focus on top 4 teams
  const defaultTop = useMemo(() => {
    return constructors.filter(
      (c) =>
        c.includes('Red Bull') ||
        c.includes('Mercedes') ||
        c.includes('Ferrari') ||
        c.includes('McLaren')
    );
  }, [constructors]);

  const [activeTeams, setActiveTeams] = useState<string[]>([]);

  // Initialize or fallback active teams
  const selectedTeams = activeTeams.length > 0 ? activeTeams : defaultTop.length > 0 ? defaultTop : constructors.slice(0, 5);

  const toggleTeam = (team: string) => {
    if (selectedTeams.includes(team)) {
      if (selectedTeams.length > 1) {
        setActiveTeams(selectedTeams.filter((t) => t !== team));
      }
    } else {
      setActiveTeams([...selectedTeams, team]);
    }
  };

  if (!chartData || chartData.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-500 text-xs">
        No championship trend data available for current selection.
      </div>
    );
  }

  return (
    <div className="w-full">
      {/* Team Visibility Toggles */}
      <div className="flex flex-wrap gap-1.5 mb-4">
        {constructors.slice(0, 10).map((team) => {
          const isSelected = selectedTeams.includes(team);
          const color = getTeamColor(team);
          return (
            <button
              key={team}
              onClick={() => toggleTeam(team)}
              className={`px-2.5 py-1 rounded-md text-xs font-medium transition-all flex items-center gap-1.5 ${
                isSelected
                  ? 'bg-neutral-800 text-white border border-[#444]'
                  : 'bg-transparent text-gray-500 hover:text-gray-300 border border-transparent'
              }`}
            >
              <span
                className="w-2 h-2 rounded-full"
                style={{ backgroundColor: isSelected ? color : '#555' }}
              />
              <span>{team}</span>
            </button>
          );
        })}
      </div>

      <div className="h-[360px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 10, right: 20, left: 0, bottom: 10 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#222" vertical={false} />
            <XAxis
              dataKey="season"
              stroke="#666"
              fontSize={11}
              tickLine={false}
              axisLine={{ stroke: '#333' }}
            />
            <YAxis
              stroke="#666"
              fontSize={11}
              tickLine={false}
              axisLine={{ stroke: '#333' }}
              tickFormatter={(v) => `${v} pts`}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#181818',
                borderColor: '#333',
                borderRadius: '8px',
                fontSize: '12px',
                color: '#fff',
              }}
              formatter={(value: any, name: any) => [`${value} Points`, name]}
              labelFormatter={(label) => `Season ${label}`}
            />
            <Legend
              wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }}
              formatter={(val) => <span className="text-gray-300">{val}</span>}
            />
            {selectedTeams.map((team) => (
              <Line
                key={team}
                type="monotone"
                dataKey={team}
                name={team}
                stroke={getTeamColor(team)}
                strokeWidth={2.5}
                dot={{ r: 3, fill: getTeamColor(team) }}
                activeDot={{ r: 6, stroke: '#fff', strokeWidth: 1.5 }}
                connectNulls
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
