<template>
  <div class="glass-panel rounded-lg p-6">
    <h3 class="text-lg font-bold text-white mb-4 flex items-center">
      <i class="fas fa-filter mr-2 text-purple-400"></i>
      Lọc Giao Dịch
    </h3>

    <div class="space-y-4">
      <!-- Transaction Type -->
      <div>
        <label class="text-purple-300 text-sm mb-2 block">Loại giao dịch</label>
        <select
          v-model="filters.type"
          class="w-full px-4 py-2 bg-slate-800/50 border border-purple-500/30 rounded-lg text-white focus:border-purple-500/50 focus:outline-none"
        >
          <option value="">Tất cả</option>
          <option value="deposit">Nạp tiền</option>
          <option value="withdrawal">Rút tiền</option>
          <option value="trading">Giao dịch</option>
          <option value="fee">Phí</option>
        </select>
      </div>

      <!-- Status -->
      <div>
        <label class="text-purple-300 text-sm mb-2 block">Trạng thái</label>
        <select
          v-model="filters.status"
          class="w-full px-4 py-2 bg-slate-800/50 border border-purple-500/30 rounded-lg text-white focus:border-purple-500/50 focus:outline-none"
        >
          <option value="">Tất cả</option>
          <option value="completed">Hoàn thành</option>
          <option value="pending">Chờ xử lý</option>
          <option value="processing">Đang xử lý</option>
          <option value="failed">Thất bại</option>
          <option value="cancelled">Đã hủy</option>
        </select>
      </div>

      <!-- Currency -->
      <div>
        <label class="text-purple-300 text-sm mb-2 block">Tiền tệ</label>
        <select
          v-model="filters.currency"
          class="w-full px-4 py-2 bg-slate-800/50 border border-purple-500/30 rounded-lg text-white focus:border-purple-500/50 focus:outline-none"
        >
          <option value="">Tất cả</option>
          <option value="USDT">USDT</option>
          <option value="BTC">BTC</option>
          <option value="ETH">ETH</option>
          <option value="VND">VND</option>
          <option value="USD">USD</option>
        </select>
      </div>

      <!-- Date Range -->
      <div>
        <label class="text-purple-300 text-sm mb-2 block">Khoảng thời gian</label>
        <DateRangePicker v-model="dateRange" />
      </div>

      <!-- Amount Range -->
      <div>
        <label class="text-purple-300 text-sm mb-2 block">Khoảng số tiền</label>
        <div class="grid grid-cols-2 gap-3">
          <input
            v-model.number="filters.minAmount"
            type="number"
            placeholder="Tối thiểu"
            class="px-4 py-2 bg-slate-800/50 border border-purple-500/30 rounded-lg text-white placeholder-purple-300/50 focus:border-purple-500/50 focus:outline-none"
          />
          <input
            v-model.number="filters.maxAmount"
            type="number"
            placeholder="Tối đa"
            class="px-4 py-2 bg-slate-800/50 border border-purple-500/30 rounded-lg text-white placeholder-purple-300/50 focus:border-purple-500/50 focus:outline-none"
          />
        </div>
      </div>

      <!-- Search -->
      <div>
        <label class="text-purple-300 text-sm mb-2 block">Tìm kiếm</label>
        <input
          v-model="filters.search"
          type="text"
          placeholder="ID, mô tả..."
          class="w-full px-4 py-2 bg-slate-800/50 border border-purple-500/30 rounded-lg text-white placeholder-purple-300/50 focus:border-purple-500/50 focus:outline-none"
        />
      </div>

      <!-- Actions -->
      <div class="flex space-x-3 pt-4">
        <button
          @click="applyFilters"
          class="flex-1 px-4 py-2 bg-gradient-to-r from-purple-500 to-indigo-500 text-white rounded-lg font-medium hover:from-purple-600 hover:to-indigo-600 transition-all"
        >
          Áp dụng
        </button>
        <button
          @click="resetFilters"
          class="px-4 py-2 bg-slate-700 text-white rounded-lg hover:bg-slate-600 transition-all"
        >
          Đặt lại
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';
import DateRangePicker from '../shared/DateRangePicker.vue';

const emit = defineEmits(['filter-change']);

const filters = ref({
  type: '',
  status: '',
  currency: '',
  minAmount: null,
  maxAmount: null,
  search: '',
});

const dateRange = ref({ start: null, end: null });

const applyFilters = () => {
  const filterData = {
    ...filters.value,
    startDate: dateRange.value.start,
    endDate: dateRange.value.end,
  };
  emit('filter-change', filterData);
};

const resetFilters = () => {
  filters.value = {
    type: '',
    status: '',
    currency: '',
    minAmount: null,
    maxAmount: null,
    search: '',
  };
  dateRange.value = { start: null, end: null };
  applyFilters();
};

watch([filters, dateRange], () => {
  // Auto-apply filters with debounce could be added here
}, { deep: true });
</script>

