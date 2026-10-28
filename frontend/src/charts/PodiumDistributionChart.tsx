import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
} from 'recharts';

interface PodiumItem {
  driver_name?: string;
  name?: string;
  wins?: number;
  p1?: number;
  seconds?: number;
  p2?: number;
  thirds?: number;
  p3?: number;
  total_podiums?: number;
}

interface PodiumDistributionChartProps {
  data: PodiumItem[];
  limit?: number;
}

export default function PodiumDistributionChart({ data, limit = 8 }: PodiumDistributionChartProps) {
  const chartData = data.slice(0, limit).map((d) => ({
    name: d.driver_name || d.name || 'Unknown',
    p1: d.wins !== undefined ? d.wins : d.p1 || 0,
    p2: d.seconds !== undefined ? d.seconds : d.p2 || 0,
    p3: d.thirds !== undefined ? d.thirds : d.p3 || 0,
    total: d.total_podiums || ((d.wins || 0) + (d.seconds || 0) + (d.thirds || 0)),
  }));

  if (!chartData || chartData.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-500 text-xs">
        No podium telemetry recorded.
      </div>
    );
  }

  return (
    <div className="w-full h-[320px]">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={chartData}
          margin={{ top: 10, right: 20, left: 0, bottom: 20 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#222" vertical={false} />
          <XAxis
            dataKey="name"
            stroke="#888"
            fontSize={11}
            tickLine={false}
            axisLine={{ stroke: '#333' }}
            interval={0}
            angle={-25}
            textAnchor="end"
          />
          <YAxis
            stroke="#666"
            fontSize={11}
            tickLine={false}
            axisLine={{ stroke: '#333' }}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#181818',
              borderColor: '#333',
              borderRadius: '8px',
              fontSize: '12px',
              color: '#fff',
            }}
          />
          <Legend
            verticalAlign="top"
            align="right"
            wrapperStyle={{ fontSize: '11px', paddingBottom: '10px' }}
          />
          <Bar dataKey="p1" name="P1 (Wins)" stackId="a" fill="#FFD700" radius={[0, 0, 0, 0]} />
          <Bar dataKey="p2" name="P2 (2nd)" stackId="a" fill="#C0C0C0" radius={[0, 0, 0, 0]} />
          <Bar dataKey="p3" name="P3 (3rd)" stackId="a" fill="#CD7F32" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
