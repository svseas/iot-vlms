import api from './api';
import type { ApiResponse, ApiListResponse, TelemetryRecord, TelemetryAggregate, Device, LatestTelemetry } from '../types';

export const telemetryApi = {
  getLatest: async (stationId: string) => {
    const response = await api.get<ApiResponse<LatestTelemetry>>(`/telemetry/latest/${stationId}`);
    return response.data;
  },

  query: async (params: {
    station_id?: string;
    device_id?: string;
    metric_type?: string;
    start_time?: string;
    end_time?: string;
    limit?: number;
  }) => {
    const response = await api.get<ApiListResponse<TelemetryRecord>>('/telemetry', { params });
    return response.data;
  },

  getAggregates: async (params: {
    station_id: string;
    metric_type: string;
    start_time: string;
    end_time: string;
    interval?: string;
  }) => {
    const response = await api.get<ApiListResponse<TelemetryAggregate>>('/telemetry/aggregates', { params });
    return response.data;
  },

  getDevices: async (stationId: string) => {
    const response = await api.get<ApiListResponse<Device>>(`/telemetry/devices/${stationId}`);
    return response.data;
  },
};
