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

interface DNFTrendItem {
  season: number;
  total_entries: number;
  classified: number;
  dnfs: number;
  completion_rate: number;
  dnf_rate: number;
}

interface DNFTrendsChartProps {
  data: DNFTrendItem[];
}

export default function DNFTrendsChart({ data }: DNFTrendsChartProps) {
  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-500 text-xs">
        No DNF trends telemetry available.
      </div>
    );
  }

  return (
    <div className="w-full h-[320px]">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 10 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#222" vertical={false} />
          <XAxis
            dataKey="season"
            stroke="#666"
            fontSize={11}
            tickLine={false}
            axisLine={{ stroke: '#333' }}
          />
          <YAxis
            yAxisId="left"
            stroke="#666"
            fontSize={11}
            tickLine={false}
            axisLine={{ stroke: '#333' }}
            tickFormatter={(v) => `${v}`}
          />
          <YAxis
            yAxisId="right"
            orientation="right"
            stroke="#666"
            fontSize={11}
            tickLine={false}
            axisLine={{ stroke: '#333' }}
            tickFormatter={(v) => `${v}%`}
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
          <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
          <Line
            yAxisId="left"
            type="monotone"
            dataKey="dnfs"
            name="Total DNFs"
            stroke="#E10600"
            strokeWidth={2.5}
            dot={{ r: 3, fill: '#E10600' }}
          />
          <Line
            yAxisId="right"
            type="monotone"
            dataKey="dnf_rate"
            name="DNF Rate (%)"
            stroke="#FFB800"
            strokeWidth={2}
            strokeDasharray="4 4"
            dot={{ r: 2, fill: '#FFB800' }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
