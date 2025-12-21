<script setup>
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import { useAuthStore } from '../../store/auth';
import { useAppStore } from '../../store/app';

const route = useRoute();
const authStore = useAuthStore();
const appStore = useAppStore();

const menuItems = computed(() => {
  const items = [
    {
      title: 'Dashboard',
      icon: 'fas fa-chart-line',
      path: '/dashboard',
      permission: 'dashboard:read',
    },
    {
      title: 'Quản lý người dùng',
      icon: 'fas fa-users',
      path: '/users',
      permission: 'user:read',
    },
    {
      title: 'Chat Hỗ trợ',
      icon: 'ri-customer-service-2-line',
      path: '/chat',
      permission: 'support:chat',
    },
    {
      title: 'Quản lý tài chính',
      icon: 'fas fa-wallet',
      path: '/financial',
      permission: 'financial:read',
    },
    {
      title: 'Phân tích & Báo cáo',
      icon: 'fas fa-chart-bar',
      path: '/analytics',
      permission: 'analytics:read',
    },
    {
      title: 'Cài đặt hệ thống',
      icon: 'fas fa-cog',
      path: '/settings',
      permission: 'system:read',
    },
    {
      title: 'Diagnostics',
      icon: 'fas fa-stethoscope',
      path: '/diagnostics',
      permission: 'system:read',
    },
    {
      title: 'Alert Management',
      icon: 'fas fa-bell',
      path: '/alerts',
      permission: 'system:read',
    },
    {
      title: 'Scenario Builder',
      icon: 'fas fa-magic',
      path: '/scenario-builder',
      permission: 'system:read',
    },
    {
      title: 'Session Manager',
      icon: 'fas fa-clock',
      path: '/session-manager',
      permission: 'system:read',
    },
    {
      title: 'Monitoring Hub',
      icon: 'fas fa-eye',
      path: '/monitoring-hub',
      permission: 'system:read',
    },
    {
      title: 'Educational Hub',
      icon: 'fas fa-graduation-cap',
      path: '/educational-hub',
      permission: 'system:read',
    },
    {
      title: 'Audit Logs',
      icon: 'fas fa-clipboard-list',
      path: '/audit-logs',
      permission: 'system:read',
    },
    {
      title: 'Điều khiển giao dịch',
      icon: 'fas fa-sliders-h',
      path: '/admin-controls',
      permission: 'admin:trading:control',
    },
  ];

  // Filter by permissions
  return items.filter(item => {
    if (!item.permission) return true;
    return authStore.hasPermission(item.permission);
  });
});

const isActive = (path) => {
  return route.path.startsWith(path);
};
</script>

<template>
  <aside
    :class="[
      'fixed left-0 top-0 h-full bg-gradient-dark border-r border-white/10 z-40',
      'transition-transform duration-300 ease-in-out',
      appStore.isSidebarOpen ? 'translate-x-0' : '-translate-x-full',
      'lg:translate-x-0',
    ]"
    style="width: 260px;"
  >
    <!-- Logo -->
    <div class="flex items-center gap-3 px-6 py-6 border-b border-white/10">
      <div class="w-10 h-10 bg-gradient-button rounded-lg flex items-center justify-center shadow-lg">
        <i class="fas fa-crown text-white text-lg"></i>
      </div>
      <div>
        <h1 class="text-white text-lg font-bold font-secular">AdminPortal</h1>
        <p class="text-white/60 text-xs uppercase tracking-widest">CMEETRADING</p>
      </div>
    </div>

    <!-- Menu -->
    <nav class="px-4 py-4 space-y-1 overflow-y-auto" style="height: calc(100vh - 100px);">
      <router-link
        v-for="item in menuItems"
        :key="item.path"
        :to="item.path"
        :class="[
          'flex items-center gap-3 px-4 py-3 rounded-lg transition-all',
          'text-white/70 hover:text-white hover:bg-white/10',
          isActive(item.path) && 'bg-primary/20 text-white border-l-4 border-primary',
        ]"
      >
        <i :class="[item.icon, 'text-lg']"></i>
        <span class="font-medium">{{ item.title }}</span>
      </router-link>
    </nav>
  </aside>

  <!-- Mobile overlay -->
  <div
    v-if="appStore.isSidebarOpen"
    class="fixed inset-0 bg-black/50 z-30 lg:hidden"
    @click="appStore.setSidebarOpen(false)"
  ></div>
</template>

<style scoped>
.bg-gradient-dark {
  background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
}
</style>

