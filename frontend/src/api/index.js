import api from './client';

export const authAPI = {
  login: (credentials) => api.post('/token/', credentials),
  register: (data) => api.post('/users/users/', data),
  me: () => api.get('/users/users/me/'),
};

export const userAPI = {
  list: (params) => api.get('/users/users/', { params }),
  follow: (id) => api.post(`/users/users/${id}/follow/`),
  unfollow: (id) => api.post(`/users/users/${id}/unfollow/`),
};

export const postAPI = {
  feed: (page = 1) => api.get('/posts/posts/', { params: { page } }),
  create: (formData) => api.post('/posts/posts/', formData),
  update: (id, data) => api.patch(`/posts/posts/${id}/`, data),
  remove: (id) => api.delete(`/posts/posts/${id}/`),
  like: (id) => api.post(`/posts/posts/${id}/like/`),
  unlike: (id) => api.post(`/posts/posts/${id}/unlike/`),
  comments: (id, page = 1) => api.get(`/posts/posts/${id}/comments/`, { params: { page } }),
};

export const commentAPI = {
  create: (data) => api.post('/posts/comments/', data),
  remove: (id) => api.delete(`/posts/comments/${id}/`),
};

export const storyAPI = {
  list: () => api.get('/stories/'),
};

export const notificationAPI = {
  list: (params) => api.get('/notifications/', { params }),
  markRead: (id) => api.patch(`/notifications/${id}/`, { is_read: true }),
  markAllRead: () => api.post('/notifications/mark-all-read/'),
};

export function errorMessage(error, fallback = 'Something went wrong. Please try again.') {
  const data = error?.response?.data;
  if (!data) return fallback;
  if (typeof data === 'string') return fallback;
  if (data.detail) return data.detail;
  const first = Object.values(data).flat()[0];
  return typeof first === 'string' ? first : fallback;
}
