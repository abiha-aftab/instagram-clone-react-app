import { useCallback, useEffect, useMemo, useState } from 'react';
import { authAPI } from '../api';
import { tokenStore } from '../api/client';
import { AuthContext } from './auth-context';

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(() => Boolean(tokenStore.access));

  const loadMe = useCallback(async () => {
    const { data } = await authAPI.me();
    setUser(data);
    return data;
  }, []);

  useEffect(() => {
    if (!tokenStore.access) return;
    authAPI
      .me()
      .then(({ data }) => setUser(data))
      .catch(() => tokenStore.clear())
      .finally(() => setLoading(false));
  }, []);

  const login = useCallback(
    async (credentials) => {
      const { data } = await authAPI.login(credentials);
      tokenStore.save(data);
      return loadMe();
    },
    [loadMe],
  );

  const register = useCallback(
    async ({ email, username, password }) => {
      await authAPI.register({ email, username, password });
      return login({ email, password });
    },
    [login],
  );

  const logout = useCallback(() => {
    tokenStore.clear();
    setUser(null);
  }, []);

  const value = useMemo(
    () => ({ user, loading, login, register, logout, refreshUser: loadMe }),
    [user, loading, login, register, logout, loadMe],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
