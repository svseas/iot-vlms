import React from 'react';
import { Row, Col, Card, Statistic } from 'antd';
import {
  ThunderboltOutlined,
  CloudOutlined,
  BulbOutlined,
  DashboardOutlined,
} from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import type { MetricItem } from '../../types';

interface StationMetricsProps {
  telemetry: MetricItem[];
}

const StationMetrics: React.FC<StationMetricsProps> = ({ telemetry }) => {
  const { t } = useTranslation();
  const getLatestValue = (metricType: string) => {
    if (!Array.isArray(telemetry)) return null;
    const record = telemetry.find((item) => item.metric_type === metricType);
    return record ? { value: record.value } : null;
  };

  const batterySOC = getLatestValue('battery_soc');
  const solarPower = getLatestValue('solar_power');
  const temperature = getLatestValue('temperature');
  const humidity = getLatestValue('humidity');
  const windSpeed = getLatestValue('wind_speed');
  const lightStatus = getLatestValue('light_status');
  const pressure = getLatestValue('pressure');
  const batteryVoltage = getLatestValue('battery_voltage');

  return (
    <Row gutter={[16, 16]}>
      <Col xs={12} sm={8} md={6} lg={4}>
        <Card size="small">
          <Statistic
            title={t('metrics.batterySOC')}
            value={batterySOC?.value || 0}
            suffix="%"
            prefix={<ThunderboltOutlined />}
            styles={{
              content: { color: (batterySOC?.value || 0) > 50 ? '#52c41a' : '#faad14' },
            }}
          />
        </Card>
      </Col>
      <Col xs={12} sm={8} md={6} lg={4}>
        <Card size="small">
          <Statistic
            title={t('metrics.batteryVoltage')}
            value={batteryVoltage?.value || 0}
            suffix="V"
            precision={1}
            styles={{ content: { color: '#1890ff' } }}
          />
        </Card>
      </Col>
      <Col xs={12} sm={8} md={6} lg={4}>
        <Card size="small">
          <Statistic
            title={t('metrics.solarPower')}
            value={solarPower?.value || 0}
            suffix="W"
            precision={1}
            styles={{ content: { color: '#faad14' } }}
          />
        </Card>
      </Col>
      <Col xs={12} sm={8} md={6} lg={4}>
        <Card size="small">
          <Statistic
            title={t('metrics.temperature')}
            value={temperature?.value || 0}
            suffix="°C"
            prefix={<CloudOutlined />}
            precision={1}
          />
        </Card>
      </Col>
      <Col xs={12} sm={8} md={6} lg={4}>
        <Card size="small">
          <Statistic
            title={t('metrics.humidity')}
            value={humidity?.value || 0}
            suffix="%"
            precision={1}
            styles={{ content: { color: '#1890ff' } }}
          />
        </Card>
      </Col>
      <Col xs={12} sm={8} md={6} lg={4}>
        <Card size="small">
          <Statistic
            title={t('metrics.windSpeed')}
            value={windSpeed?.value || 0}
            suffix="km/h"
            precision={1}
            styles={{ content: { color: '#13c2c2' } }}
          />
        </Card>
      </Col>
      <Col xs={12} sm={8} md={6} lg={4}>
        <Card size="small">
          <Statistic
            title={t('metrics.pressure')}
            value={pressure?.value || 0}
            suffix="hPa"
            prefix={<DashboardOutlined />}
            precision={0}
          />
        </Card>
      </Col>
      <Col xs={12} sm={8} md={6} lg={4}>
        <Card size="small">
          <Statistic
            title={t('metrics.lightStatus')}
            value={lightStatus?.value === 1 ? t('common.on') : t('common.off')}
            prefix={<BulbOutlined />}
            styles={{
              content: { color: lightStatus?.value === 1 ? '#52c41a' : '#8c8c8c' },
            }}
          />
        </Card>
      </Col>
    </Row>
  );
};

export default StationMetrics;
