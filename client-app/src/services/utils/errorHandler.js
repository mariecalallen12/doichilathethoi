/**
 * Error handling utility with retry logic and user-friendly messages
 */

const MAX_RETRIES = 3;
const RETRY_DELAY = 1000; // 1 second

/**
 * Get user-friendly error message
 */
export function getErrorMessage(error) {
  // #region agent log
  fetch('http://localhost:7242/ingest/a94652aa-f954-45ed-8dd8-1c88a5bdb78d',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'errorHandler.js:11',message:'getErrorMessage called',data:{hasError:!!error,hasResponse:!!error?.response,status:error?.response?.status,dataDetail:error?.response?.data?.detail,dataMessage:error?.response?.data?.message,errorCode:error?.code,errorMessage:error?.message},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'B'})).catch(()=>{});
  // #endregion
  
  if (!error) return 'Đã xảy ra lỗi không xác định';

  // Network errors
  if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
    return 'Kết nối quá lâu. Vui lòng kiểm tra kết nối mạng và thử lại.';
  }

  if (error.code === 'ERR_NETWORK' || error.message?.includes('Network Error')) {
    return 'Không thể kết nối đến máy chủ. Vui lòng kiểm tra kết nối mạng.';
  }

  // HTTP errors
  if (error.response) {
    const status = error.response.status;
    const data = error.response.data;

    // Get message from response
    if (data?.detail) {
      // #region agent log
      fetch('http://localhost:7242/ingest/a94652aa-f954-45ed-8dd8-1c88a5bdb78d',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'errorHandler.js:30',message:'Returning data.detail',data:{detail:data.detail,status},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'B'})).catch(()=>{});
      // #endregion
      // Translate common English error messages to Vietnamese
      const detail = data.detail;
      // #region agent log
      console.log('[DEBUG] Error detail:', detail, 'Type:', typeof detail);
      fetch('http://localhost:7242/ingest/a94652aa-f954-45ed-8dd8-1c88a5bdb78d',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'errorHandler.js:30',message:'Checking error detail',data:{detail,detailType:typeof detail,isNot Found:detail==='Not Found'||detail?.includes?.('Not Found')},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'B'})}).catch(()=>{});
      // #endregion
      if (detail === 'Not Found' || detail === 'Not found' || detail === 'not found' || 
          (typeof detail === 'string' && detail.toLowerCase().includes('not found'))) {
        // Include URL context if available
        const url = error.config?.url || error.request?.responseURL || 'unknown endpoint';
        const translated = `Không tìm thấy tài nguyên: ${url}`;
        // #region agent log
        console.log('[DEBUG] Translating Not Found:', detail, '->', translated);
        fetch('http://localhost:7242/ingest/a94652aa-f954-45ed-8dd8-1c88a5bdb78d',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'errorHandler.js:35',message:'Translating Not Found',data:{original:detail,translated},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'B'})}).catch(()=>{});
        // #endregion
        return translated;
      }
      return detail;
    }
    if (data?.message) {
      // #region agent log
      fetch('http://localhost:7242/ingest/a94652aa-f954-45ed-8dd8-1c88a5bdb78d',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'errorHandler.js:33',message:'Returning data.message',data:{message:data.message,status},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'B'})).catch(()=>{});
      // #endregion
      return data.message;
    }
    if (typeof data === 'string') {
      // #region agent log
      fetch('http://localhost:7242/ingest/a94652aa-f954-45ed-8dd8-1c88a5bdb78d',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'errorHandler.js:36',message:'Returning string data',data:{data,status},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'B'})).catch(()=>{});
      // #endregion
      return data;
    }

    // Status code messages
    const statusMessages = {
      400: 'Yêu cầu không hợp lệ. Vui lòng kiểm tra lại thông tin.',
      401: 'Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.',
      403: 'Bạn không có quyền thực hiện thao tác này.',
      404: 'Không tìm thấy tài nguyên yêu cầu.',
      409: 'Dữ liệu đã tồn tại hoặc xung đột.',
      422: 'Dữ liệu không hợp lệ. Vui lòng kiểm tra lại.',
      429: 'Quá nhiều yêu cầu. Vui lòng thử lại sau.',
      500: 'Lỗi máy chủ. Vui lòng thử lại sau.',
      502: 'Máy chủ không phản hồi. Vui lòng thử lại sau.',
      503: 'Dịch vụ tạm thời không khả dụng. Vui lòng thử lại sau.',
      504: 'Máy chủ phản hồi quá lâu. Vui lòng thử lại sau.',
    };

    const finalMessage = statusMessages[status] || `Lỗi ${status}: ${error.message || 'Đã xảy ra lỗi'}`;
    // #region agent log
    fetch('http://localhost:7242/ingest/a94652aa-f954-45ed-8dd8-1c88a5bdb78d',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'errorHandler.js:54',message:'Returning status message',data:{status,finalMessage,hasStatusMessage:!!statusMessages[status]},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'B'})).catch(()=>{});
    // #endregion
    return finalMessage;
  }

  // Generic error
  // #region agent log
  fetch('http://localhost:7242/ingest/a94652aa-f954-45ed-8dd8-1c88a5bdb78d',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'errorHandler.js:58',message:'Returning generic error message',data:{errorMessage:error.message},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'B'})).catch(()=>{});
  // #endregion
  return error.message || 'Đã xảy ra lỗi không xác định';
}

/**
 * Retry function with exponential backoff
 */
export async function retry(fn, options = {}) {
  const {
    maxRetries = MAX_RETRIES,
    retryDelay = RETRY_DELAY,
    onRetry = null,
    shouldRetry = null,
  } = options;

  let lastError;
  
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error;

      // Check if we should retry
      if (shouldRetry && !shouldRetry(error, attempt)) {
        throw error;
      }

      // Don't retry on last attempt
      if (attempt >= maxRetries) {
        break;
      }

      // Don't retry on certain errors
      if (error.response) {
        const status = error.response.status;
        // Don't retry on client errors (4xx) except 429
        if (status >= 400 && status < 500 && status !== 429) {
          throw error;
        }
      }

      // Calculate delay with exponential backoff
      const delay = retryDelay * Math.pow(2, attempt);
      
      if (onRetry) {
        onRetry(error, attempt + 1, delay);
      }

      // Wait before retrying
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }

  throw lastError;
}

/**
 * Handle API error with retry and user notification
 */
export async function handleApiError(error, retryFn = null, options = {}) {
  const {
    showNotification = true,
    maxRetries = MAX_RETRIES,
    onError = null,
  } = options;

  const errorMessage = getErrorMessage(error);

  // Show notification if enabled
  if (showNotification) {
    // You can integrate with a toast notification library here
    console.error('API Error:', errorMessage);
    // Example: toast.error(errorMessage);
  }

  // Call custom error handler if provided
  if (onError) {
    onError(error, errorMessage);
  }

  // Retry if retry function provided
  if (retryFn && error.response?.status >= 500) {
    try {
      return await retry(retryFn, { maxRetries });
    } catch (retryError) {
      return Promise.reject(retryError);
    }
  }

  return Promise.reject(error);
}

/**
 * Create a retryable API call wrapper
 */
export function createRetryableApiCall(apiCall, options = {}) {
  return async (...args) => {
    return retry(
      () => apiCall(...args),
      {
        maxRetries: options.maxRetries || MAX_RETRIES,
        retryDelay: options.retryDelay || RETRY_DELAY,
        shouldRetry: (error) => {
          // Retry on network errors and server errors (5xx)
          if (!error.response) return true;
          const status = error.response.status;
          return status >= 500 || status === 429;
        },
        onRetry: (error, attempt, delay) => {
          if (options.onRetry) {
            options.onRetry(error, attempt, delay);
          } else {
            console.log(`Retrying API call (attempt ${attempt}/${options.maxRetries || MAX_RETRIES}) after ${delay}ms`);
          }
        },
      }
    );
  };
}

/**
 * Error types for categorization
 */
export const ErrorTypes = {
  NETWORK: 'network',
  TIMEOUT: 'timeout',
  AUTH: 'auth',
  VALIDATION: 'validation',
  SERVER: 'server',
  UNKNOWN: 'unknown',
};

/**
 * Categorize error type
 */
export function getErrorType(error) {
  if (!error) return ErrorTypes.UNKNOWN;

  // Network errors
  if (error.code === 'ERR_NETWORK' || error.message?.includes('Network Error')) {
    return ErrorTypes.NETWORK;
  }

  if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
    return ErrorTypes.TIMEOUT;
  }

  // HTTP errors
  if (error.response) {
    const status = error.response.status;
    if (status === 401 || status === 403) {
      return ErrorTypes.AUTH;
    }
    if (status === 400 || status === 422) {
      return ErrorTypes.VALIDATION;
    }
    if (status >= 500) {
      return ErrorTypes.SERVER;
    }
  }

  return ErrorTypes.UNKNOWN;
}

/**
 * Check if error is retryable
 */
export function isRetryableError(error) {
  const type = getErrorType(error);
  return type === ErrorTypes.NETWORK || type === ErrorTypes.TIMEOUT || type === ErrorTypes.SERVER;
}

/**
 * Format error for logging
 */
export function formatErrorForLogging(error) {
  return {
    message: error.message,
    type: getErrorType(error),
    status: error.response?.status,
    data: error.response?.data,
    stack: error.stack,
    timestamp: new Date().toISOString(),
  };
}
