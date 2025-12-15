import api from './api';
import type {
  ApiResponse,
  ApiListResponse,
  Station,
  StationListItem,
  StationCreateRequest,
  StationStatus,
} from '../types';

export const stationsApi = {
  list: async (params?: {
    page?: number;
    limit?: number;
    status?: StationStatus;
    region_id?: string;
    search?: string;
  }) => {
    const response = await api.get<ApiListResponse<StationListItem>>('/stations', { params });
    return response.data;
  },

  get: async (id: string) => {
    const response = await api.get<ApiResponse<Station>>(`/stations/${id}`);
    return response.data;
  },

  getByCode: async (code: string) => {
    const response = await api.get<ApiResponse<Station>>(`/stations/code/${code}`);
    return response.data;
  },

  create: async (data: StationCreateRequest) => {
    const response = await api.post<ApiResponse<Station>>('/stations', data);
    return response.data;
  },

  update: async (id: string, data: Partial<StationCreateRequest>) => {
    const response = await api.put<ApiResponse<Station>>(`/stations/${id}`, data);
    return response.data;
  },

  delete: async (id: string) => {
    const response = await api.delete(`/stations/${id}`);
    return response.data;
  },

  getByRegion: async (regionId: string) => {
    const response = await api.get<ApiListResponse<StationListItem>>(`/stations/region/${regionId}`);
    return response.data;
  },
};
