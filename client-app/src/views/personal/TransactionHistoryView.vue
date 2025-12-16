<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-white mb-2">Lịch Sử Giao Dịch</h1>
        <p class="text-purple-300">Xem và quản lý tất cả giao dịch</p>
      </div>
      <div class="flex items-center space-x-2">
        <button
          @click="exportToCSV"
          class="px-4 py-2 bg-gradient-to-r from-purple-500 to-indigo-500 text-white rounded-lg font-medium hover:from-purple-600 hover:to-indigo-600 transition-all"
        >
          <i class="fas fa-file-csv mr-2"></i>Xuất CSV
        </button>
        <button
          @click="exportToPDF"
          class="px-4 py-2 bg-gradient-to-r from-red-500 to-pink-500 text-white rounded-lg font-medium hover:from-red-600 hover:to-pink-600 transition-all"
        >
          <i class="fas fa-file-pdf mr-2"></i>Xuất PDF
        </button>
      </div>
    </div>

    <!-- Tabs -->
    <TransactionTabs :active-tab="activeTab" @change-tab="activeTab = $event" />

    <!-- Filter Panel -->
    <div class="grid grid-cols-1 lg:grid-cols-4 gap-6">
      <div class="lg:col-span-1">
        <FilterPanel @filter-change="handleFilterChange" />
      </div>

      <!-- Transaction List -->
      <div class="lg:col-span-3">
        <!-- Desktop Table View -->
        <div class="hidden md:block">
          <TransactionTable
            :transactions="filteredTransactions"
            :loading="isLoading"
            @view-detail="showTransactionDetail"
          />
        </div>

        <!-- Mobile Card View -->
        <div class="md:hidden">
          <TransactionCards
            :transactions="filteredTransactions"
            @view-detail="showTransactionDetail"
          />
        </div>

        <!-- Transaction Detail Modal -->
        <TransactionDetailModal
          :is-open="showDetailModal"
          :transaction="selectedTransaction"
          @close="showDetailModal = false"
          @cancel="handleCancelTransaction"
          @export="handleExportReceipt"
        />

        <!-- Pagination -->
        <div v-if="pagination.total > 0" class="mt-6 flex items-center justify-between">
          <div class="text-purple-300 text-sm">
            Hiển thị {{ (pagination.page - 1) * pagination.limit + 1 }} - 
            {{ Math.min(pagination.page * pagination.limit, pagination.total) }} 
            của {{ pagination.total }}
          </div>
          <div class="flex space-x-2">
            <button
              @click="previousPage"
              :disabled="pagination.page === 1"
              class="px-4 py-2 bg-slate-800/50 border border-purple-500/30 rounded-lg text-white hover:bg-purple-500/20 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Trước
            </button>
            <button
              @click="nextPage"
              :disabled="pagination.page * pagination.limit >= pagination.total"
              class="px-4 py-2 bg-slate-800/50 border border-purple-500/30 rounded-lg text-white hover:bg-purple-500/20 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Sau
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useTransactionsStore } from '../../stores/transactions';
import TransactionTabs from '../../components/personal/transactions/TransactionTabs.vue';
import FilterPanel from '../../components/personal/transactions/FilterPanel.vue';
import TransactionTable from '../../components/personal/transactions/TransactionTable.vue';
import TransactionCards from '../../components/personal/transactions/TransactionCards.vue';
import { exportTransactionsToCSV, exportTransactionsToPDF } from '../../utils/export';

const transactionsStore = useTransactionsStore();
const activeTab = ref('all');
const filters = ref({});
const isLoading = computed(() => transactionsStore.isLoading);
const pagination = computed(() => transactionsStore.pagination);
const showDetailModal = ref(false);
const selectedTransaction = ref(null);

// Fetch transactions on mount
onMounted(async () => {
  try {
    await transactionsStore.fetchTransactions();
  } catch (error) {
    console.error('Error fetching transactions:', error);
  }
});

const filteredTransactions = computed(() => {
  let transactions = transactionsStore.transactions;

  if (activeTab.value === 'deposits') {
    transactions = transactions.filter(t => t.type === 'deposit' || t.type === 'withdrawal');
  } else if (activeTab.value === 'orders') {
    transactions = transactions.filter(t => t.type === 'trading' || t.type === 'order');
  }

  // Apply filters
  if (filters.value.type) {
    transactions = transactions.filter(t => t.type === filters.value.type);
  }
  if (filters.value.status) {
    transactions = transactions.filter(t => t.status === filters.value.status);
  }
  if (filters.value.currency) {
    transactions = transactions.filter(t => t.currency === filters.value.currency);
  }
  if (filters.value.search) {
    const search = filters.value.search.toLowerCase();
    transactions = transactions.filter(t =>
      t.id.toLowerCase().includes(search) ||
      (t.description && t.description.toLowerCase().includes(search))
    );
  }

  return transactions;
});

const handleFilterChange = async (filterData) => {
  filters.value = filterData;
  await transactionsStore.fetchTransactions(filterData);
};

const showTransactionDetail = (transaction) => {
  selectedTransaction.value = transaction;
  showDetailModal.value = true;
};

const handleCancelTransaction = async (transaction) => {
  try {
    // Call API to cancel transaction
    const response = await fetch(`/api/client/transactions/${transaction.id}/cancel`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
      },
    });
    
    if (response.ok) {
      await transactionsStore.fetchTransactions(filters.value);
      showDetailModal.value = false;
      alert('Đã hủy giao dịch thành công');
    }
  } catch (error) {
    console.error('Failed to cancel transaction:', error);
    alert('Không thể hủy giao dịch. Vui lòng thử lại.');
  }
};

const handleExportReceipt = (transaction) => {
  // Export single transaction receipt
  exportTransactionsToPDF([transaction], {
    filename: `transaction-${transaction.id}`,
    title: 'Biên Lai Giao Dịch',
  });
};

const exportToCSV = () => {
  try {
    exportTransactionsToCSV(filteredTransactions.value, {
      filename: 'transactions',
    });
  } catch (error) {
    console.error('Failed to export to CSV:', error);
    alert('Không thể xuất file CSV. Vui lòng thử lại.');
  }
};

const exportToPDF = async () => {
  try {
    await exportTransactionsToPDF(filteredTransactions.value, {
      filename: 'transactions',
      title: 'Lịch Sử Giao Dịch',
    });
  } catch (error) {
    console.error('Failed to export to PDF:', error);
    if (error.message.includes('jsPDF')) {
      alert('PDF export cần cài đặt thư viện jsPDF. Vui lòng liên hệ admin.');
    } else {
      alert('Không thể xuất file PDF. Vui lòng thử lại.');
    }
  }
};

const previousPage = async () => {
  if (pagination.value.page > 1) {
    transactionsStore.pagination.page--;
    await transactionsStore.fetchTransactions(filters.value);
  }
};

const nextPage = async () => {
  if (pagination.value.page * pagination.value.limit < pagination.value.total) {
    transactionsStore.pagination.page++;
    await transactionsStore.fetchTransactions(filters.value);
  }
};

onMounted(async () => {
  await transactionsStore.fetchTransactions();
});
</script>

