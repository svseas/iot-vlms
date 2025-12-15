import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Spin, Card, Tag, Typography } from 'antd';
import { useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { stationsApi } from '../services/stations';
import { telemetryApi } from '../services/telemetry';
import { alertsApi } from '../services/alerts';
import { StationHeader, StationMetrics, StationCharts } from '../components/stations';
import type { AlertListItem, SeverityLevel, MetricItem } from '../types';
import dayjs from 'dayjs';

const { Text } = Typography;

const StationDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { t } = useTranslation();

  const { data: stationData, isLoading: stationLoading } = useQuery({
    queryKey: ['station', id],
    queryFn: () => stationsApi.get(id!),
    enabled: !!id,
  });

  const { data: telemetryData, isLoading: telemetryLoading } = useQuery({
    queryKey: ['telemetry', id],
    queryFn: () => telemetryApi.query({ station_id: id, limit: 200 }),
    enabled: !!id,
    refetchInterval: 5000,
  });

  const { data: latestData } = useQuery({
    queryKey: ['telemetry-latest', id],
    queryFn: () => telemetryApi.getLatest(id!),
    enabled: !!id,
    refetchInterval: 5000,
  });

  const { data: alertsData } = useQuery({
    queryKey: ['alerts', 'station', id],
    queryFn: () => alertsApi.getByStation(id!, 10),
    enabled: !!id,
  });

  const station = stationData?.data;
  const telemetry = telemetryData?.data || [];
  const alerts = alertsData?.data || [];

  // Transform latest metrics object to array format for StationMetrics
  const latestTelemetry: MetricItem[] = latestData?.data?.metrics
    ? Object.entries(latestData.data.metrics).map(([key, value]) => ({
        metric_type: key,
        value: value as number,
      }))
    : [];

  if (stationLoading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', padding: 100 }}>
        <Spin size="large" />
      </div>
    );
  }

  if (!station) {
    return <div>{t('stations.notFound')}</div>;
  }

  const severityColors: Record<SeverityLevel, string> = {
    critical: 'red',
    high: 'orange',
    medium: 'gold',
    low: 'blue',
    info: 'default',
  };

  return (
    <div>
      <StationHeader station={station} onBack={() => navigate('/stations')} />

      {/* Real-time Metrics */}
      <div style={{ marginBottom: 16 }}>
        <StationMetrics telemetry={latestTelemetry} />
      </div>

      {/* Charts */}
      <StationCharts telemetry={telemetry} />

      {/* Alerts Section */}
      <Card title={`${t('stationDetail.recentAlerts')} (${alerts.length})`} size="small" style={{ marginTop: 16 }}>
        {alerts.length === 0 ? (
          <Text type="secondary">{t('stationDetail.noAlerts')}</Text>
        ) : (
          alerts.map((alert: AlertListItem) => (
            <div
              key={alert.id}
              style={{
                padding: '8px 0',
                borderBottom: '1px solid #f0f0f0',
                display: 'flex',
                alignItems: 'center',
                gap: 8,
              }}
            >
              <Tag color={severityColors[alert.severity]}>
                {alert.severity.toUpperCase()}
              </Tag>
              <Text strong>{alert.title}</Text>
              <Text type="secondary" style={{ marginLeft: 'auto' }}>
                {dayjs(alert.created_at).format('MM-DD HH:mm')}
              </Text>
            </div>
          ))
        )}
      </Card>

      {telemetryLoading && (
        <div style={{ textAlign: 'center', padding: 20 }}>
          <Spin size="small" /> {t('stationDetail.loadingTelemetry')}
        </div>
      )}
    </div>
  );
};

export default StationDetail;
