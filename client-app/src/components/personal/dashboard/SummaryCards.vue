<template>
  <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
    <!-- Total Balance Card -->
    <div class="glass-panel rounded-lg p-6 bg-gradient-to-br from-purple-500/20 to-indigo-500/20 border border-purple-500/30">
      <div class="flex items-center justify-between mb-4">
        <div class="w-12 h-12 bg-purple-500/30 rounded-lg flex items-center justify-center">
          <i class="fas fa-wallet text-purple-300 text-xl"></i>
        </div>
        <div class="text-purple-300 text-xs">Tổng số dư</div>
      </div>
      <div class="font-orbitron text-3xl font-bold text-white mb-2">
        {{ formatVND(totalBalance) }}
      </div>
      <div class="text-purple-300 text-xs">Tất cả tài sản</div>
    </div>

    <!-- Available Balance Card -->
    <div class="glass-panel rounded-lg p-6 bg-gradient-to-br from-green-500/20 to-emerald-500/20 border border-green-500/30">
      <div class="flex items-center justify-between mb-4">
        <div class="w-12 h-12 bg-green-500/30 rounded-lg flex items-center justify-center">
          <i class="fas fa-check-circle text-green-300 text-xl"></i>
        </div>
        <div class="text-green-300 text-xs">Khả dụng</div>
      </div>
      <div class="font-orbitron text-3xl font-bold text-white mb-2">
        {{ formatVND(availableBalance) }}
      </div>
      <div class="text-green-300 text-xs">Có thể rút/giao dịch ngay</div>
    </div>

    <!-- Pending Balance Card -->
    <div class="glass-panel rounded-lg p-6 bg-gradient-to-br from-blue-500/20 to-cyan-500/20 border border-blue-500/30">
      <div class="flex items-center justify-between mb-4">
        <div class="w-12 h-12 bg-blue-500/30 rounded-lg flex items-center justify-center">
          <i class="fas fa-clock text-blue-300 text-xl"></i>
        </div>
        <div class="text-blue-300 text-xs">Chờ xử lý</div>
      </div>
      <div class="font-orbitron text-3xl font-bold text-white mb-2">
        {{ formatVND(pendingBalance) }}
      </div>
      <div class="text-blue-300 text-xs">Đang trong quá trình nạp/rút</div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useAccountStore } from '../../../stores/account';
import { formatNumber } from '../../../services/utils/formatters';
import { clientApi } from '../../../services/api/client';

const accountStore = useAccountStore();

// Các giá trị mặc định lấy từ accountStore (fallback)
const baseTotal = computed(() => accountStore.equity || 0);
const baseAvailable = computed(() => accountStore.balance?.available || 0);
const basePending = computed(() => accountStore.balance?.pending || 0);

// Cho phép SummaryCards tự gọi dashboard một lần nếu accountStore chưa có dữ liệu chi tiết
const totalBalance = computed(() => {
  return baseTotal.value;
});

const availableBalance = computed(() => {
  return baseAvailable.value;
});

const pendingBalance = computed(() => {
  return basePending.value;
});

const formatVND = (amount) => {
  return `${formatNumber(amount)} ₫`;
};
</script>
