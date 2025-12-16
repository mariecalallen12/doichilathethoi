<template>
  <div class="fixed top-4 right-4 z-50 space-y-2">
    <TransitionGroup name="toast" tag="div">
      <div
        v-for="toast in toasts"
        :key="toast.id"
        :class="[
          'glass-panel rounded-lg p-4 min-w-[300px] max-w-[400px] shadow-lg',
          getToastClass(toast.type)
        ]"
      >
        <div class="flex items-start space-x-3">
          <i :class="[getToastIcon(toast.type), 'mt-0.5']"></i>
          <div class="flex-1">
            <div class="text-white text-sm">{{ translateMessage(toast.message) }}</div>
          </div>
          <button
            @click="removeToast(toast.id)"
            class="text-purple-300 hover:text-white transition-colors"
          >
            <i class="fas fa-times"></i>
          </button>
        </div>
      </div>
    </TransitionGroup>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { getToasts, removeToast as removeToastUtil } from '../../services/utils/toast';

const toasts = ref([]);

function updateToasts() {
  const allToasts = getToasts();
  // #region agent log
  allToasts.forEach(toast => {
    if (toast.message === 'Not Found' || toast.message?.includes('Not Found')) {
      console.log('[DEBUG] ToastContainer: Found "Not Found" toast:', toast);
      fetch('http://localhost:7242/ingest/a94652aa-f954-45ed-8dd8-1c88a5bdb78d',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'ToastContainer.vue:36',message:'Not Found toast detected',data:{toast},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'G'})}).catch(()=>{});
    }
  });
  // #endregion
  toasts.value = allToasts;
}

function handleToastEvent(event) {
  updateToasts();
}

function getToastClass(type) {
  const classes = {
    success: 'bg-green-500/20 border border-green-500/30',
    error: 'bg-red-500/20 border border-red-500/30',
    warning: 'bg-yellow-500/20 border border-yellow-500/30',
    info: 'bg-blue-500/20 border border-blue-500/30',
  };
  return classes[type] || classes.info;
}

function getToastIcon(type) {
  const icons = {
    success: 'fas fa-check-circle text-green-400',
    error: 'fas fa-exclamation-circle text-red-400',
    warning: 'fas fa-exclamation-triangle text-yellow-400',
    info: 'fas fa-info-circle text-blue-400',
  };
  return icons[type] || icons.info;
}

function translateMessage(message) {
  // Final safety net: Translate "Not Found" at display time
  if (!message) return message;
  
  // Normalize the message for comparison
  const normalized = typeof message === 'string' 
    ? message.trim().toLowerCase().replace(/\s+/g, ' ')
    : String(message).trim().toLowerCase();
  
  // Check for various forms of "Not Found"
  const notFoundPatterns = [
    'not found',
    'notfound',
    'not-found',
    'not_found',
    'notfound',
  ];
  
  if (notFoundPatterns.some(pattern => normalized === pattern || normalized.includes(pattern))) {
    console.log('[DEBUG] ToastContainer: Translating message at display time:', message, '-> normalized:', normalized);
    return 'Không tìm thấy tài nguyên yêu cầu';
  }
  
  return message;
}

function removeToast(id) {
  removeToastUtil(id);
  updateToasts();
}

onMounted(() => {
  updateToasts();
  window.addEventListener('toast', handleToastEvent);
  // Poll for updates (in case toasts are added directly)
  const interval = setInterval(updateToasts, 100);
  onUnmounted(() => clearInterval(interval));
  
  // MutationObserver to catch "Not Found" text in DOM as final safety net
  const observer = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
      // Check added nodes
      mutation.addedNodes.forEach((node) => {
        if (node.nodeType === Node.ELEMENT_NODE) {
          const element = node;
          // Check if this is a toast element or contains toast
          const toastElement = element.classList?.contains('glass-panel') 
            ? element 
            : element.querySelector?.('.glass-panel');
          
          if (toastElement) {
            const textNodes = toastElement.querySelectorAll('.text-white, div');
            textNodes.forEach((textNode) => {
              const text = textNode.textContent?.trim() || '';
              if (text === 'Not Found' || text === 'Not found' || 
                  text.toLowerCase() === 'not found') {
                console.log('[DEBUG] MutationObserver: Found "Not Found" in DOM, translating:', text);
                textNode.textContent = 'Không tìm thấy tài nguyên yêu cầu';
              }
            });
          }
        } else if (node.nodeType === Node.TEXT_NODE) {
          // Check text nodes directly
          const text = node.textContent?.trim() || '';
          if (text === 'Not Found' || text === 'Not found' || 
              text.toLowerCase() === 'not found') {
            console.log('[DEBUG] MutationObserver: Found "Not Found" in text node, translating');
            node.textContent = 'Không tìm thấy tài nguyên yêu cầu';
          }
        }
      });
      
      // Also check for character data changes
      if (mutation.type === 'characterData') {
        const text = mutation.target.textContent?.trim() || '';
        if (text === 'Not Found' || text === 'Not found' || 
            text.toLowerCase() === 'not found') {
          console.log('[DEBUG] MutationObserver: Found "Not Found" in characterData, translating');
          mutation.target.textContent = 'Không tìm thấy tài nguyên yêu cầu';
        }
      }
    });
    
    // Also do a sweep of all toast elements periodically
    const allToasts = document.querySelectorAll('.glass-panel');
    allToasts.forEach((toast) => {
      const textElements = toast.querySelectorAll('.text-white, div');
      textElements.forEach((el) => {
        const text = el.textContent?.trim() || '';
        if (text === 'Not Found' || text === 'Not found' || 
            text.toLowerCase() === 'not found') {
          console.log('[DEBUG] MutationObserver: Found "Not Found" in existing toast, translating');
          el.textContent = 'Không tìm thấy tài nguyên yêu cầu';
        }
      });
    });
  });
  
  // Observe the toast container and document body
  const container = document.querySelector('.fixed.top-4.right-4') || document.body;
  if (container) {
    observer.observe(container, {
      childList: true,
      subtree: true,
      characterData: true,
      attributes: false
    });
  }
  
  // Also set up a periodic check as backup
  const periodicCheck = setInterval(() => {
    const allToasts = document.querySelectorAll('.glass-panel');
    allToasts.forEach((toast) => {
      const textElements = toast.querySelectorAll('.text-white');
      textElements.forEach((el) => {
        const text = el.textContent?.trim() || '';
        if (text === 'Not Found' || text === 'Not found' || 
            text.toLowerCase() === 'not found') {
          console.log('[DEBUG] Periodic check: Found "Not Found", translating');
          el.textContent = 'Không tìm thấy tài nguyên yêu cầu';
        }
      });
    });
  }, 100);
  
  onUnmounted(() => {
    observer.disconnect();
    clearInterval(periodicCheck);
  });
});

onUnmounted(() => {
  window.removeEventListener('toast', handleToastEvent);
});
</script>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(100%);
}
</style>
