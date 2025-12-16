<script setup>
import { ref, computed } from 'vue';
import Table from '../ui/Table.vue';
import Button from '../ui/Button.vue';
import api from '../../services/api';

const props = defineProps({
  loading: Boolean,
  pagination: {
    type: Object,
    default: null,
  },
});

const emit = defineEmits(['page-change', 'refresh']);

const customerBalances = ref([]);
const summary = ref({});
const searchQuery = ref('');
const currencyFilter = ref('all');
const minBalance = ref('');
const maxBalance = ref('');

const headers = [
  { key: 'userId', label: 'User ID', sortable: true },
  { key: 'email', label: 'Email', sortable: true },
  { key: 'displayName', label: 'Tên hiển thị', sortable: false },
  { key: 'balances', label: 'Số dư theo loại tiền', sortable: false },
  { key: 'totalBalanceUSD', label: 'Tổng (USD)', sortable: true },
  { key: 'lastUpdated', label: 'Cập nhật lần cuối', sortable: true },
];

const formatCurrency = (amount, currency) => {
  if (currency === 'VND') {
    return `${amount.toLocaleString('vi-VN')} ₫`;
  }
  if (currency === 'BTC') {
    return `₿${amount.toFixed(8)}`;
  }
  if (currency === 'ETH') {
    return `Ξ${amount.toFixed(6)}`;
  }
  return `${amount.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} ${currency}`;
};

const formatDate = (dateString) => {
  if (!dateString) return 'N/A';
  return new Date(dateString).toLocaleString('vi-VN');
};

const exportToCSV = () => {
  const csvHeaders = ['User ID', 'Email', 'Tên hiển thị', 'USDT', 'BTC', 'ETH', 'VND', 'USD', 'Tổng (USD)', 'Cập nhật lần cuối'];
  const csvRows = customerBalances.value.map(cb => {
    const balances = cb.balances || {};
    return [
      cb.userId,
      cb.email,
      cb.displayName || '',
      balances.USDT || 0,
      balances.BTC || 0,
      balances.ETH || 0,
      balances.VND || 0,
      balances.USD || 0,
      cb.totalBalanceUSD || 0,
      formatDate(cb.lastUpdated)
    ];
  });
  
  const csvContent = [
    csvHeaders.join(','),
    ...csvRows.map(row => row.map(cell => `"${cell}"`).join(','))
  ].join('\n');
  
  const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  const url = URL.createObjectURL(blob);
  link.setAttribute('href', url);
  link.setAttribute('download', `customer_wallet_balances_${new Date().toISOString().split('T')[0]}.csv`);
  link.style.visibility = 'hidden';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

defineExpose({
  setData: (data, summaryData) => {
    customerBalances.value = data || [];
    summary.value = summaryData || {};
  },
  getFilters: () => ({
    search: searchQuery.value || undefined,
    currency: currencyFilter.value !== 'all' ? currencyFilter.value : undefined,
    minBalance: minBalance.value ? parseFloat(minBalance.value) : undefined,
    maxBalance: maxBalance.value ? parseFloat(maxBalance.value) : undefined,
  }),
  exportToCSV,
});
</script>

<template>
  <div class="space-y-4">
    <!-- Summary Cards -->
    <div v-if="summary.totalCustomers" class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="bg-white/5 rounded-lg p-4 border border-white/10">
        <div class="text-white/60 text-sm mb-1">Tổng số khách hàng</div>
        <div class="text-2xl font-bold text-white">{{ summary.totalCustomers }}</div>
      </div>
      <div class="bg-white/5 rounded-lg p-4 border border-white/10">
        <div class="text-white/60 text-sm mb-1">Tổng số dư (USD)</div>
        <div class="text-2xl font-bold text-green-400">${{ (summary.totalBalanceUSD || 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}</div>
      </div>
      <div class="bg-white/5 rounded-lg p-4 border border-white/10">
        <div class="text-white/60 text-sm mb-1">Số dư trung bình (USD)</div>
        <div class="text-2xl font-bold text-blue-400">${{ (summary.averageBalanceUSD || 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}</div>
      </div>
      <div class="bg-white/5 rounded-lg p-4 border border-white/10">
        <div class="text-white/60 text-sm mb-1">Số loại tiền tệ</div>
        <div class="text-2xl font-bold text-purple-400">{{ (summary.currencies || []).length }}</div>
      </div>
    </div>

    <!-- Filters and Actions -->
    <div class="flex flex-col md:flex-row gap-4 items-start md:items-center justify-between">
      <div class="flex flex-wrap gap-2">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Tìm kiếm theo email hoặc tên..."
          class="px-4 py-2 rounded-lg bg-white/10 border border-white/20 text-white placeholder-white/40 min-w-[200px]"
          @keyup.enter="emit('refresh')"
        />
        <select
          v-model="currencyFilter"
          class="px-4 py-2 rounded-lg bg-white/10 border border-white/20 text-white"
          @change="emit('refresh')"
        >
          <option value="all">Tất cả loại tiền</option>
          <option value="USDT">USDT</option>
          <option value="BTC">BTC</option>
          <option value="ETH">ETH</option>
          <option value="VND">VND</option>
          <option value="USD">USD</option>
        </select>
        <input
          v-model="minBalance"
          type="number"
          placeholder="Số dư tối thiểu (USD)"
          class="px-4 py-2 rounded-lg bg-white/10 border border-white/20 text-white placeholder-white/40 w-[180px]"
          @keyup.enter="emit('refresh')"
        />
        <input
          v-model="maxBalance"
          type="number"
          placeholder="Số dư tối đa (USD)"
          class="px-4 py-2 rounded-lg bg-white/10 border border-white/20 text-white placeholder-white/40 w-[180px]"
          @keyup.enter="emit('refresh')"
        />
      </div>
      <div class="flex gap-2">
        <Button variant="primary" icon="fas fa-download" @click="exportToCSV">
          Xuất CSV
        </Button>
        <Button variant="ghost" icon="fas fa-sync-alt" @click="emit('refresh')">
          Làm mới
        </Button>
      </div>
    </div>

    <!-- Table -->
    <Table
      :headers="headers"
      :data="customerBalances"
      :loading="loading"
      :pagination="pagination"
      @page-change="emit('page-change', $event)"
    >
      <template #default="{ data }">
        <tr
          v-for="customer in data"
          :key="customer.userId"
          class="border-b border-white/5 hover:bg-white/5 transition-colors"
        >
          <td class="px-4 py-3 text-white/80 text-sm font-mono">{{ customer.userId }}</td>
          <td class="px-4 py-3 text-white/90 text-sm">{{ customer.email }}</td>
          <td class="px-4 py-3 text-white/80 text-sm">{{ customer.displayName || 'N/A' }}</td>
          <td class="px-4 py-3">
            <div class="flex flex-wrap gap-2">
              <span
                v-for="(balance, currency) in customer.balances"
                :key="currency"
                class="px-2 py-1 bg-white/10 rounded text-xs text-white/90"
              >
                {{ formatCurrency(balance, currency) }}
              </span>
              <span v-if="!customer.balances || Object.keys(customer.balances).length === 0" class="text-white/40 text-xs">
                Không có số dư
              </span>
            </div>
          </td>
          <td class="px-4 py-3 text-white font-semibold">
            ${{ (customer.totalBalanceUSD || 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}
          </td>
          <td class="px-4 py-3 text-white/60 text-sm">{{ formatDate(customer.lastUpdated) }}</td>
        </tr>
      </template>
    </Table>

    <div v-if="!loading && customerBalances.length === 0" class="text-center py-12 text-white/60">
      <i class="fas fa-wallet text-4xl mb-2"></i>
      <p>Không có dữ liệu số dư ví khách hàng</p>
    </div>
  </div>
</template>

