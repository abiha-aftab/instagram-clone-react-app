import api from './axios';

// Authentication
export const authAPI = {
  register: (data) => api.post('/users/register/', data),
  login: (data) => api.post('/auth/login/', data),
  refresh: (refreshToken) => api.post('/auth/refresh/', { refresh: refreshToken }),
  verify: (token) => api.post('/auth/verify/', { token }),
};

// Users
export const userAPI = {
  getProfile: () => api.get('/users/profile/'),
  updateProfile: (data) => api.put('/users/profile/', data),
  getUserByUsername: (username) => api.get(`/users/profile/${username}/`),
  searchUsers: (query) => api.get(`/users/search/?q=${query}`),
  followUser: (username) => api.post(`/users/follow/${username}/`),
  unfollowUser: (username) => api.delete(`/users/unfollow/${username}/`),
  getFollowers: (username) => api.get(`/users/${username}/followers/`),
  getFollowing: (username) => api.get(`/users/${username}/following/`),
};

// Posts
export const postAPI = {
  getFeed: () => api.get('/posts/'),
  createPost: (data) => api.post('/posts/', data, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  getPost: (id) => api.get(`/posts/${id}/`),
  updatePost: (id, data) => api.put(`/posts/${id}/`, data),
  deletePost: (id) => api.delete(`/posts/${id}/`),
  getUserPosts: (username) => api.get(`/posts/user/${username}/`),
  likePost: (id) => api.post(`/posts/${id}/like/`),
  unlikePost: (id) => api.delete(`/posts/${id}/unlike/`),
  getPostLikes: (id) => api.get(`/posts/${id}/likes/`),
  getPostComments: (id) => api.get(`/posts/${id}/comments/`),
  createComment: (postId, data) => api.post(`/posts/${postId}/comments/`, data),
  updateComment: (id, data) => api.put(`/posts/comments/${id}/`, data),
  deleteComment: (id) => api.delete(`/posts/comments/${id}/`),
  getCommentReplies: (id) => api.get(`/posts/comments/${id}/replies/`),
};

// Stories
export const storyAPI = {
  getStories: () => api.get('/stories/'),
  createStory: (data) => api.post('/stories/', data, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  getStory: (id) => api.get(`/stories/${id}/`),
  deleteStory: (id) => api.delete(`/stories/${id}/`),
  getUserStories: (username) => api.get(`/stories/user/${username}/`),
  viewStory: (id) => api.post(`/stories/${id}/view/`),
  getStoryViewers: (id) => api.get(`/stories/${id}/viewers/`),
};

// Notifications
export const notificationAPI = {
  getNotifications: () => api.get('/notifications/'),
  getUnreadNotifications: () => api.get('/notifications/unread/'),
  getNotificationCount: () => api.get('/notifications/count/'),
  markAsRead: (id) => api.patch(`/notifications/${id}/read/`),
  markAllAsRead: () => api.patch('/notifications/mark-all-read/'),
  deleteNotification: (id) => api.delete(`/notifications/${id}/delete/`),
};
