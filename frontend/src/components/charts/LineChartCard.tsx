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
} from 'recharts';

interface DataPoint {
  time: string;
  value: number;
}

interface LineChartCardProps {
  title: string;
  data: DataPoint[];
  color?: string;
  unit?: string;
  height?: number;
  yDomain?: [number | 'auto', number | 'auto'];
}

const LineChartCard: React.FC<LineChartCardProps> = ({
  title,
  data,
  color = '#1890ff',
  unit = '',
  height = 250,
  yDomain = ['auto', 'auto'],
}) => {
  return (
    <Card title={title} size="small">
      <ResponsiveContainer width="100%" height={height}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="time" fontSize={12} />
          <YAxis domain={yDomain} fontSize={12} />
          <Tooltip
            formatter={(value: number) => [`${value}${unit}`, title.split(' ')[0]]}
          />
          <Line
            type="monotone"
            dataKey="value"
            stroke={color}
            strokeWidth={2}
            dot={false}
            animationDuration={300}
          />
        </LineChart>
      </ResponsiveContainer>
    </Card>
  );
};

export default LineChartCard;
