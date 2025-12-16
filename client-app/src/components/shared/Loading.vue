<template>
  <div v-if="show" :class="['loading-container', containerClass]">
    <div v-if="type === 'spinner'" class="loading-spinner" :class="spinnerClass">
      <div class="spinner"></div>
      <p v-if="message" class="loading-message">{{ message }}</p>
    </div>
    <div v-else-if="type === 'skeleton'" class="loading-skeleton">
      <LoadingSkeleton :type="skeletonType" :rows="rows" :columns="columns" />
    </div>
    <div v-else-if="type === 'overlay'" class="loading-overlay">
      <div class="spinner"></div>
      <p v-if="message" class="loading-message">{{ message }}</p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import LoadingSkeleton from '../personal/shared/LoadingSkeleton.vue';

const props = defineProps({
  show: {
    type: Boolean,
    default: false,
  },
  type: {
    type: String,
    default: 'spinner',
    validator: (value) => ['spinner', 'skeleton', 'overlay'].includes(value),
  },
  message: {
    type: String,
    default: '',
  },
  size: {
    type: String,
    default: 'medium',
    validator: (value) => ['small', 'medium', 'large'].includes(value),
  },
  fullScreen: {
    type: Boolean,
    default: false,
  },
  skeletonType: {
    type: String,
    default: 'card',
  },
  rows: {
    type: Number,
    default: 3,
  },
  columns: {
    type: Number,
    default: 4,
  },
});

const containerClass = computed(() => {
  const classes = [];
  if (props.fullScreen) {
    classes.push('fixed inset-0 z-50');
  }
  if (props.type === 'overlay') {
    classes.push('fixed inset-0 z-50 bg-black/50 backdrop-blur-sm');
  }
  return classes.join(' ');
});

const spinnerClass = computed(() => {
  return `spinner-${props.size}`;
});
</script>

<style scoped>
.loading-container {
  display: flex;
  align-items: center;
  justify-content: center;
}

.loading-spinner {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.loading-overlay {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  min-height: 100vh;
}

.spinner {
  border: 3px solid rgba(139, 92, 246, 0.2);
  border-top: 3px solid #8b5cf6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.spinner-small {
  width: 24px;
  height: 24px;
  border-width: 2px;
}

.spinner-medium {
  width: 40px;
  height: 40px;
  border-width: 3px;
}

.spinner-large {
  width: 64px;
  height: 64px;
  border-width: 4px;
}

.loading-message {
  color: #a78bfa;
  font-size: 0.875rem;
  text-align: center;
  margin-top: 0.5rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>

