import React from 'react';
import { Row, Col, Tabs } from 'antd';
import { useTranslation } from 'react-i18next';
import { LineChartCard, AreaChartCard } from '../charts';
import type { TelemetryRecord } from '../../types';
import dayjs from 'dayjs';

interface StationChartsProps {
  telemetry: TelemetryRecord[];
}

const StationCharts: React.FC<StationChartsProps> = ({ telemetry }) => {
  const { t } = useTranslation();
  const getMetricData = (metricType: string, limit = 20) => {
    return telemetry
      .filter((t) => t.metric_type === metricType)
      .sort((a, b) => new Date(a.time).getTime() - new Date(b.time).getTime())
      .slice(-limit)
      .map((t) => ({
        time: dayjs(t.time).format('HH:mm:ss'),
        value: t.value,
      }));
  };

  const powerCharts = (
    <Row gutter={[16, 16]}>
      <Col xs={24} lg={12}>
        <AreaChartCard
          title={`${t('metrics.batterySOC')} (%)`}
          data={getMetricData('battery_soc')}
          color="#52c41a"
          unit="%"
          yDomain={[0, 100]}
        />
      </Col>
      <Col xs={24} lg={12}>
        <LineChartCard
          title={`${t('metrics.batteryVoltage')} (V)`}
          data={getMetricData('battery_voltage')}
          color="#1890ff"
          unit="V"
        />
      </Col>
      <Col xs={24} lg={12}>
        <LineChartCard
          title={`${t('metrics.solarPower')} (W)`}
          data={getMetricData('solar_power')}
          color="#faad14"
          unit="W"
        />
      </Col>
      <Col xs={24} lg={12}>
        <LineChartCard
          title={`${t('metrics.solarVoltage')} (V)`}
          data={getMetricData('solar_voltage')}
          color="#722ed1"
          unit="V"
        />
      </Col>
      <Col xs={24} lg={12}>
        <LineChartCard
          title={`${t('metrics.solarCurrent')} (A)`}
          data={getMetricData('solar_current')}
          color="#eb2f96"
          unit="A"
        />
      </Col>
      <Col xs={24} lg={12}>
        <LineChartCard
          title={`${t('metrics.batteryTemperature')} (°C)`}
          data={getMetricData('battery_temperature')}
          color="#ff4d4f"
          unit="°C"
        />
      </Col>
    </Row>
  );

  const weatherCharts = (
    <Row gutter={[16, 16]}>
      <Col xs={24} lg={12}>
        <LineChartCard
          title={`${t('metrics.temperature')} (°C)`}
          data={getMetricData('temperature')}
          color="#ff4d4f"
          unit="°C"
        />
      </Col>
      <Col xs={24} lg={12}>
        <AreaChartCard
          title={`${t('metrics.humidity')} (%)`}
          data={getMetricData('humidity')}
          color="#1890ff"
          unit="%"
          yDomain={[0, 100]}
        />
      </Col>
      <Col xs={24} lg={12}>
        <LineChartCard
          title={`${t('metrics.windSpeed')} (km/h)`}
          data={getMetricData('wind_speed')}
          color="#13c2c2"
          unit=" km/h"
        />
      </Col>
      <Col xs={24} lg={12}>
        <LineChartCard
          title={`${t('metrics.windDirection')} (°)`}
          data={getMetricData('wind_direction')}
          color="#722ed1"
          unit="°"
          yDomain={[0, 360]}
        />
      </Col>
      <Col xs={24} lg={12}>
        <LineChartCard
          title={`${t('metrics.pressure')} (hPa)`}
          data={getMetricData('pressure')}
          color="#eb2f96"
          unit=" hPa"
        />
      </Col>
    </Row>
  );

  const lightCharts = (
    <Row gutter={[16, 16]}>
      <Col xs={24} lg={12}>
        <AreaChartCard
          title={`${t('metrics.lightIntensity')} (%)`}
          data={getMetricData('light_intensity')}
          color="#faad14"
          unit="%"
          yDomain={[0, 100]}
        />
      </Col>
      <Col xs={24} lg={12}>
        <LineChartCard
          title={`${t('metrics.lightPower')} (W)`}
          data={getMetricData('light_power')}
          color="#722ed1"
          unit="W"
        />
      </Col>
    </Row>
  );

  return (
    <Tabs
      defaultActiveKey="power"
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
        {
          key: 'light',
          label: t('stationDetail.lightSystem'),
          children: lightCharts,
        },
      ]}
    />
  );
};

export default StationCharts;
