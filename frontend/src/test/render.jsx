import { render } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { AuthContext } from '../context/auth-context';

export const me = { id: 1, username: 'mara', following_count: 0, followers_count: 0 };

export function renderWithAuth(ui, { user = me, refreshUser = async () => user } = {}) {
  return render(
    <MemoryRouter>
      <AuthContext.Provider value={{ user, refreshUser, logout() {} }}>{ui}</AuthContext.Provider>
    </MemoryRouter>,
  );
}

export const page = (results, next = null) => ({ data: { count: results.length, next, results } });

export function makePost(overrides = {}) {
  return {
    id: 10,
    title: 'Low tide',
    caption: 'Harbour at 6am',
    image: '/media/posts/a.jpg',
    created_at: new Date().toISOString(),
    author: { id: 2, username: 'teo', avatar: null },
    likes_count: 3,
    comments_count: 0,
    is_liked: false,
    is_published: true,
    ...overrides,
  };
}
