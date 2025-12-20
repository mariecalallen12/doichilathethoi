/**
 * Error Handler Utility
 * Centralized error handling for API calls and store actions
 */

/**
 * Extract error message from error object
 */
export function getErrorMessage(error) {
  if (!error) return 'Unknown error occurred'
  
  // API error response
  if (error.response?.data) {
    const data = error.response.data
    return data.detail || data.message || data.error || 'Server error occurred'
  }
  
  // Network error
  if (error.request) {
    return 'Network error. Please check your connection.'
  }
  
  // Generic error
  return error.message || error.toString() || 'An error occurred'
}

/**
 * Handle API error with logging and user feedback
 */
export function handleApiError(error, context = '') {
  const message = getErrorMessage(error)
  
  console.error(`[${context}] API Error:`, {
    message,
    status: error.response?.status,
    data: error.response?.data,
    error
  })
  
  // Show toast if available
  if (typeof window !== 'undefined' && window.showToast) {
    window.showToast(message, 'error', 'Error')
  }
  
  return message
}

/**
 * Wrap async function with error handling
 */
export function withErrorHandling(fn, context = '') {
  return async (...args) => {
    try {
      return await fn(...args)
    } catch (error) {
      const message = handleApiError(error, context)
      throw new Error(message)
    }
  }
}

/**
 * Check if error is authentication error
 */
export function isAuthError(error) {
  return error.response?.status === 401 || error.response?.status === 403
}

/**
 * Check if error is network error
 */
export function isNetworkError(error) {
  return !error.response && error.request
}

/**
 * Check if error is validation error
 */
export function isValidationError(error) {
  return error.response?.status === 422 || error.response?.status === 400
}

export default {
  getErrorMessage,
  handleApiError,
  withErrorHandling,
  isAuthError,
  isNetworkError,
  isValidationError
}
