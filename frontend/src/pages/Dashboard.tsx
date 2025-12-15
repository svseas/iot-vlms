import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Row, Col, Typography, Spin } from 'antd';
import {
  EnvironmentOutlined,
  AlertOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  ThunderboltOutlined,
  CloudOutlined,
} from '@ant-design/icons';
import { useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { stationsApi } from '../services/stations';
import { alertsApi } from '../services/alerts';
import { telemetryApi } from '../services/telemetry';
import { StatsCard, AlertsTable, StationsTable } from '../components/dashboard';
import {
  LineChartCard,
  AreaChartCard,
  PieChartCard,
  BarChartCard,
} from '../components/charts';
import type { TelemetryRecord } from '../types';
import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';

dayjs.extend(relativeTime);

const { Title } = Typography;

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const { t } = useTranslation();

  const { data: stationsData, isLoading: stationsLoading } = useQuery({
    queryKey: ['stations'],
    queryFn: () => stationsApi.list({ limit: 100 }),
  });

  const { data: alertsData, isLoading: alertsLoading } = useQuery({
    queryKey: ['alerts', 'recent'],
    queryFn: () => alertsApi.list({ limit: 10, resolved: false }),
  });

  const { data: alertStats } = useQuery({
    queryKey: ['alertStats'],
    queryFn: () => alertsApi.getStats(),
  });

  const { data: telemetryData } = useQuery({
    queryKey: ['telemetry', 'dashboard'],
    queryFn: () => telemetryApi.query({ limit: 500 }),
    refetchInterval: 5000,
  });

  const stations = stationsData?.data || [];
  const alerts = alertsData?.data || [];
  const stats = alertStats?.data;
  const telemetry = telemetryData?.data || [];

  const activeStations = stations.filter((s) => s.status === 'active').length;
  const criticalAlerts = stats?.critical || 0;

  const getAggregatedMetricData = (metricType: string) => {
    const metricData = telemetry.filter(
      (t: TelemetryRecord) => t.metric_type === metricType
    );
    const grouped: Record<string, { sum: number; count: number }> = {};

    metricData.forEach((t: TelemetryRecord) => {
      const time = dayjs(t.time).format('HH:mm');
      if (!grouped[time]) {
        grouped[time] = { sum: 0, count: 0 };
      }
      grouped[time].sum += t.value;
      grouped[time].count += 1;
    });

    return Object.entries(grouped)
      .map(([time, data]) => ({
        time,
        value: Math.round((data.sum / data.count) * 100) / 100,
      }))
      .slice(-15);
  };

  const getBatteryDistribution = () => {
    const stationBattery: Record<string, number> = {};
    telemetry
      .filter((t: TelemetryRecord) => t.metric_type === 'battery_soc')
      .forEach((t: TelemetryRecord) => {
        stationBattery[t.station_id] = t.value;
      });

    return [
      { name: '0-25%', value: 0, color: '#ff4d4f' },
      { name: '26-50%', value: 0, color: '#faad14' },
      { name: '51-75%', value: 0, color: '#1890ff' },
      { name: '76-100%', value: 0, color: '#52c41a' },
    ].map((range) => {
      const values = Object.values(stationBattery);
      if (range.name === '0-25%')
        range.value = values.filter((v) => v <= 25).length;
      else if (range.name === '26-50%')
        range.value = values.filter((v) => v > 25 && v <= 50).length;
      else if (range.name === '51-75%')
        range.value = values.filter((v) => v > 50 && v <= 75).length;
      else range.value = values.filter((v) => v > 75).length;
      return range;
    }).filter((r) => r.value > 0);
  };

  const getStationPowerData = () => {
    const stationPower: Record<string, { name: string; value: number }> = {};
    stations.forEach((s) => {
      stationPower[s.id] = { name: s.code, value: 0 };
    });
    telemetry
      .filter((t: TelemetryRecord) => t.metric_type === 'solar_power')
      .forEach((t: TelemetryRecord) => {
        if (stationPower[t.station_id]) {
          stationPower[t.station_id].value = t.value;
        }
      });
    return Object.values(stationPower)
      .filter((s) => s.value > 0)
      .slice(0, 8);
  };

  const getAlertDistribution = () => {
    if (!stats) return [];
    return [
      { name: t('alertSeverity.critical'), value: stats.critical, color: '#ff4d4f' },
      { name: t('alertSeverity.high'), value: stats.high, color: '#fa8c16' },
      { name: t('alertSeverity.medium'), value: stats.medium, color: '#faad14' },
      { name: t('alertSeverity.low'), value: stats.low, color: '#1890ff' },
      { name: t('alertSeverity.info'), value: stats.info, color: '#8c8c8c' },
    ].filter((a) => a.value > 0);
  };

  const avgBattery = Math.round(
    telemetry
      .filter((t: TelemetryRecord) => t.metric_type === 'battery_soc')
      .reduce(
        (acc: number, t: TelemetryRecord, _: number, arr: TelemetryRecord[]) =>
          acc + t.value / arr.length,
        0
      ) || 0
  );

  const avgTemp = Math.round(
    telemetry
      .filter((t: TelemetryRecord) => t.metric_type === 'temperature')
      .reduce(
        (acc: number, t: TelemetryRecord, _: number, arr: TelemetryRecord[]) =>
          acc + t.value / arr.length,
        0
      ) || 0
  );

  if (stationsLoading || alertsLoading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', padding: 100 }}>
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div>
      <Title level={4}>{t('dashboard.title')}</Title>

      {/* Stats Cards */}
      <Row gutter={[16, 16]}>
        <Col xs={12} sm={6} lg={4}>
          <StatsCard
            title={t('dashboard.totalStations')}
            value={stations.length}
            prefix={<EnvironmentOutlined />}
            valueStyle={{ color: '#1890ff' }}
            onClick={() => navigate('/stations')}
          />
        </Col>
        <Col xs={12} sm={6} lg={4}>
          <StatsCard
            title={t('dashboard.activeStations')}
            value={activeStations}
            prefix={<CheckCircleOutlined />}
            valueStyle={{ color: '#52c41a' }}
          />
        </Col>
        <Col xs={12} sm={6} lg={4}>
          <StatsCard
            title={t('dashboard.criticalAlerts')}
            value={criticalAlerts}
            prefix={<ExclamationCircleOutlined />}
            valueStyle={{ color: criticalAlerts > 0 ? '#ff4d4f' : '#52c41a' }}
            onClick={() => navigate('/alerts')}
          />
        </Col>
        <Col xs={12} sm={6} lg={4}>
          <StatsCard
            title={t('dashboard.unresolvedAlerts')}
            value={stats?.unresolved || 0}
            prefix={<AlertOutlined />}
            valueStyle={{ color: '#faad14' }}
          />
        </Col>
        <Col xs={12} sm={6} lg={4}>
          <StatsCard
            title={t('dashboard.avgBattery')}
            value={avgBattery}
            suffix="%"
            prefix={<ThunderboltOutlined />}
            valueStyle={{ color: '#722ed1' }}
          />
        </Col>
        <Col xs={12} sm={6} lg={4}>
          <StatsCard
            title={t('dashboard.avgTemp')}
            value={avgTemp}
            suffix="°C"
            prefix={<CloudOutlined />}
            valueStyle={{ color: '#13c2c2' }}
          />
        </Col>
      </Row>

      {/* Charts Row 1 */}
      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col xs={24} lg={12}>
          <AreaChartCard
            title={t('dashboard.batterySOC')}
            data={getAggregatedMetricData('battery_soc')}
            color="#52c41a"
            unit="%"
            yDomain={[0, 100]}
          />
        </Col>
        <Col xs={24} lg={12}>
          <LineChartCard
            title={t('dashboard.solarPower')}
            data={getAggregatedMetricData('solar_power')}
            color="#faad14"
            unit="W"
          />
        </Col>
      </Row>

      {/* Charts Row 2 */}
      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col xs={24} lg={8}>
          <PieChartCard
            title={t('dashboard.batteryHealth')}
            data={getBatteryDistribution()}
            innerRadius={50}
            outerRadius={80}
          />
        </Col>
        <Col xs={24} lg={8}>
          <BarChartCard
            title={t('dashboard.stationSolarOutput')}
            data={getStationPowerData()}
            layout="vertical"
            unit="W"
          />
        </Col>
        <Col xs={24} lg={8}>
          <PieChartCard
            title={t('dashboard.alertDistribution')}
            data={getAlertDistribution()}
          />
        </Col>
      </Row>

      {/* Charts Row 3 - Weather */}
      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col xs={24} lg={8}>
          <LineChartCard
            title={t('dashboard.temperatureTrend')}
            data={getAggregatedMetricData('temperature')}
            color="#ff4d4f"
            unit="°C"
            height={200}
          />
        </Col>
        <Col xs={24} lg={8}>
          <AreaChartCard
            title={t('dashboard.humidityTrend')}
            data={getAggregatedMetricData('humidity')}
            color="#1890ff"
            unit="%"
            height={200}
            yDomain={[0, 100]}
          />
        </Col>
        <Col xs={24} lg={8}>
          <LineChartCard
            title={t('dashboard.windSpeed')}
            data={getAggregatedMetricData('wind_speed')}
            color="#13c2c2"
            unit=" km/h"
            height={200}
          />
        </Col>
      </Row>

      {/* Tables Row */}
      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col xs={24} lg={14}>
          <AlertsTable
            alerts={alerts}
            onViewAll={() => navigate('/alerts')}
          />
        </Col>
        <Col xs={24} lg={10}>
          <StationsTable
            stations={stations}
            onViewAll={() => navigate('/stations')}
            onRowClick={(station) => navigate(`/stations/${station.id}`)}
          />
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;
