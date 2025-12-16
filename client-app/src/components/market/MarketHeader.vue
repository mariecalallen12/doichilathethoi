<template>
  <header class="sticky top-0 z-50 bg-gradient-to-r from-purple-900/90 via-indigo-900/90 to-blue-900/90 backdrop-blur-md border-b border-purple-500/20 shadow-lg">
    <div class="container mx-auto px-4">
      <div class="flex items-center justify-between h-16">
        <!-- Logo Section -->
        <div class="flex items-center space-x-3 cursor-pointer" @click="goHome">
          <div class="relative w-12 h-12 bg-gradient-to-r from-purple-400 via-violet-500 to-indigo-500 rounded-xl flex items-center justify-center shadow-lg">
            <div class="absolute inset-0 bg-gradient-to-r from-purple-600 to-indigo-600 rounded-xl blur opacity-75"></div>
            <i class="fas fa-gem text-white text-xl relative z-10"></i>
            <div class="absolute -top-1 -right-1 w-3 h-3 bg-gradient-to-r from-yellow-400 to-orange-400 rounded-full animate-pulse"></div>
          </div>
          <div class="flex flex-col">
            <span class="text-transparent bg-gradient-to-r from-purple-300 via-violet-300 to-indigo-300 bg-clip-text font-bold text-xl tracking-wide">CMEETRADING</span>
            <span class="text-purple-400/80 text-xs font-light tracking-widest">CMEETRADING</span>
          </div>
        </div>

        <!-- Navigation Menu -->
        <nav class="hidden lg:flex space-x-8">
          <router-link
            v-for="item in navItems"
            :key="item.path"
            :to="item.path"
            class="relative text-purple-100 hover:text-transparent hover:bg-gradient-to-r hover:from-purple-300 hover:to-indigo-300 hover:bg-clip-text transition-all duration-300 cursor-pointer group"
            :class="{
              'text-transparent bg-gradient-to-r from-purple-300 to-indigo-300 bg-clip-text': item.path === '/market'
            }"
          >
            <span class="relative z-10">{{ item.label }}</span>
            <div 
              class="absolute bottom-0 left-0 h-0.5 bg-gradient-to-r from-purple-400 to-indigo-400 transition-all duration-300"
              :class="item.path === '/market' ? 'w-full' : 'w-0 group-hover:w-full'"
            ></div>
          </router-link>
        </nav>

        <!-- Right Section: Notifications & User Profile -->
        <div class="flex items-center space-x-4">
          <!-- Notifications Bell -->
          <button
            class="relative p-2 text-purple-100 hover:text-white transition-colors"
            @click="toggleNotifications"
          >
            <i class="fas fa-bell text-xl"></i>
            <span
              v-if="notificationCount > 0"
              class="absolute top-0 right-0 w-5 h-5 bg-red-500 rounded-full flex items-center justify-center text-xs text-white font-bold"
            >
              {{ notificationCount }}
            </span>
          </button>

          <!-- User Profile Dropdown -->
          <div class="relative" ref="profileDropdownRef">
            <button
              class="flex items-center space-x-2 text-purple-100 hover:text-white transition-colors"
              @click="toggleProfileDropdown"
            >
              <div class="w-10 h-10 rounded-full bg-gradient-to-r from-purple-400 to-indigo-400 flex items-center justify-center">
                <i class="fas fa-user text-white"></i>
              </div>
              <div class="hidden md:block text-left">
                <div class="text-sm font-medium text-white">Nguyễn Minh Anh</div>
                <div class="text-xs text-purple-300">VIP Trader</div>
              </div>
              <i class="fas fa-chevron-down text-xs"></i>
            </button>

            <!-- Dropdown Menu -->
            <div
              v-if="showProfileDropdown"
              class="absolute right-0 mt-2 w-48 bg-slate-800/95 backdrop-blur-md rounded-lg shadow-xl border border-purple-500/20 py-2 z-50"
            >
              <router-link
                to="/personal/profile"
                class="block px-4 py-2 text-sm text-purple-100 hover:bg-purple-500/20 transition-colors"
                @click="showProfileDropdown = false"
              >
                <i class="fas fa-user mr-2"></i>Hồ sơ
              </router-link>
              <router-link
                to="/personal/dashboard"
                class="block px-4 py-2 text-sm text-purple-100 hover:bg-purple-500/20 transition-colors"
                @click="showProfileDropdown = false"
              >
                <i class="fas fa-home mr-2"></i>Trang chủ
              </router-link>
              <button
                class="block w-full text-left px-4 py-2 text-sm text-red-400 hover:bg-red-500/20 transition-colors"
                @click="handleLogout"
              >
                <i class="fas fa-sign-out-alt mr-2"></i>Đăng xuất
              </button>
            </div>
          </div>

          <!-- Mobile Menu Button -->
          <button
            class="lg:hidden text-white text-2xl"
            @click="toggleMobileMenu"
          >
            <i :class="mobileMenuOpen ? 'fas fa-times' : 'fas fa-bars'"></i>
          </button>
        </div>
      </div>

      <!-- Mobile Menu -->
      <div
        v-if="mobileMenuOpen"
        class="lg:hidden border-t border-purple-500/20 bg-slate-950/90 backdrop-blur-md py-4"
      >
        <div class="flex flex-col space-y-2">
          <router-link
            v-for="item in navItems"
            :key="item.path"
            :to="item.path"
            class="px-4 py-2 text-purple-100 hover:bg-purple-500/20 transition-colors"
            :class="{ 'bg-purple-500/20': item.path === '/market' }"
            @click="mobileMenuOpen = false"
          >
            {{ item.label }}
          </router-link>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const showProfileDropdown = ref(false);
const mobileMenuOpen = ref(false);
const notificationCount = ref(3);
const profileDropdownRef = ref(null);

const navItems = [
  { path: '/', label: 'Trang chủ' },
  { path: '/market', label: 'Thị trường' },
  { path: '/trading', label: 'Giao dịch' },
  { path: '/education', label: 'Giáo dục' },
  { path: '/analysis', label: 'Phân tích' },
];

const goHome = () => {
  router.push('/');
};

const toggleProfileDropdown = () => {
  showProfileDropdown.value = !showProfileDropdown.value;
};

const toggleMobileMenu = () => {
  mobileMenuOpen.value = !mobileMenuOpen.value;
};

const toggleNotifications = () => {
  console.log('Toggle notifications');
};

const handleLogout = () => {
  router.push('/login');
};

// Close dropdown when clicking outside
const handleClickOutside = (event) => {
  if (profileDropdownRef.value && !profileDropdownRef.value.contains(event.target)) {
    showProfileDropdown.value = false;
  }
};

onMounted(() => {
  document.addEventListener('click', handleClickOutside);
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
});
</script>

