<script setup>
import { computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../../store/auth';
import { useAppStore } from '../../store/app';

const router = useRouter();
const authStore = useAuthStore();
const appStore = useAppStore();

const currentUser = computed(() => authStore.currentUser);

const handleLogout = async () => {
  await authStore.logout();
  router.push('/login');
};

const toggleSidebar = () => {
  appStore.toggleSidebar();
};
</script>

<template>
  <header class="sticky top-0 z-30 bg-gradient-dark border-b border-white/10">
    <div class="flex items-center justify-between px-4 lg:px-6 py-4">
      <!-- Left: Menu toggle & Breadcrumb -->
      <div class="flex items-center gap-4">
        <button
          @click="toggleSidebar"
          class="lg:hidden p-2 text-white/70 hover:text-white hover:bg-white/10 rounded-lg transition-all"
        >
          <i class="fas fa-bars text-xl"></i>
        </button>
        <slot name="breadcrumb" />
      </div>

      <!-- Right: User menu -->
      <div class="flex items-center gap-4">
        <!-- Notifications -->
        <button
          class="relative p-2 text-white/70 hover:text-white hover:bg-white/10 rounded-lg transition-all"
        >
          <i class="fas fa-bell text-xl"></i>
          <span
            class="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"
          ></span>
        </button>

        <!-- User dropdown -->
        <div class="relative group">
          <button
            class="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-white/10 transition-all"
          >
            <div class="w-8 h-8 bg-gradient-button rounded-full flex items-center justify-center">
              <i class="fas fa-user text-white text-sm"></i>
            </div>
            <div class="hidden md:block text-left">
              <p class="text-sm font-medium text-white">
                {{ currentUser?.full_name || currentUser?.email || 'Admin' }}
              </p>
              <p class="text-xs text-white/60">{{ currentUser?.role || 'ADMIN' }}</p>
            </div>
            <i class="fas fa-chevron-down text-white/60 text-xs"></i>
          </button>

          <!-- Dropdown menu -->
          <div
            class="absolute right-0 mt-2 w-48 glass-effect rounded-lg shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all"
          >
            <div class="p-2">
              <router-link
                to="/profile"
                class="flex items-center gap-3 px-3 py-2 rounded-lg text-white/70 hover:text-white hover:bg-white/10 transition-all"
              >
                <i class="fas fa-user-circle"></i>
                <span>Hồ sơ</span>
              </router-link>
              <router-link
                to="/settings"
                class="flex items-center gap-3 px-3 py-2 rounded-lg text-white/70 hover:text-white hover:bg-white/10 transition-all"
              >
                <i class="fas fa-cog"></i>
                <span>Cài đặt</span>
              </router-link>
              <div class="border-t border-white/10 my-1"></div>
              <button
                @click="handleLogout"
                class="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-red-300 hover:text-red-200 hover:bg-red-500/10 transition-all"
              >
                <i class="fas fa-sign-out-alt"></i>
                <span>Đăng xuất</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </header>
</template>

<style scoped>
.bg-gradient-dark {
  background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
}

.glass-effect {
  background: rgba(15, 23, 42, 0.95);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}
</style>

