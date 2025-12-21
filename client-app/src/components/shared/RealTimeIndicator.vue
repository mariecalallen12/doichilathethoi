<template>
  <div class="real-time-indicator" :class="statusClass">
    <div class="indicator-dot" :class="{ 'pulse': isActive }"></div>
    <span class="indicator-text">{{ statusText }}</span>
    <span class="indicator-timer" v-if="isActive && showTimer">{{ lastUpdate }}</span>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';

const props = defineProps({
  isActive: {
    type: Boolean,
    default: false
  },
  updateInterval: {
    type: Number,
    default: 5000 // milliseconds
  },
  showTimer: {
    type: Boolean,
    default: true
  }
});

const lastUpdate = ref('Just now');
const secondsSinceUpdate = ref(0);
const timer = ref(null);

const statusClass = computed(() => {
  return props.isActive ? 'status-active' : 'status-inactive';
});

const statusText = computed(() => {
  return props.isActive ? 'Live Updates' : 'Paused';
});

// Update timer display
const updateTimer = () => {
  secondsSinceUpdate.value++;
  
  if (secondsSinceUpdate.value < 5) {
    lastUpdate.value = 'Just now';
  } else if (secondsSinceUpdate.value < 60) {
    lastUpdate.value = `${secondsSinceUpdate.value}s ago`;
  } else {
    const minutes = Math.floor(secondsSinceUpdate.value / 60);
    lastUpdate.value = `${minutes}m ago`;
  }
};

// Reset timer on new update
const resetTimer = () => {
  secondsSinceUpdate.value = 0;
  lastUpdate.value = 'Just now';
};

onMounted(() => {
  // Start timer
  timer.value = setInterval(updateTimer, 1000);
  
  // Reset timer every update interval
  setInterval(() => {
    if (props.isActive) {
      resetTimer();
    }
  }, props.updateInterval);
});

onUnmounted(() => {
  if (timer.value) {
    clearInterval(timer.value);
  }
});
</script>

<style scoped>
.real-time-indicator {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.status-active {
  background: rgba(34, 197, 94, 0.1);
  border: 1px solid rgba(34, 197, 94, 0.3);
  color: #22c55e;
}

.status-inactive {
  background: rgba(156, 163, 175, 0.1);
  border: 1px solid rgba(156, 163, 175, 0.3);
  color: #9ca3af;
}

.indicator-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: currentColor;
}

.indicator-dot.pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.indicator-text {
  font-weight: 600;
  letter-spacing: 0.025em;
}

.indicator-timer {
  font-size: 11px;
  opacity: 0.7;
  margin-left: 4px;
}

/* Dark mode styles */
@media (prefers-color-scheme: dark) {
  .status-active {
    background: rgba(34, 197, 94, 0.15);
  }
  
  .status-inactive {
    background: rgba(156, 163, 175, 0.15);
  }
}
</style>
