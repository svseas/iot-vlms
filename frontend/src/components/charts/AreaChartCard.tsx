import React from 'react';
import { Card } from 'antd';
import {
  AreaChart,
  Area,
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

interface AreaChartCardProps {
  title: string;
  data: DataPoint[];
  color?: string;
  unit?: string;
  height?: number;
  yDomain?: [number | 'auto', number | 'auto'];
  fillOpacity?: number;
}

const AreaChartCard: React.FC<AreaChartCardProps> = ({
  title,
  data,
  color = '#1890ff',
  unit = '',
  height = 250,
  yDomain = ['auto', 'auto'],
  fillOpacity = 0.3,
}) => {
  return (
    <Card title={title} size="small">
      <ResponsiveContainer width="100%" height={height}>
        <AreaChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="time" fontSize={12} />
          <YAxis domain={yDomain} fontSize={12} />
          <Tooltip
            formatter={(value: number) => [`${value}${unit}`, title.split(' ')[0]]}
          />
          <Area
            type="monotone"
            dataKey="value"
            stroke={color}
            fill={color}
            fillOpacity={fillOpacity}
            animationDuration={300}
          />
        </AreaChart>
      </ResponsiveContainer>
    </Card>
  );
};

export default AreaChartCard;
