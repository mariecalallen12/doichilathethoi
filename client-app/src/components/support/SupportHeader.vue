<template>
  <header class="sticky top-0 z-50 bg-gradient-to-r from-purple-900/90 via-indigo-900/90 to-blue-900/90 backdrop-blur-md border-b border-purple-500/20 shadow-lg">
    <div class="container mx-auto px-4">
      <div class="flex items-center justify-between h-16">
        <!-- Logo Section -->
        <router-link to="/" class="flex items-center space-x-3 cursor-pointer">
          <div class="relative w-12 h-12 bg-gradient-to-r from-purple-400 via-violet-500 to-indigo-500 rounded-xl flex items-center justify-center shadow-lg">
            <div class="absolute inset-0 bg-gradient-to-r from-purple-600 to-indigo-600 rounded-xl blur opacity-75"></div>
            <i class="fas fa-gem text-white text-xl relative z-10"></i>
            <div class="absolute -top-1 -right-1 w-3 h-3 bg-gradient-to-r from-yellow-400 to-orange-400 rounded-full animate-pulse"></div>
          </div>
          <div class="flex flex-col">
            <span class="text-transparent bg-gradient-to-r from-purple-300 via-violet-300 to-indigo-300 bg-clip-text font-bold text-xl tracking-wide">CMEETRADING</span>
            <span class="text-purple-400/80 text-xs font-light tracking-widest">CMEETRADING</span>
          </div>
        </router-link>

        <!-- Navigation Menu -->
        <nav class="hidden lg:flex space-x-8">
          <router-link
            v-for="item in navItems"
            :key="item.path"
            :to="item.path"
            class="relative text-purple-100 hover:text-transparent hover:bg-gradient-to-r hover:from-purple-300 hover:to-indigo-300 hover:bg-clip-text transition-all duration-300 cursor-pointer group"
            active-class="text-transparent bg-gradient-to-r from-purple-300 to-indigo-300 bg-clip-text"
          >
            <span class="relative z-10">{{ item.label }}</span>
            <div class="absolute bottom-0 left-0 w-0 h-0.5 bg-gradient-to-r from-purple-400 to-indigo-400 group-hover:w-full transition-all duration-300"></div>
          </router-link>
        </nav>

        <!-- Right Section -->
        <div class="flex items-center space-x-4">
          <router-link
            to="/login"
            class="bg-gradient-to-r from-purple-600/80 to-indigo-600/80 text-white px-4 py-2 rounded-lg border border-purple-400/30 hover:from-purple-600 hover:to-indigo-600 transition-all"
          >
            Đăng nhập
          </router-link>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
const navItems = [
  { path: '/', label: 'Trang chủ' },
  { path: '/market', label: 'Thị trường' },
  { path: '/trading', label: 'Giao dịch' },
  { path: '/education', label: 'Giáo dục' },
  { path: '/analysis', label: 'Phân tích' },
];
</script>

