<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900/20 to-slate-900">
    <!-- Sidebar -->
    <aside
      :class="[
        'fixed top-0 left-0 z-40 h-screen transition-transform',
        'lg:translate-x-0',
        mobileMenuOpen ? 'translate-x-0' : '-translate-x-full',
        'w-64 bg-slate-800/95 backdrop-blur-md border-r border-purple-500/20'
      ]"
    >
      <div class="flex flex-col h-full">
        <!-- Logo Section -->
        <div class="p-6 border-b border-purple-500/20">
          <div class="flex items-center space-x-3">
            <div class="relative w-10 h-10 bg-gradient-to-r from-purple-400 via-violet-500 to-indigo-500 rounded-lg flex items-center justify-center overflow-hidden">
              <div class="absolute inset-0 bg-gradient-to-r from-purple-600 to-indigo-600 rounded-xl blur opacity-75"></div>
              <i class="fas fa-user-circle text-white text-xl relative z-10"></i>
            </div>
            <div>
              <div class="text-white font-bold text-lg">Khu Vực Cá Nhân</div>
              <div class="text-purple-300 text-xs">CMEETRADING</div>
            </div>
          </div>
        </div>

        <!-- Navigation Menu -->
        <nav class="flex-1 overflow-y-auto p-4 space-y-2">
          <router-link
            v-for="item in menuItems"
            :key="item.path"
            :to="item.path"
            :class="[
              'flex items-center space-x-3 px-4 py-3 rounded-lg transition-all duration-300',
              'text-purple-100 hover:bg-purple-500/20 hover:text-white',
              $route.path === item.path ? 'bg-purple-500/30 text-white border-l-4 border-purple-400' : ''
            ]"
            @click="mobileMenuOpen = false"
          >
            <i :class="[item.icon, 'text-lg']"></i>
            <span class="font-medium">{{ item.label }}</span>
          </router-link>
        </nav>

        <!-- User Info Footer -->
        <div class="p-4 border-t border-purple-500/20">
          <div class="flex items-center space-x-3">
            <div class="w-10 h-10 rounded-full bg-gradient-to-r from-purple-400 to-indigo-400 flex items-center justify-center">
              <i class="fas fa-user text-white"></i>
            </div>
            <div class="flex-1 min-w-0">
              <div class="text-white text-sm font-medium truncate">Nguyễn Minh Anh</div>
              <div class="text-purple-300 text-xs truncate">VIP Member</div>
            </div>
          </div>
        </div>
      </div>
    </aside>

    <!-- Overlay for mobile -->
    <div
      v-if="mobileMenuOpen"
      class="fixed inset-0 bg-black/50 z-30 lg:hidden"
      @click="mobileMenuOpen = false"
    ></div>

    <!-- Main Content -->
    <div class="lg:pl-64">
      <!-- Top Header -->
      <header class="sticky top-0 z-30 bg-slate-800/95 backdrop-blur-md border-b border-purple-500/20">
        <div class="px-4 sm:px-6 lg:px-8">
          <div class="flex items-center justify-between h-16">
            <!-- Mobile Menu Button -->
            <button
              @click="mobileMenuOpen = !mobileMenuOpen"
              class="lg:hidden p-2 text-purple-100 hover:text-white"
            >
              <i class="fas fa-bars text-xl"></i>
            </button>

            <!-- Breadcrumb -->
            <nav class="hidden md:flex items-center space-x-2 text-sm">
              <router-link to="/personal/dashboard" class="text-purple-300 hover:text-white">
                Khu Vực Cá Nhân
              </router-link>
              <i class="fas fa-chevron-right text-purple-500 text-xs"></i>
              <span class="text-white">{{ currentPageTitle }}</span>
            </nav>

            <!-- Right Section -->
            <div class="flex items-center space-x-4">
              <!-- Notifications -->
              <button class="relative p-2 text-purple-100 hover:text-white transition-colors">
                <i class="fas fa-bell text-xl"></i>
                <span
                  v-if="notificationCount > 0"
                  class="absolute top-0 right-0 w-5 h-5 bg-red-500 rounded-full flex items-center justify-center text-xs text-white font-bold"
                >
                  {{ notificationCount }}
                </span>
              </button>

              <!-- Quick Actions -->
              <div class="hidden sm:flex items-center space-x-2">
                <router-link
                  to="/personal/deposit"
                  class="px-4 py-2 bg-gradient-to-r from-green-500 to-emerald-500 text-white rounded-lg text-sm font-medium hover:from-green-600 hover:to-emerald-600 transition-all"
                >
                  <i class="fas fa-plus mr-2"></i>Nạp Tiền
                </router-link>
                <router-link
                  to="/personal/withdraw"
                  class="px-4 py-2 bg-gradient-to-r from-blue-500 to-cyan-500 text-white rounded-lg text-sm font-medium hover:from-blue-600 hover:to-cyan-600 transition-all"
                >
                  <i class="fas fa-minus mr-2"></i>Rút Tiền
                </router-link>
              </div>
            </div>
          </div>
        </div>
      </header>

      <!-- Page Content -->
      <main class="p-4 sm:p-6 lg:p-8">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();
const mobileMenuOpen = ref(false);
const notificationCount = ref(3);

const menuItems = [
  {
    path: '/personal/overview',
    label: 'Trang Cá Nhân',
    icon: 'fas fa-user-circle',
  },
  {
    path: '/personal/wallet',
    label: 'Ví Điện Tử',
    icon: 'fas fa-wallet',
  },
  {
    path: '/personal/deposit',
    label: 'Nạp Tiền',
    icon: 'fas fa-arrow-down',
  },
  {
    path: '/personal/withdraw',
    label: 'Rút Tiền',
    icon: 'fas fa-arrow-up',
  },
  {
    path: '/personal/transactions',
    label: 'Lịch Sử Giao Dịch',
    icon: 'fas fa-history',
  },
  {
    path: '/personal/rates',
    label: 'Tỷ Giá Hối Đoái',
    icon: 'fas fa-exchange-alt',
  },
  {
    path: '/personal/profile',
    label: 'Thông Tin Cá Nhân',
    icon: 'fas fa-user',
  },
];

const currentPageTitle = computed(() => {
  const item = menuItems.find(item => item.path === route.path);
  return item ? item.label : 'Khu Vực Cá Nhân';
});
</script>

<style scoped>
/* Custom scrollbar for sidebar */
nav::-webkit-scrollbar {
  width: 6px;
}

nav::-webkit-scrollbar-track {
  background: rgba(30, 41, 59, 0.5);
}

nav::-webkit-scrollbar-thumb {
  background: rgba(139, 92, 246, 0.5);
  border-radius: 3px;
}

nav::-webkit-scrollbar-thumb:hover {
  background: rgba(139, 92, 246, 0.7);
}
</style>

