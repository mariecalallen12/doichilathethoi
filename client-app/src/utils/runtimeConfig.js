// Runtime helpers to resolve API and WebSocket endpoints safely in all envs
const DEFAULT_API_FALLBACK =
  typeof window !== 'undefined'
    ? `${window.location.origin}/api`
    : 'https://cmeetrading.com/api';

/**
 * Resolve API base URL with sane defaults.
 * Priority: VITE_API_BASE_URL -> window.origin/api -> production domain.
 */
export function getApiBaseUrl() {
  const env = (import.meta.env.VITE_API_BASE_URL || '').trim();
  const hostname = typeof window !== 'undefined' ? window.location.hostname : '';

  // If env is localhost but we are on a non-localhost host, ignore env to avoid CORS/prod issues
  if (env && env.includes('localhost') && hostname && hostname !== 'localhost' && hostname !== '127.0.0.1') {
    return DEFAULT_API_FALLBACK.replace(/\/+$/, '');
  }

  if (env) return env;
  return DEFAULT_API_FALLBACK.replace(/\/+$/, '');
}

const DEFAULT_WS_FALLBACK =
  typeof window !== 'undefined'
    ? `${window.location.origin.replace(/^http/, 'ws')}/ws`
    : 'wss://cmeetrading.com/ws';

/**
 * Resolve WebSocket base URL, ensure correct scheme and single /ws suffix.
 */
export function getWsBaseUrl() {
  const env = (import.meta.env.VITE_WS_URL || '').trim();
  const hostname = typeof window !== 'undefined' ? window.location.hostname : '';

  // Ignore localhost env when running on non-localhost hosts to avoid CORS
  const isLocalhostHost = hostname === 'localhost' || hostname === '127.0.0.1';
  let base =
    env && !(env.includes('localhost') && !isLocalhostHost)
      ? env
      : DEFAULT_WS_FALLBACK;

  // Normalize scheme
  base = base.replace(/^http:/, 'ws:').replace(/^https:/, 'wss:');

  // Trim trailing slash
  base = base.replace(/\/+$/, '');

  // Ensure single /ws path
  if (!/\/ws($|\/|\?)/.test(base)) {
    base = `${base}/ws`;
  }

  return base;
}

