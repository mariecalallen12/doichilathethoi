/**
 * Lightweight logging & metrics hooks.
 * Có thể gắn Sentry/LogRocket hoặc backend metrics sau này.
 */

const ENABLE_CONSOLE_LOGGING = import.meta.env.VITE_ENABLE_CLIENT_LOGGING === 'true';

export function logError(context, error, extra = {}) {
  if (!ENABLE_CONSOLE_LOGGING) return;
  // eslint-disable-next-line no-console
  console.error('[AppError]', context, {
    message: error?.message,
    stack: error?.stack,
    ...extra,
  });
  // Hook Sentry/LogRocket tại đây nếu cần
}

export function logWarning(context, details = {}) {
  if (!ENABLE_CONSOLE_LOGGING) return;
  // eslint-disable-next-line no-console
  console.warn('[AppWarn]', context, details);
}

export function logInfo(context, details = {}) {
  if (!ENABLE_CONSOLE_LOGGING) return;
  // eslint-disable-next-line no-console
  console.info('[AppInfo]', context, details);
}

/**
 * Simple performance timer helper.
 */
export function startTimer(label) {
  const start = performance.now();
  return () => {
    const duration = performance.now() - start;
    if (ENABLE_CONSOLE_LOGGING) {
      // eslint-disable-next-line no-console
      console.info('[Perf]', label, `${duration.toFixed(0)}ms`);
    }
    return duration;
  };
}

