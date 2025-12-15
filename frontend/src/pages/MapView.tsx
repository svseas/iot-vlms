import React, { useState, useRef, useMemo, useEffect } from 'react';
import { Card, Typography, Spin, Tag, Drawer, Divider, Row, Col, Statistic, Tabs } from 'antd';
import {
  ThunderboltOutlined,
  CloudOutlined,
  EnvironmentOutlined,
} from '@ant-design/icons';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import { Icon, DivIcon } from 'leaflet';
import type { Marker as LeafletMarker } from 'leaflet';
import { useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { stationsApi } from '../services/stations';
import { telemetryApi } from '../services/telemetry';
import { alertsApi } from '../services/alerts';
import { LineChartCard, AreaChartCard } from '../components/charts';
import type { StationListItem, StationStatus, Station, TelemetryRecord, MetricItem } from '../types';
import dayjs from 'dayjs';
import 'leaflet/dist/leaflet.css';

// CSS for flickering animation
const flickerStyle = document.createElement('style');
flickerStyle.textContent = `
  @keyframes flicker {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
  }
  .lighthouse-critical {
    animation: flicker 0.5s ease-in-out infinite;
  }
  .lighthouse-marker {
    transition: transform 0.2s ease;
  }
  .lighthouse-marker:hover {
    transform: scale(1.1);
  }
`;
document.head.appendChild(flickerStyle);

const { Title, Text } = Typography;

// SVG lighthouse icon as data URL
const lighthouseSvg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="40" height="40">
  <defs>
    <linearGradient id="tower" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#e74c3c"/>
      <stop offset="50%" style="stop-color:#ffffff"/>
      <stop offset="100%" style="stop-color:#e74c3c"/>
    </linearGradient>
  </defs>
  <!-- Base -->
  <rect x="16" y="54" width="32" height="8" rx="2" fill="#34495e"/>
  <!-- Tower -->
  <path d="M24 54 L20 54 L26 20 L38 20 L44 54 L40 54" fill="url(#tower)" stroke="#2c3e50" stroke-width="1"/>
  <!-- Red stripes -->
  <rect x="27" y="28" width="10" height="6" fill="#e74c3c"/>
  <rect x="25" y="40" width="14" height="6" fill="#e74c3c"/>
  <!-- Light house top -->
  <rect x="26" y="14" width="12" height="6" fill="#2c3e50"/>
  <rect x="24" y="12" width="16" height="4" fill="#f39c12"/>
  <!-- Light beam -->
  <ellipse cx="32" cy="10" rx="8" ry="4" fill="#f1c40f" opacity="0.8"/>
  <!-- Dome -->
  <path d="M28 12 Q32 6 36 12" fill="#e74c3c" stroke="#c0392b" stroke-width="1"/>
</svg>`;

const activeLighthouseSvg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="40" height="40">
  <defs>
    <linearGradient id="towerActive" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#27ae60"/>
      <stop offset="50%" style="stop-color:#ffffff"/>
      <stop offset="100%" style="stop-color:#27ae60"/>
    </linearGradient>
    <filter id="glow">
      <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>
  <!-- Base -->
  <rect x="16" y="54" width="32" height="8" rx="2" fill="#2c3e50"/>
  <!-- Tower -->
  <path d="M24 54 L20 54 L26 20 L38 20 L44 54 L40 54" fill="url(#towerActive)" stroke="#1e8449" stroke-width="1"/>
  <!-- Green stripes -->
  <rect x="27" y="28" width="10" height="6" fill="#27ae60"/>
  <rect x="25" y="40" width="14" height="6" fill="#27ae60"/>
  <!-- Light house top -->
  <rect x="26" y="14" width="12" height="6" fill="#2c3e50"/>
  <rect x="24" y="12" width="16" height="4" fill="#f39c12"/>
  <!-- Light beam - glowing -->
  <ellipse cx="32" cy="10" rx="10" ry="5" fill="#f1c40f" filter="url(#glow)"/>
  <!-- Dome -->
  <path d="M28 12 Q32 6 36 12" fill="#27ae60" stroke="#1e8449" stroke-width="1"/>
</svg>`;

const defaultIcon = new Icon({
  iconUrl: `data:image/svg+xml;base64,${btoa(lighthouseSvg)}`,
  iconSize: [40, 40],
  iconAnchor: [20, 40],
  popupAnchor: [0, -40],
});

const activeIcon = new Icon({
  iconUrl: `data:image/svg+xml;base64,${btoa(activeLighthouseSvg)}`,
  iconSize: [48, 48],
  iconAnchor: [24, 48],
  popupAnchor: [0, -48],
});

// Critical alert lighthouse SVG (red with warning glow)
const criticalLighthouseSvg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="48" height="48">
  <defs>
    <linearGradient id="towerCritical" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#dc3545"/>
      <stop offset="50%" style="stop-color:#ffffff"/>
      <stop offset="100%" style="stop-color:#dc3545"/>
    </linearGradient>
    <filter id="glowRed">
      <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>
  <!-- Warning glow circle -->
  <circle cx="32" cy="32" r="30" fill="#dc3545" opacity="0.3" filter="url(#glowRed)"/>
  <!-- Base -->
  <rect x="16" y="54" width="32" height="8" rx="2" fill="#2c3e50"/>
  <!-- Tower -->
  <path d="M24 54 L20 54 L26 20 L38 20 L44 54 L40 54" fill="url(#towerCritical)" stroke="#dc3545" stroke-width="2"/>
  <!-- Red stripes -->
  <rect x="27" y="28" width="10" height="6" fill="#dc3545"/>
  <rect x="25" y="40" width="14" height="6" fill="#dc3545"/>
  <!-- Light house top -->
  <rect x="26" y="14" width="12" height="6" fill="#2c3e50"/>
  <rect x="24" y="12" width="16" height="4" fill="#dc3545"/>
  <!-- Light beam - red warning -->
  <ellipse cx="32" cy="10" rx="12" ry="6" fill="#dc3545" filter="url(#glowRed)"/>
  <!-- Dome -->
  <path d="M28 12 Q32 6 36 12" fill="#dc3545" stroke="#a71d2a" stroke-width="1"/>
  <!-- Warning icon -->
  <text x="32" y="48" font-size="14" fill="#fff" text-anchor="middle" font-weight="bold">!</text>
</svg>`;

const createCriticalIcon = () => new DivIcon({
  html: `<div class="lighthouse-marker lighthouse-critical">${criticalLighthouseSvg}</div>`,
  iconSize: [48, 48],
  iconAnchor: [24, 48],
  popupAnchor: [0, -48],
  className: '',
});

const statusColors: Record<StationStatus, string> = {
  active: 'green',
  inactive: 'red',
  maintenance: 'orange',
  decommissioned: 'default',
};

interface HoverMarkerProps {
  station: StationListItem;
  isSelected: boolean;
  hasCriticalAlert: boolean;
  onSelect: (station: StationListItem) => void;
  t: (key: string) => string;
}

const HoverMarker: React.FC<HoverMarkerProps> = ({ station, isSelected, hasCriticalAlert, onSelect, t }) => {
  const markerRef = useRef<LeafletMarker>(null);

  const eventHandlers = useMemo(
    () => ({
      mouseover() {
        markerRef.current?.openPopup();
      },
      mouseout() {
        markerRef.current?.closePopup();
      },
      click() {
        onSelect(station);
      },
    }),
    [station, onSelect]
  );

  // Determine which icon to use
  const getIcon = () => {
    if (hasCriticalAlert) return createCriticalIcon();
    if (isSelected) return activeIcon;
    return defaultIcon;
  };

  return (
    <Marker
      ref={markerRef}
      position={[station.location.lat, station.location.lng]}
      icon={getIcon()}
      eventHandlers={eventHandlers}
    >
      <Popup>
        <div style={{ minWidth: 180 }}>
          <h4 style={{ margin: '0 0 4px 0' }}>{station.name}</h4>
          <p style={{ margin: '2px 0', fontSize: 12 }}>
            <strong>{t('stations.code')}:</strong> {station.code}
          </p>
          <p style={{ margin: '2px 0', fontSize: 12 }}>
            <Tag color={statusColors[station.status]} style={{ margin: 0 }}>
              {t(`stationStatus.${station.status}`).toUpperCase()}
            </Tag>
          </p>
          <p style={{ margin: '4px 0 0 0', fontSize: 11, color: '#666' }}>
            {t('map.clickForDetails')}
          </p>
        </div>
      </Popup>
    </Marker>
  );
};

interface StationPanelProps {
  station: Station | null;
  telemetry: TelemetryRecord[];
  latestTelemetry: MetricItem[];
  loading: boolean;
  t: (key: string) => string;
}

const StationPanel: React.FC<StationPanelProps> = ({
  station,
  telemetry,
  latestTelemetry,
  loading,
  t,
}) => {
  const getLatestValue = (metricType: string): number | null => {
    if (!Array.isArray(latestTelemetry)) return null;
    const record = latestTelemetry.find((item) => item.metric_type === metricType);
    return record ? record.value : null;
  };

  const getMetricData = (metricType: string, limit = 20) => {
    if (!Array.isArray(telemetry)) return [];
    return telemetry
      .filter((item) => item.metric_type === metricType)
      .sort((a, b) => new Date(a.time).getTime() - new Date(b.time).getTime())
      .slice(-limit)
      .map((item) => ({
        time: dayjs(item.time).format('HH:mm'),
        value: item.value,
      }));
  };

  const batterySOC = getLatestValue('battery_soc');
  const solarPower = getLatestValue('solar_power');
  const temperature = getLatestValue('temperature');
  const humidity = getLatestValue('humidity');

  if (!station) return null;

  const powerCharts = (
    <Row gutter={[8, 8]}>
      <Col span={24}>
        <AreaChartCard
          title={`${t('metrics.batterySOC')} (%)`}
          data={getMetricData('battery_soc')}
          color="#52c41a"
          unit="%"
          yDomain={[0, 100]}
          height={180}
        />
      </Col>
      <Col span={24}>
        <LineChartCard
          title={`${t('metrics.solarPower')} (W)`}
          data={getMetricData('solar_power')}
          color="#faad14"
          unit="W"
          height={180}
        />
      </Col>
      <Col span={24}>
        <LineChartCard
          title={`${t('metrics.batteryVoltage')} (V)`}
          data={getMetricData('battery_voltage')}
          color="#1890ff"
          unit="V"
          height={180}
        />
      </Col>
    </Row>
  );

  const weatherCharts = (
    <Row gutter={[8, 8]}>
      <Col span={24}>
        <LineChartCard
          title={`${t('metrics.temperature')} (°C)`}
          data={getMetricData('temperature')}
          color="#ff4d4f"
          unit="°C"
          height={180}
        />
      </Col>
      <Col span={24}>
        <AreaChartCard
          title={`${t('metrics.humidity')} (%)`}
          data={getMetricData('humidity')}
          color="#1890ff"
          unit="%"
          yDomain={[0, 100]}
          height={180}
        />
      </Col>
      <Col span={24}>
        <LineChartCard
          title={`${t('metrics.windSpeed')} (km/h)`}
          data={getMetricData('wind_speed')}
          color="#13c2c2"
          unit=" km/h"
          height={180}
        />
      </Col>
    </Row>
  );

  return (
    <div style={{ padding: '0 8px' }}>
      {/* Station Header */}
      <div style={{ marginBottom: 16 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <Title level={4} style={{ margin: 0 }}>{station.name}</Title>
            <Text type="secondary">{station.code}</Text>
          </div>
          <Tag color={statusColors[station.status]} style={{ marginTop: 4 }}>
            {t(`stationStatus.${station.status}`).toUpperCase()}
          </Tag>
        </div>
      </div>

      {/* Location Info */}
      <Card size="small" style={{ marginBottom: 16 }} styles={{ body: { padding: 12 } }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <EnvironmentOutlined style={{ color: '#1890ff' }} />
          <div>
            <Text style={{ fontSize: 12 }}>{t('map.coordinates')}</Text>
            <br />
            <Text strong style={{ fontSize: 13 }}>
              {station.location.lat.toFixed(6)}, {station.location.lng.toFixed(6)}
            </Text>
          </div>
        </div>
        {station.metadata?.province ? (
          <div style={{ marginTop: 8 }}>
            <Text type="secondary" style={{ fontSize: 12 }}>
              {t('stationDetail.province')}: {station.metadata.province as string}
            </Text>
          </div>
        ) : null}
      </Card>

      <Divider style={{ margin: '12px 0' }} />

      {/* Real-time Metrics */}
      <Title level={5} style={{ marginBottom: 12 }}>{t('map.realTimeMetrics')}</Title>
      {loading ? (
        <div style={{ textAlign: 'center', padding: 20 }}>
          <Spin size="small" />
        </div>
      ) : (
        <Row gutter={[8, 8]} style={{ marginBottom: 16 }}>
          <Col span={12}>
            <Card size="small" styles={{ body: { padding: 12 } }}>
              <Statistic
                title={t('metrics.batterySOC')}
                value={batterySOC ?? 0}
                suffix="%"
                prefix={<ThunderboltOutlined />}
                styles={{
                  content: {
                    fontSize: 18,
                    color: (batterySOC ?? 0) > 50 ? '#52c41a' : '#faad14',
                  },
                }}
              />
            </Card>
          </Col>
          <Col span={12}>
            <Card size="small" styles={{ body: { padding: 12 } }}>
              <Statistic
                title={t('metrics.solarPower')}
                value={solarPower ?? 0}
                suffix="W"
                styles={{
                  content: { fontSize: 18, color: '#faad14' },
                }}
              />
            </Card>
          </Col>
          <Col span={12}>
            <Card size="small" styles={{ body: { padding: 12 } }}>
              <Statistic
                title={t('metrics.temperature')}
                value={temperature ?? 0}
                suffix="°C"
                prefix={<CloudOutlined />}
                styles={{
                  content: { fontSize: 18 },
                }}
              />
            </Card>
          </Col>
          <Col span={12}>
            <Card size="small" styles={{ body: { padding: 12 } }}>
              <Statistic
                title={t('metrics.humidity')}
                value={humidity ?? 0}
                suffix="%"
                styles={{
                  content: { fontSize: 18, color: '#1890ff' },
                }}
              />
            </Card>
          </Col>
        </Row>
      )}

      <Divider style={{ margin: '12px 0' }} />

      {/* Charts */}
      <Title level={5} style={{ marginBottom: 12 }}>{t('map.charts')}</Title>
      {loading ? (
        <div style={{ textAlign: 'center', padding: 40 }}>
          <Spin />
          <div style={{ marginTop: 8 }}>
            <Text type="secondary">{t('stationDetail.loadingTelemetry')}</Text>
          </div>
        </div>
      ) : (
        <Tabs
          defaultActiveKey="power"
          size="small"
          items={[
            {
              key: 'power',
              label: t('stationDetail.powerBattery'),
              children: powerCharts,
            },
            {
              key: 'weather',
              label: t('stationDetail.weather'),
              children: weatherCharts,
            },
          ]}
        />
      )}
    </div>
  );
};

const MapView: React.FC = () => {
  const { t } = useTranslation();
  const [selectedStation, setSelectedStation] = useState<StationListItem | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);

  const { data, isLoading } = useQuery({
    queryKey: ['stations'],
    queryFn: () => stationsApi.list({ limit: 100 }),
  });

  // Fetch unresolved critical alerts
  const { data: criticalAlerts } = useQuery({
    queryKey: ['alerts', 'critical', 'unresolved'],
    queryFn: () => alertsApi.list({ severity: 'critical', resolved: false, limit: 100 }),
    refetchInterval: 10000, // Refresh every 10 seconds
  });

  // Get set of station IDs with critical alerts
  const stationsWithCriticalAlerts = useMemo(() => {
    const alertList = criticalAlerts?.data || [];
    return new Set(alertList.map(alert => alert.station_id));
  }, [criticalAlerts]);

  const { data: stationDetail } = useQuery({
    queryKey: ['station', selectedStation?.id],
    queryFn: () => stationsApi.get(selectedStation!.id),
    enabled: !!selectedStation?.id,
  });

  const { data: telemetryData, isLoading: telemetryLoading } = useQuery({
    queryKey: ['telemetry', 'map', selectedStation?.id],
    queryFn: () => telemetryApi.query({ station_id: selectedStation!.id, limit: 200 }),
    enabled: !!selectedStation?.id,
    refetchInterval: drawerOpen ? 10000 : false,
  });

  const { data: latestData } = useQuery({
    queryKey: ['telemetry-latest', 'map', selectedStation?.id],
    queryFn: () => telemetryApi.getLatest(selectedStation!.id),
    enabled: !!selectedStation?.id,
    refetchInterval: drawerOpen ? 10000 : false,
  });

  const stations = data?.data || [];
  const station = stationDetail?.data || null;
  const telemetry = Array.isArray(telemetryData?.data) ? telemetryData.data : [];

  // Transform latest metrics object to array format
  const latestTelemetry: MetricItem[] = latestData?.data?.metrics
    ? Object.entries(latestData.data.metrics).map(([key, value]) => ({
        metric_type: key,
        value: value as number,
      }))
    : [];

  const defaultCenter: [number, number] = [12.5, 108.0];
  const defaultZoom = 6;

  const handleSelectStation = (station: StationListItem) => {
    setSelectedStation(station);
    setDrawerOpen(true);
  };

  const handleCloseDrawer = () => {
    setDrawerOpen(false);
    setSelectedStation(null);
  };

  if (isLoading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', padding: 100 }}>
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div style={{ position: 'relative' }}>
      <Title level={4} style={{ marginBottom: 16 }}>
        {t('map.title')}
      </Title>

      <div style={{ display: 'flex', gap: 0 }}>
        <Card
          styles={{ body: { padding: 0, overflow: 'hidden' } }}
          style={{
            flex: 1,
            transition: 'all 0.3s ease',
          }}
        >
          <MapContainer
            center={defaultCenter}
            zoom={defaultZoom}
            style={{ height: 'calc(100vh - 220px)', width: '100%' }}
          >
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            {stations.map((station: StationListItem) => (
              <HoverMarker
                key={station.id}
                station={station}
                isSelected={selectedStation?.id === station.id}
                hasCriticalAlert={stationsWithCriticalAlerts.has(station.id)}
                onSelect={handleSelectStation}
                t={t}
              />
            ))}
          </MapContainer>
        </Card>

        <Drawer
          title={
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <EnvironmentOutlined />
              {t('map.stationDetails')}
            </div>
          }
          placement="right"
          onClose={handleCloseDrawer}
          open={drawerOpen}
          width={420}
          mask={false}
          styles={{
            body: { padding: '12px 16px', overflow: 'auto' },
          }}
        >
          <StationPanel
            station={station}
            telemetry={telemetry}
            latestTelemetry={latestTelemetry}
            loading={telemetryLoading}
            t={t}
          />
        </Drawer>
      </div>
    </div>
  );
};

export default MapView;
