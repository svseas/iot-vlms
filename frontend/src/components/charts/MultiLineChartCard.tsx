import React from 'react';
import { Card } from 'antd';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';

interface SeriesConfig {
  dataKey: string;
  name: string;
  color: string;
}

interface MultiLineChartCardProps {
  title: string;
  data: Record<string, unknown>[];
  series: SeriesConfig[];
  xAxisKey?: string;
  height?: number;
  yDomain?: [number | 'auto', number | 'auto'];
  showLegend?: boolean;
}

const MultiLineChartCard: React.FC<MultiLineChartCardProps> = ({
  title,
  data,
  series,
  xAxisKey = 'time',
  height = 250,
  yDomain = ['auto', 'auto'],
  showLegend = true,
}) => {
  return (
    <Card title={title} size="small">
      <ResponsiveContainer width="100%" height={height}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey={xAxisKey} fontSize={12} />
          <YAxis domain={yDomain} fontSize={12} />
          <Tooltip />
          {showLegend && <Legend />}
          {series.map((s) => (
            <Line
              key={s.dataKey}
              type="monotone"
              dataKey={s.dataKey}
              name={s.name}
              stroke={s.color}
              strokeWidth={2}
              dot={false}
              animationDuration={300}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </Card>
  );
};

export default MultiLineChartCard;
