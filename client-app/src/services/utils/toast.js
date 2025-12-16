/**
 * Toast notification utility
 * Simple implementation - can be replaced with a library like vue-toastification
 */

const toasts = [];
let toastIdCounter = 0;

export const ToastType = {
  SUCCESS: 'success',
  ERROR: 'error',
  WARNING: 'warning',
  INFO: 'info',
};

/**
 * Show a toast notification
 */
export function showToast(message, type = ToastType.INFO, duration = 3000) {
  // Translate "Not Found" immediately when toast is created
  if (message === 'Not Found' || message === 'Not found' || message === 'not found' ||
      (typeof message === 'string' && message.toLowerCase().trim() === 'not found')) {
    console.log('[DEBUG] showToast: Translating "Not Found" at creation time:', message);
    message = 'Không tìm thấy tài nguyên yêu cầu';
  }
  
  const toast = {
    id: toastIdCounter++,
    message,
    type,
    duration,
    timestamp: Date.now(),
  };

  toasts.push(toast);

  // Auto remove after duration
  setTimeout(() => {
    removeToast(toast.id);
  }, duration);

  // Trigger custom event for toast component
  if (typeof window !== 'undefined') {
    window.dispatchEvent(new CustomEvent('toast', { detail: toast }));
  }

  return toast.id;
}

/**
 * Remove a toast
 */
export function removeToast(id) {
  const index = toasts.findIndex(t => t.id === id);
  if (index >= 0) {
    toasts.splice(index, 1);
  }
}

/**
 * Clear all toasts
 */
export function clearToasts() {
  toasts.length = 0;
}

/**
 * Get all toasts
 */
export function getToasts() {
  // Translate "Not Found" in existing toasts when retrieving
  return toasts.map(toast => {
    if (toast.message === 'Not Found' || toast.message === 'Not found' || toast.message === 'not found' ||
        (typeof toast.message === 'string' && toast.message.toLowerCase().trim() === 'not found')) {
      console.log('[DEBUG] getToasts: Translating "Not Found" in existing toast');
      return { ...toast, message: 'Không tìm thấy tài nguyên yêu cầu' };
    }
    return toast;
  });
}

/**
 * Success toast
 */
export function success(message, duration) {
  return showToast(message, ToastType.SUCCESS, duration);
}

/**
 * Error toast
 */
export function error(message, duration = 5000) {
  // #region agent log
  console.log('[DEBUG] Error toast shown:', message);
  fetch('http://localhost:7242/ingest/a94652aa-f954-45ed-8dd8-1c88a5bdb78d',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'toast.js:77',message:'Error toast called',data:{message,isNot Found:message==='Not Found'||message.includes('Not Found')},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'F'})}).catch(()=>{});
  // #endregion
  
  // Last resort: Translate "Not Found" if it somehow got through
  if (message === 'Not Found' || message === 'Not found' || message === 'not found' ||
      (typeof message === 'string' && message.toLowerCase().trim() === 'not found')) {
    console.log('[DEBUG] Intercepting "Not Found" in toast function, replacing with Vietnamese');
    message = 'Không tìm thấy tài nguyên yêu cầu';
  }
  
  return showToast(message, ToastType.ERROR, duration);
}

/**
 * Warning toast
 */
export function warning(message, duration) {
  return showToast(message, ToastType.WARNING, duration);
}

/**
 * Info toast
 */
export function info(message, duration) {
  return showToast(message, ToastType.INFO, duration);
}
