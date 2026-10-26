import axios from 'axios';

export const tokenStore = {
  get access() {
    return localStorage.getItem('access_token');
  },
  get refresh() {
    return localStorage.getItem('refresh_token');
  },
  save({ access, refresh }) {
    if (access) localStorage.setItem('access_token', access);
    if (refresh) localStorage.setItem('refresh_token', refresh);
  },
  clear() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  },
};

const api = axios.create({ baseURL: import.meta.env.VITE_API_URL || '/api' });

api.interceptors.request.use((config) => {
  const token = tokenStore.access;
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

let refreshing = null;

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;
    const canRefresh =
      error.response?.status === 401 && tokenStore.refresh && original && !original._retried;
    if (!canRefresh) throw error;

    original._retried = true;
    refreshing ??= axios
      .post(`${api.defaults.baseURL}/token/refresh/`, { refresh: tokenStore.refresh })
      .then(({ data }) => tokenStore.save(data))
      .finally(() => {
        refreshing = null;
      });

    try {
      await refreshing;
    } catch {
      tokenStore.clear();
      throw error;
    }
    return api(original);
  },
);

export default api;
