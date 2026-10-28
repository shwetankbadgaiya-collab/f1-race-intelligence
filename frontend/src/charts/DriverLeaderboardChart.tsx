import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Cell,
} from 'recharts';
import { getTeamColor } from '../utils/colors';

interface DriverLeaderboardItem {
  driver_id: string;
  driver_name: string;
  code?: string;
  constructor_name?: string;
  points: number;
  wins: number;
  podiums: number;
  avg_finish_position?: number;
}

interface DriverLeaderboardChartProps {
  data: DriverLeaderboardItem[];
  limit?: number;
}

export default function DriverLeaderboardChart({ data, limit = 10 }: DriverLeaderboardChartProps) {
  const chartData = data.slice(0, limit);

  if (!chartData || chartData.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-500 text-xs">
        No driver standings available.
      </div>
    );
  }

  return (
    <div className="w-full h-[360px]">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={chartData}
          layout="vertical"
          margin={{ top: 5, right: 30, left: 40, bottom: 5 }}
        >
          <XAxis
            type="number"
            stroke="#666"
            fontSize={11}
            tickLine={false}
            axisLine={{ stroke: '#333' }}
            tickFormatter={(v) => `${v} pts`}
          />
          <YAxis
            type="category"
            dataKey="driver_name"
            stroke="#999"
            fontSize={11}
            tickLine={false}
            axisLine={{ stroke: '#333' }}
            width={110}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#181818',
              borderColor: '#333',
              borderRadius: '8px',
              fontSize: '12px',
              color: '#fff',
            }}
            formatter={(value: any, name: any, item: any) => [
              `${value} Points (${item.payload.wins} Wins, ${item.payload.podiums} Podiums)`,
              item.payload.constructor_name || 'Driver',
            ]}
          />
          <Bar dataKey="points" radius={[0, 4, 4, 0]}>
            {chartData.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={getTeamColor(entry.constructor_name || 'default')}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
