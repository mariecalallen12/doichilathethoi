<template>
  <div class="notification-center fixed top-16 right-4 w-96 max-h-[600px] bg-slate-800/95 backdrop-blur-sm rounded-lg border border-purple-500/20 shadow-xl z-50 flex flex-col">
    <!-- Header -->
    <div class="flex items-center justify-between p-4 border-b border-slate-700">
      <h3 class="text-white font-semibold flex items-center gap-2">
        <i class="fas fa-bell text-purple-400"></i>
        Notifications
        <span
          v-if="unreadCount > 0"
          class="bg-red-500 text-white text-xs font-bold rounded-full px-2 py-0.5"
        >
          {{ unreadCount }}
        </span>
      </h3>
      <div class="flex items-center gap-2">
        <button
          v-if="unreadCount > 0"
          @click="markAllAsRead"
          class="text-xs text-purple-400 hover:text-purple-300 transition-colors"
          title="Mark all as read"
        >
          Mark all read
        </button>
        <button
          @click="$emit('close')"
          class="text-gray-400 hover:text-white transition-colors"
        >
          <i class="fas fa-times"></i>
        </button>
      </div>
    </div>

    <!-- Filter Tabs -->
    <div class="flex border-b border-slate-700">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        @click="activeTab = tab.key"
        :class="[
          'flex-1 px-4 py-2 text-sm transition-colors',
          activeTab === tab.key
            ? 'text-purple-400 border-b-2 border-purple-400 bg-purple-500/10'
            : 'text-gray-400 hover:text-gray-300'
        ]"
      >
        {{ tab.label }}
        <span
          v-if="tab.count > 0"
          class="ml-1 text-xs"
        >
          ({{ tab.count }})
        </span>
      </button>
    </div>

    <!-- Notifications List -->
    <div class="flex-1 overflow-y-auto">
      <div v-if="isLoading" class="p-8 text-center text-gray-400">
        <i class="fas fa-spinner fa-spin text-2xl mb-2"></i>
        <p>Loading notifications...</p>
      </div>
      
      <div v-else-if="filteredNotifications.length === 0" class="p-8 text-center text-gray-400">
        <i class="fas fa-bell-slash text-3xl mb-2"></i>
        <p>No notifications</p>
      </div>
      
      <div v-else class="divide-y divide-slate-700">
        <div
          v-for="notification in filteredNotifications"
          :key="notification.id"
          :class="[
            'p-4 hover:bg-slate-700/50 transition-colors cursor-pointer',
            { 'bg-slate-700/30': !notification.is_read }
          ]"
          @click="handleNotificationClick(notification)"
        >
          <div class="flex items-start gap-3">
            <!-- Icon -->
            <div
              :class="[
                'flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center',
                getSeverityClass(notification.severity)
              ]"
            >
              <i :class="getNotificationIcon(notification.type)"></i>
            </div>
            
            <!-- Content -->
            <div class="flex-1 min-w-0">
              <div class="flex items-start justify-between gap-2">
                <h4
                  :class="[
                    'text-sm font-medium',
                    notification.is_read ? 'text-gray-300' : 'text-white font-semibold'
                  ]"
                >
                  {{ notification.title }}
                </h4>
                <button
                  @click.stop="dismissNotification(notification.id)"
                  class="text-gray-500 hover:text-gray-300 transition-colors flex-shrink-0"
                  title="Dismiss"
                >
                  <i class="fas fa-times text-xs"></i>
                </button>
              </div>
              
              <p class="text-xs text-gray-400 mt-1 line-clamp-2">
                {{ notification.message }}
              </p>
              
              <div class="flex items-center justify-between mt-2">
                <span class="text-xs text-gray-500">
                  {{ formatTime(notification.created_at) }}
                </span>
                <span
                  v-if="notification.severity"
                  :class="[
                    'text-xs px-2 py-0.5 rounded',
                    getSeverityBadgeClass(notification.severity)
                  ]"
                >
                  {{ notification.severity }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <div class="p-3 border-t border-slate-700 text-center">
      <button
        @click="loadMore"
        :disabled="isLoading"
        class="text-xs text-purple-400 hover:text-purple-300 transition-colors disabled:opacity-50"
      >
        Load more
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useNotificationsStore } from '../../stores/notifications';

const emit = defineEmits(['close']);

const notificationsStore = useNotificationsStore();
const activeTab = ref('all');
const currentPage = ref(1);
const pageSize = 20;

const tabs = computed(() => {
  return [
    { key: 'all', label: 'All', count: notificationsStore.notifications.length },
    { key: 'unread', label: 'Unread', count: notificationsStore.unreadCount },
    { key: 'alerts', label: 'Alerts', count: notificationsStore.alerts.length },
  ];
});

const isLoading = computed(() => notificationsStore.isLoading);
const unreadCount = computed(() => notificationsStore.unreadCount);

const filteredNotifications = computed(() => {
  let filtered = [...notificationsStore.notifications];
  
  if (activeTab.value === 'unread') {
    filtered = filtered.filter(n => !n.is_read && !n.is_dismissed && !n.is_expired);
  } else if (activeTab.value === 'alerts') {
    filtered = filtered.filter(n => n.type === 'alert' && !n.is_dismissed && !n.is_expired);
  }
  
  return filtered.slice(0, currentPage.value * pageSize);
});

function getSeverityClass(severity) {
  const classes = {
    low: 'bg-blue-500/20 text-blue-400',
    medium: 'bg-yellow-500/20 text-yellow-400',
    high: 'bg-orange-500/20 text-orange-400',
    critical: 'bg-red-500/20 text-red-400',
  };
  return classes[severity] || classes.medium;
}

function getSeverityBadgeClass(severity) {
  const classes = {
    low: 'bg-blue-500/20 text-blue-400',
    medium: 'bg-yellow-500/20 text-yellow-400',
    high: 'bg-orange-500/20 text-orange-400',
    critical: 'bg-red-500/20 text-red-400',
  };
  return classes[severity] || classes.medium;
}

function getNotificationIcon(type) {
  const icons = {
    alert: 'fas fa-exclamation-triangle',
    info: 'fas fa-info-circle',
    warning: 'fas fa-exclamation-circle',
    success: 'fas fa-check-circle',
  };
  return icons[type] || icons.info;
}

function formatTime(timestamp) {
  if (!timestamp) return '';
  
  const date = new Date(timestamp);
  const now = new Date();
  const diffMs = now - date;
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);
  
  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;
  
  return date.toLocaleDateString();
}

async function handleNotificationClick(notification) {
  if (!notification.is_read) {
    await notificationsStore.markAsRead(notification.id);
  }
  
  // Navigate if link_url exists
  if (notification.link_url) {
    // Use router if available
    const router = window.__VUE_ROUTER__;
    if (router) {
      router.push(notification.link_url);
    } else {
      window.location.href = notification.link_url;
    }
  }
}

async function dismissNotification(notificationId) {
  await notificationsStore.dismissNotification(notificationId);
}

async function markAllAsRead() {
  await notificationsStore.markAllAsRead();
}

function loadMore() {
  currentPage.value++;
  notificationsStore.fetchNotifications({
    skip: (currentPage.value - 1) * pageSize,
    limit: pageSize,
  });
}

onMounted(() => {
  notificationsStore.fetchNotifications({ limit: pageSize });
});
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>

