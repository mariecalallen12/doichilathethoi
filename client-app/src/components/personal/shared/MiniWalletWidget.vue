<template>
  <transition name="fade">
    <div
      v-if="isAuthenticated"
      class="fixed bottom-4 right-4 z-40 w-72 max-w-[calc(100vw-2rem)] bg-slate-900/90 border border-purple-500/30 rounded-2xl shadow-2xl backdrop-blur-md p-4 space-y-3"
    >
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-2">
          <div class="w-10 h-10 rounded-xl bg-gradient-to-r from-purple-500 to-indigo-500 flex items-center justify-center">
            <i class="fas fa-wallet text-white"></i>
          </div>
          <div>
            <p class="text-xs text-purple-200">Số dư khả dụng</p>
            <p class="text-lg font-semibold text-white">{{ formattedAvailable }}</p>
          </div>
        </div>
        <button
          class="text-purple-200 hover:text-white"
          @click="toggleCollapse"
          @keydown.enter.prevent="toggleCollapse"
          @keydown.space.prevent="toggleCollapse"
          aria-label="Thu gọn ví"
          :aria-expanded="!collapsed"
          type="button"
        >
          <i :class="collapsed ? 'fas fa-chevron-up' : 'fas fa-chevron-down'"></i>
        </button>
      </div>

      <div v-if="!collapsed" class="space-y-3">
        <div
          v-if="accountStore.isLoading"
          class="bg-slate-800/70 rounded-lg p-3 text-sm text-purple-100 animate-pulse"
        >
          <div class="h-4 bg-slate-700/80 rounded w-2/3 mb-2"></div>
          <div class="h-4 bg-slate-700/60 rounded w-1/2"></div>
        </div>
        <div v-else class="bg-slate-800/70 rounded-lg p-3 text-sm text-purple-100">
          <div class="flex items-center justify-between">
            <span>Đang khóa</span>
            <span class="font-semibold">{{ formattedLocked }}</span>
          </div>
          <div class="flex items-center justify-between mt-1">
            <span>Chờ xử lý</span>
            <span class="font-semibold">{{ formattedPending }}</span>
          </div>
        </div>

        <div class="grid grid-cols-3 gap-2">
          <router-link
            to="/personal/deposit"
            class="btn-action"
          >
            <i class="fas fa-plus mr-1"></i>
            Nạp
          </router-link>
          <router-link
            to="/personal/withdraw"
            class="btn-action"
          >
            <i class="fas fa-minus mr-1"></i>
            Rút
          </router-link>
          <router-link
            to="/trading"
            class="btn-action"
          >
            <i class="fas fa-chart-line mr-1"></i>
            Trading
          </router-link>
        </div>

        <div class="text-xs text-purple-200/80">
          <span class="font-semibold text-purple-100">Mẹo:</span> Bạn có thể dùng số dư ví để giao dịch nhanh.
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue';
import { useAccountStore } from '../../../stores/account';
import { useRouter } from 'vue-router';

const accountStore = useAccountStore();
const router = useRouter();
const collapsed = ref(false);
const authToken = ref(localStorage.getItem('auth_token'));

const isAuthenticated = computed(() => !!authToken.value);

const formattedAvailable = computed(() =>
  accountStore.balance.available?.toLocaleString('vi-VN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }) || '0.00'
);

const formattedLocked = computed(() =>
  accountStore.balance.locked?.toLocaleString('vi-VN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }) || '0.00'
);

const formattedPending = computed(() =>
  accountStore.balance.pending?.toLocaleString('vi-VN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }) || '0.00'
);

const toggleCollapse = () => {
  collapsed.value = !collapsed.value;
};

onMounted(async () => {
  // Check authentication trước khi gọi API
  if (!isAuthenticated.value) {
    return; // Không gọi API nếu chưa đăng nhập
  }
  
  try {
    // Chỉ fetch nếu chưa có dữ liệu để tránh gọi trùng với overview
    if (
      !accountStore.currencies?.crypto &&
      !accountStore.currencies?.fiat &&
      !accountStore.balance?.available
    ) {
      await accountStore.fetchBalance();
    }
  } catch (error) {
    // Suppress 401 errors (expected khi token hết hạn)
    if (error.response?.status !== 401) {
      console.error('MiniWalletWidget: cannot fetch balance', error);
    }
  }
});

router.afterEach(() => {
  authToken.value = localStorage.getItem('auth_token');
});

if (typeof window !== 'undefined') {
  window.addEventListener('storage', () => {
    authToken.value = localStorage.getItem('auth_token');
  });
}
</script>

<style scoped>
.btn-action {
  @apply px-3 py-2 rounded-lg text-sm font-semibold text-white text-center bg-gradient-to-r from-purple-500 to-indigo-500 hover:from-purple-600 hover:to-indigo-600 transition-all shadow;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(8px);
}
</style>
