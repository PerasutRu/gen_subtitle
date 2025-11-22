import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create axios instance with interceptor for auth token
const api = axios.create({
  baseURL: API_URL
});

// Add auth token to all requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// User Management
export const getUsers = async () => {
  const response = await api.get('/admin/users');
  return response.data;
};

export const createUser = async (userData) => {
  const response = await api.post('/admin/register', userData);
  return response.data;
};

export const deleteUser = async (username) => {
  const response = await api.delete(`/admin/user/${username}`);
  return response.data;
};

// Session Management
export const getSessions = async () => {
  const response = await api.get('/admin/sessions');
  return response.data;
};

export const deleteSession = async (sessionId) => {
  const response = await api.delete(`/admin/session/${sessionId}`);
  return response.data;
};

export const resetAllSessions = async () => {
  const response = await api.post('/admin/reset');
  return response.data;
};

// System Stats
export const getStats = async () => {
  const response = await api.get('/admin/stats');
  return response.data;
};

export const reloadLimits = async () => {
  const response = await api.post('/admin/reload-limits');
  return response.data;
};

// User Limits Management
export const getUserLimits = async (username) => {
  const response = await api.get(`/admin/user/${username}/limits`);
  return response.data;
};

export const setUserLimits = async (username, limits) => {
  const response = await api.put(`/admin/user/${username}/limits`, limits);
  return response.data;
};

export const deleteUserLimits = async (username) => {
  const response = await api.delete(`/admin/user/${username}/limits`);
  return response.data;
};

// Default Limits Management
export const getDefaultLimits = async () => {
  const response = await api.get('/admin/default-limits');
  return response.data;
};

export const updateDefaultLimits = async (limits) => {
  const response = await api.put('/admin/default-limits', limits);
  return response.data;
};

// Activity Logs
export const getActivities = async (params = {}) => {
  const queryParams = new URLSearchParams();
  
  if (params.limit) queryParams.append('limit', params.limit);
  if (params.offset) queryParams.append('offset', params.offset);
  if (params.activity_type) queryParams.append('activity_type', params.activity_type);
  if (params.session_id) queryParams.append('session_id', params.session_id);
  if (params.username) queryParams.append('username', params.username);
  if (params.status) queryParams.append('status', params.status);
  if (params.date_from) queryParams.append('date_from', params.date_from);
  if (params.date_to) queryParams.append('date_to', params.date_to);
  
  const response = await api.get(`/admin/activities?${queryParams}`);
  return response.data;
};

export const getActivityStats = async () => {
  const response = await api.get('/admin/activities/stats');
  return response.data;
};
