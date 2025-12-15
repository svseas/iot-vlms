import api from './api';
import type {
  ApiResponse,
  ApiListResponse,
  Alert,
  AlertListItem,
  AlertCreateRequest,
  AlertStats,
  AlertType,
  SeverityLevel,
} from '../types';

export const alertsApi = {
  list: async (params?: {
    page?: number;
    limit?: number;
    station_id?: string;
    alert_type?: AlertType;
    severity?: SeverityLevel;
    acknowledged?: boolean;
    resolved?: boolean;
    start_date?: string;
    end_date?: string;
  }) => {
    const response = await api.get<ApiListResponse<AlertListItem>>('/alerts', { params });
    return response.data;
  },

  get: async (id: string) => {
    const response = await api.get<ApiResponse<Alert>>(`/alerts/${id}`);
    return response.data;
  },

  create: async (data: AlertCreateRequest) => {
    const response = await api.post<ApiResponse<Alert>>('/alerts', data);
    return response.data;
  },

  acknowledge: async (id: string) => {
    const response = await api.post<ApiResponse<Alert>>(`/alerts/${id}/acknowledge`);
    return response.data;
  },

  resolve: async (id: string) => {
    const response = await api.post<ApiResponse<Alert>>(`/alerts/${id}/resolve`);
    return response.data;
  },

  getByStation: async (stationId: string, limit = 10) => {
    const response = await api.get<ApiListResponse<AlertListItem>>(`/alerts/station/${stationId}`, {
      params: { limit },
    });
    return response.data;
  },

  getStats: async (stationId?: string) => {
    const params = stationId ? { station_id: stationId } : undefined;
    const response = await api.get<ApiResponse<AlertStats>>('/alerts/stats', { params });
    return response.data;
  },
};
