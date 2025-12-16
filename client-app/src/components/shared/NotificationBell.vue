<template>
  <div class="relative">
    <button
      @click="toggleCenter"
      class="relative p-2 text-gray-300 hover:text-white transition-colors rounded-lg hover:bg-slate-700/50"
      :class="{ 'text-purple-400': isOpen }"
    >
      <i class="fas fa-bell text-lg"></i>
      <span
        v-if="unreadCount > 0"
        class="absolute -top-1 -right-1 bg-red-500 text-white text-xs font-bold rounded-full h-5 w-5 flex items-center justify-center"
        :class="{ 'animate-pulse': criticalAlerts.length > 0 }"
      >
        {{ unreadCount > 99 ? '99+' : unreadCount }}
      </span>
    </button>
    
    <NotificationCenter
      v-if="isOpen"
      @close="isOpen = false"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useNotificationsStore } from '../../stores/notifications';
import NotificationCenter from './NotificationCenter.vue';

const notificationsStore = useNotificationsStore();
const isOpen = ref(false);

const unreadCount = computed(() => notificationsStore.unreadCount);
const criticalAlerts = computed(() => notificationsStore.criticalAlerts);

function toggleCenter() {
  isOpen.value = !isOpen.value;
}

// Close on outside click
function handleClickOutside(event) {
  if (isOpen.value && !event.target.closest('.notification-bell-container')) {
    isOpen.value = false;
  }
}

onMounted(() => {
  // Fetch notifications on mount
  notificationsStore.fetchNotifications({ limit: 20 });
  notificationsStore.fetchUnreadCount();
  
  // Listen for click outside
  document.addEventListener('click', handleClickOutside);
  
  // Listen for new notifications via custom events
  window.addEventListener('diagnostic-alert', handleNewAlert);
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
  window.removeEventListener('diagnostic-alert', handleNewAlert);
});

function handleNewAlert(event) {
  // Add notification to store if it's a diagnostic alert
  const alert = event.detail;
  notificationsStore.addNotification({
    id: alert.id || Date.now(),
    type: 'alert',
    category: 'diagnostic',
    severity: alert.severity || 'medium',
    title: alert.title,
    message: alert.message,
    data: alert.conditions_met,
    created_at: alert.timestamp || new Date().toISOString(),
    is_read: false,
    is_dismissed: false,
    is_expired: false,
  });
  
  // Refresh unread count
  notificationsStore.fetchUnreadCount();
}
</script>

<style scoped>
.notification-bell-container {
  position: relative;
}
</style>

