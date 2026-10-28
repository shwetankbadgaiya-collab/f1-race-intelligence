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

interface DriverContribution {
  constructor: string;
  driver1Name: string;
  driver1Points: number;
  driver2Name: string;
  driver2Points: number;
}

interface PointsDistributionChartProps {
  data: DriverContribution[];
}

export default function PointsDistributionChart({ data }: PointsDistributionChartProps) {
  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-500 text-xs">
        No driver contribution telemetry available.
      </div>
    );
  }

  return (
    <div className="w-full h-[320px]">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#222" vertical={false} />
          <XAxis
            dataKey="constructor"
            stroke="#888"
            fontSize={11}
            tickLine={false}
            axisLine={{ stroke: '#333' }}
          />
          <YAxis stroke="#666" fontSize={11} tickLine={false} axisLine={{ stroke: '#333' }} />
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
          <Bar dataKey="driver1Points" name="Lead Driver Points" stackId="a" fill="#E10600" radius={[0, 0, 0, 0]} />
          <Bar dataKey="driver2Points" name="Second Driver Points" stackId="a" fill="#3671C6" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
