<template>
  <div v-if="hasError" class="error-boundary">
    <div class="error-container">
      <div class="error-icon">
        <i class="ri-error-warning-line"></i>
      </div>
      <h2 class="error-title">Đã xảy ra lỗi</h2>
      <p class="error-message">
        {{ errorMessage || 'Có lỗi không mong muốn xảy ra. Vui lòng thử lại sau.' }}
      </p>
      <div class="error-actions">
        <button @click="handleReload" class="btn-primary">
          <i class="ri-refresh-line mr-2"></i>
          Tải lại trang
        </button>
        <button @click="handleGoHome" class="btn-secondary">
          <i class="ri-home-line mr-2"></i>
          Về trang chủ
        </button>
      </div>
      <details v-if="showDetails" class="error-details">
        <summary>Chi tiết lỗi (dành cho nhà phát triển)</summary>
        <pre class="error-stack">{{ errorStack }}</pre>
      </details>
    </div>
  </div>
  <slot v-else />
</template>

<script setup>
import { ref, onErrorCaptured, provide } from 'vue';
import { useRouter } from 'vue-router';

const props = defineProps({
  fallback: {
    type: Function,
    default: null,
  },
  onError: {
    type: Function,
    default: null,
  },
  showDetails: {
    type: Boolean,
    default: false,
  },
});

const router = useRouter();
const hasError = ref(false);
const errorMessage = ref('');
const errorStack = ref('');

// Provide error handler for child components
provide('errorHandler', {
  handleError: (error) => {
    hasError.value = true;
    errorMessage.value = error.message || 'Đã xảy ra lỗi không mong muốn';
    errorStack.value = error.stack || error.toString();
    
    // Call custom error handler if provided
    if (props.onError) {
      props.onError(error);
    }
    
    // Log error for debugging
    if (import.meta.env.DEV) {
      console.error('ErrorBoundary caught error:', error);
    }
  },
});

// Capture Vue component errors
onErrorCaptured((error, instance, info) => {
  hasError.value = true;
  
  // Provide more user-friendly error messages for common issues
  let userMessage = error.message || 'Đã xảy ra lỗi trong component';
  
  // Check for specific API/client errors
  if (error.message && error.message.includes('is not a function')) {
    if (error.message.includes('.get') || error.message.includes('h.get')) {
      userMessage = 'Lỗi kết nối API. Vui lòng tải lại trang hoặc liên hệ hỗ trợ nếu vấn đề vẫn tiếp tục.';
    } else {
      userMessage = 'Lỗi khởi tạo ứng dụng. Vui lòng tải lại trang.';
    }
  } else if (error.message && error.message.includes('Network Error')) {
    userMessage = 'Lỗi kết nối mạng. Vui lòng kiểm tra kết nối internet của bạn.';
  } else if (error.message && error.message.includes('timeout')) {
    userMessage = 'Yêu cầu quá thời gian chờ. Vui lòng thử lại sau.';
  }
  
  errorMessage.value = userMessage;
  errorStack.value = `${error.toString()}\n\nComponent: ${info}\n\nStack: ${error.stack || 'N/A'}`;
  
  // Call custom error handler if provided
  if (props.onError) {
    props.onError(error, instance, info);
  }
  
  // Log error for debugging
  if (import.meta.env.DEV) {
    console.error('ErrorBoundary caught component error:', error, instance, info);
  }
  
  // Return false to prevent error from propagating
  return false;
});

// Handle global errors
if (typeof window !== 'undefined') {
  window.addEventListener('error', (event) => {
    // Check if it's a resource loading error (asset loading failure)
    const isAssetError = event.target && (
      event.target.tagName === 'SCRIPT' || 
      event.target.tagName === 'LINK' || 
      event.target.tagName === 'IMG'
    );
    
    if (isAssetError) {
      // Log asset loading failures for debugging
      console.error('Asset loading failed:', {
        tag: event.target.tagName,
        src: event.target.src || event.target.href,
        message: event.message
      });
      
      // Try to reload the page if critical assets fail
      if (event.target.tagName === 'SCRIPT' && event.target.src) {
        console.warn('Critical script failed to load, attempting page reload...');
        setTimeout(() => {
          if (!hasError.value) {
            window.location.reload();
          }
        }, 2000);
      }
      return;
    }
    
    // Filter out resource loading errors and non-critical errors
    if (event.message?.includes('Loading chunk') || 
        event.message?.includes('Failed to fetch') ||
        event.filename?.includes('chrome-extension')) {
      console.warn('Non-critical error ignored:', event.message);
      return;
    }
    
    hasError.value = true;
    
    // Provide more user-friendly error messages
    let userMessage = event.message || 'Đã xảy ra lỗi JavaScript';
    
    // Check for specific API/client errors
    if (event.message && event.message.includes('is not a function')) {
      if (event.message.includes('.get') || event.message.includes('h.get')) {
        userMessage = 'Lỗi kết nối API. Vui lòng tải lại trang hoặc liên hệ hỗ trợ nếu vấn đề vẫn tiếp tục.';
      } else {
        userMessage = 'Lỗi khởi tạo ứng dụng. Vui lòng tải lại trang.';
      }
    }
    
    errorMessage.value = userMessage;
    errorStack.value = `${event.filename}:${event.lineno}:${event.colno}\n\n${event.error?.stack || 'N/A'}`;
    
    if (props.onError) {
      props.onError(event.error);
    }
  });
  
  window.addEventListener('unhandledrejection', (event) => {
    // Filter out API errors that are already handled gracefully
    const reason = event.reason?.message || event.reason?.toString() || '';
    if (reason.includes('401') || 
        reason.includes('403') || 
        reason.includes('Authentication') ||
        reason.includes('Failed to fetch') ||
        reason.includes('Network Error') ||
        reason.includes('API error')) {
      console.warn('API error handled gracefully, not showing error boundary:', reason);
      event.preventDefault(); // Prevent default error handling
      return;
    }
    
    // Check for API client initialization errors
    if (reason.includes('is not a function') && (reason.includes('.get') || reason.includes('h.get'))) {
      hasError.value = true;
      errorMessage.value = 'Lỗi kết nối API. Vui lòng tải lại trang hoặc liên hệ hỗ trợ nếu vấn đề vẫn tiếp tục.';
      errorStack.value = event.reason?.stack || event.reason?.toString() || 'N/A';
      
      if (props.onError) {
        props.onError(event.reason);
      }
      event.preventDefault();
      return;
    }
    
    hasError.value = true;
    
    // Provide more user-friendly error messages
    let userMessage = event.reason?.message || 'Đã xảy ra lỗi Promise';
    if (userMessage.includes('is not a function')) {
      userMessage = 'Lỗi khởi tạo ứng dụng. Vui lòng tải lại trang.';
    }
    
    errorMessage.value = userMessage;
    errorStack.value = event.reason?.stack || event.reason?.toString() || 'N/A';
    
    if (props.onError) {
      props.onError(event.reason);
    }
  });
}

const handleReload = () => {
  window.location.reload();
};

const handleGoHome = () => {
  router.push('/');
  hasError.value = false;
  errorMessage.value = '';
  errorStack.value = '';
};
</script>

<style scoped>
.error-boundary {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.error-container {
  max-width: 600px;
  width: 100%;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 1rem;
  padding: 3rem;
  text-align: center;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.error-icon {
  font-size: 4rem;
  color: #ef4444;
  margin-bottom: 1rem;
}

.error-title {
  font-size: 1.5rem;
  font-weight: bold;
  color: white;
  margin-bottom: 1rem;
}

.error-message {
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 2rem;
  line-height: 1.6;
}

.error-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-bottom: 2rem;
}

.btn-primary,
.btn-secondary {
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.2);
}

.error-details {
  margin-top: 2rem;
  text-align: left;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 0.5rem;
  padding: 1rem;
}

.error-details summary {
  color: rgba(255, 255, 255, 0.8);
  cursor: pointer;
  margin-bottom: 0.5rem;
}

.error-stack {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.875rem;
  white-space: pre-wrap;
  word-break: break-all;
  max-height: 300px;
  overflow-y: auto;
  padding: 1rem;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 0.25rem;
}
</style>

