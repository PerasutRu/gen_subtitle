import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// User Management
export const getUsers = async () => {
  const response = await axios.get(`${API_URL}/admin/users`);
  return response.data;
};

export const createUser = async (userData) => {
  const response = await axios.post(`${API_URL}/admin/register`, userData);
  return response.data;
};

export const deleteUser = async (username) => {
  const response = await axios.delete(`${API_URL}/admin/user/${username}`);
  return response.data;
};

// Session Management
export const getSessions = async () => {
  const response = await axios.get(`${API_URL}/admin/sessions`);
  return response.data;
};

export const deleteSession = async (sessionId) => {
  const response = await axios.delete(`${API_URL}/admin/session/${sessionId}`);
  return response.data;
};

export const resetAllSessions = async () => {
  const response = await axios.post(`${API_URL}/admin/reset`);
  return response.data;
};

// System Stats
export const getStats = async () => {
  const response = await axios.get(`${API_URL}/admin/stats`);
  return response.data;
};

export const reloadLimits = async () => {
  const response = await axios.post(`${API_URL}/admin/reload-limits`);
  return response.data;
};
