import React from 'react';
import { Card, Progress, Typography } from 'antd';

const { Text } = Typography;

interface GaugeChartProps {
  title: string;
  value: number;
  max?: number;
  unit?: string;
  thresholds?: {
    warning: number;
    danger: number;
  };
  size?: number;
}

const GaugeChart: React.FC<GaugeChartProps> = ({
  title,
  value,
  max = 100,
  unit = '%',
  thresholds = { warning: 50, danger: 25 },
  size = 120,
}) => {
  const percent = Math.min(100, (value / max) * 100);

  const getColor = () => {
    if (percent <= thresholds.danger) return '#ff4d4f';
    if (percent <= thresholds.warning) return '#faad14';
    return '#52c41a';
  };

  return (
    <Card size="small" style={{ textAlign: 'center' }}>
      <Progress
        type="dashboard"
        percent={percent}
        strokeColor={getColor()}
        size={size}
        format={() => (
          <div>
            <div style={{ fontSize: 24, fontWeight: 'bold', color: getColor() }}>
              {value.toFixed(1)}
            </div>
            <div style={{ fontSize: 12, color: '#8c8c8c' }}>{unit}</div>
          </div>
        )}
      />
      <Text strong style={{ display: 'block', marginTop: 8 }}>
        {title}
      </Text>
    </Card>
  );
};

export default GaugeChart;
