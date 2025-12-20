/**
 * Toast notification utility
 * Simple wrapper for showing toast notifications
 */

export function showToast(message, type = 'info', title = null, duration = 5000) {
  if (typeof window !== 'undefined' && window.showToast) {
    window.showToast(message, type, title, duration)
  } else {
    // Fallback to console if ToastContainer not loaded
    console.log(`[${type.toUpperCase()}] ${title ? title + ': ' : ''}${message}`)
  }
}

export function success(message, title = 'Success', duration = 5000) {
  showToast(message, 'success', title, duration)
}

export function error(message, title = 'Error', duration = 7000) {
  showToast(message, 'error', title, duration)
}

export function warning(message, title = 'Warning', duration = 6000) {
  showToast(message, 'warning', title, duration)
}

export function info(message, title = null, duration = 5000) {
  showToast(message, 'info', title, duration)
}

// Aliases for compatibility
export const showSuccess = success
export const showError = error
export const showWarning = warning
export const showInfo = info

export default {
  show: showToast,
  success,
  error,
  warning,
  info,
  showSuccess,
  showError,
  showWarning,
  showInfo
}
