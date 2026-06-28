/**
 * Almacenamiento de tokens. Usa localStorage por simplicidad operativa; para
 * máxima seguridad puede migrarse a cookies httpOnly emitidas por el backend.
 */
const ACCESS_KEY = "le_access_token";
const REFRESH_KEY = "le_refresh_token";

export const tokenStore = {
  getAccessToken: () => localStorage.getItem(ACCESS_KEY),
  getRefreshToken: () => localStorage.getItem(REFRESH_KEY),
  setTokens(access: string, refresh: string) {
    localStorage.setItem(ACCESS_KEY, access);
    localStorage.setItem(REFRESH_KEY, refresh);
  },
  clear() {
    localStorage.removeItem(ACCESS_KEY);
    localStorage.removeItem(REFRESH_KEY);
  },
  isAuthenticated: () => Boolean(localStorage.getItem(ACCESS_KEY)),
};
