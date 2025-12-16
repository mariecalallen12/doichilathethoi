<template>
  <div class="space-y-8">
    <!-- Header -->
    <section>
      <h1 class="text-3xl font-bold text-white mb-2">Trang Cá Nhân</h1>
      <p class="text-purple-300">Tổng hợp ví, giao dịch, bảo mật và hồ sơ trong một nơi</p>
    </section>

    <!-- Summary & Quick Actions -->
    <section class="space-y-6">
      <SummaryCards />
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div class="lg:col-span-2 space-y-6">
          <BalanceOverview />
          <StatsSummary />
        </div>
        <div class="lg:col-span-1">
          <QuickActions />
          <SecurityPanel class="mt-6" />
        </div>
      </div>
    </section>

    <!-- Wallet & Trading Balance -->
    <section class="glass-panel rounded-lg p-6 space-y-4">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-xl font-bold text-white">Ví Điện Tử & Dùng Cho Trading</h2>
          <p class="text-purple-300 text-sm">Xem nhanh số dư và giá trị danh mục</p>
        </div>
        <div class="text-sm text-purple-200">
          Số dư khả dụng: <span class="font-semibold text-white">{{ formattedAvailable }}</span>
        </div>
      </div>
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div class="lg:col-span-2">
          <CurrencyList />
        </div>
        <div class="lg:col-span-1 space-y-4">
          <PortfolioAnalytics />
        </div>
      </div>
    </section>

    <!-- Deposit & Withdraw -->
    <section class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div class="space-y-4">
        <div class="flex items-center justify-between">
          <div>
            <h2 class="text-xl font-bold text-white">Nạp Tiền</h2>
            <p class="text-purple-300 text-sm">Chọn phương thức nạp phù hợp</p>
          </div>
        </div>
        <div class="glass-panel rounded-lg p-4">
          <div class="flex space-x-1 mb-4 overflow-x-auto">
            <button
              v-for="tab in depositTabs"
              :key="tab.id"
              @click="activeDepositTab = tab.id"
              :class="[
                'px-3 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-all',
                activeDepositTab === tab.id
                  ? 'bg-gradient-to-r from-purple-500 to-indigo-500 text-white'
                  : 'text-purple-300 hover:text-white hover:bg-purple-500/10'
              ]"
            >
              <i :class="[tab.icon, 'mr-2']"></i>{{ tab.label }}
            </button>
          </div>
          <div>
            <CryptoDeposit v-if="activeDepositTab === 'crypto'" />
            <VietQRDeposit v-if="activeDepositTab === 'vietqr'" />
            <OnlinePaymentDeposit v-if="activeDepositTab === 'online'" />
          </div>
        </div>
      </div>

      <div class="space-y-4">
        <div class="flex items-center justify-between">
          <div>
            <h2 class="text-xl font-bold text-white">Rút Tiền</h2>
            <p class="text-purple-300 text-sm">Quản lý yêu cầu rút tiền</p>
          </div>
        </div>
        <div class="glass-panel rounded-lg p-4 space-y-6">
          <WithdrawForm />
          <WithdrawHistory />
        </div>
      </div>
    </section>

    <!-- Transactions & Rates -->
    <section class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="lg:col-span-2 glass-panel rounded-lg p-4 space-y-4">
        <div class="flex items-center justify-between">
          <div>
            <h2 class="text-xl font-bold text-white">Lịch Sử Giao Dịch</h2>
            <p class="text-purple-300 text-sm">Theo dõi và lọc giao dịch nạp/rút/trading</p>
          </div>
          <div class="flex items-center space-x-2">
            <button
              @click="exportToCSV"
              class="px-3 py-2 bg-gradient-to-r from-purple-500 to-indigo-500 text-white rounded-lg text-sm hover:from-purple-600 hover:to-indigo-600 transition-all"
            >
              <i class="fas fa-file-csv mr-1"></i>CSV
            </button>
            <button
              @click="exportToPDF"
              class="px-3 py-2 bg-gradient-to-r from-red-500 to-pink-500 text-white rounded-lg text-sm hover:from-red-600 hover:to-pink-600 transition-all"
            >
              <i class="fas fa-file-pdf mr-1"></i>PDF
            </button>
          </div>
        </div>
        <TransactionTabs :active-tab="activeTab" @change-tab="activeTab = $event" />
        <FilterPanel @filter-change="handleFilterChange" />
        <TransactionCards
          :transactions="filteredTransactions"
          @view-detail="showTransactionDetail"
        />
        <TransactionDetailModal
          :is-open="showDetailModal"
          :transaction="selectedTransaction"
          @close="showDetailModal = false"
          @cancel="handleCancelTransaction"
          @export="handleExportReceipt"
        />
      </div>

      <div class="lg:col-span-1 space-y-4">
        <div class="glass-panel rounded-lg p-4 space-y-4">
          <div>
            <h2 class="text-xl font-bold text-white mb-2">Tỷ Giá & Chuyển Đổi</h2>
            <p class="text-purple-300 text-sm">USDT và các loại tiền tệ</p>
          </div>
          <RateCards />
          <CurrencyConverter />
        </div>
      </div>
    </section>

    <!-- Profile & Security -->
    <section class="glass-panel rounded-lg p-6 space-y-6">
      <div>
        <h2 class="text-xl font-bold text-white">Hồ Sơ & Bảo Mật</h2>
        <p class="text-purple-300 text-sm">Quản lý hồ sơ, ngân hàng và 2FA</p>
      </div>
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div class="space-y-4">
          <PersonalInfoForm />
          <VerificationStatus />
        </div>
        <div class="space-y-4">
          <BankAccountList />
          <SecuritySettings />
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue';
import SummaryCards from '../../components/personal/dashboard/SummaryCards.vue';
import BalanceOverview from '../../components/personal/dashboard/BalanceOverview.vue';
import QuickActions from '../../components/personal/dashboard/QuickActions.vue';
import SecurityPanel from '../../components/personal/dashboard/SecurityPanel.vue';
import StatsSummary from '../../components/personal/dashboard/StatsSummary.vue';
import CurrencyList from '../../components/personal/wallet/CurrencyList.vue';
import PortfolioAnalytics from '../../components/personal/wallet/PortfolioAnalytics.vue';
import CryptoDeposit from '../../components/personal/deposit/CryptoDeposit.vue';
import VietQRDeposit from '../../components/personal/deposit/VietQRDeposit.vue';
import OnlinePaymentDeposit from '../../components/personal/deposit/OnlinePaymentDeposit.vue';
import WithdrawForm from '../../components/personal/withdraw/WithdrawForm.vue';
import WithdrawHistory from '../../components/personal/withdraw/WithdrawHistory.vue';
import TransactionTabs from '../../components/personal/transactions/TransactionTabs.vue';
import TransactionCards from '../../components/personal/transactions/TransactionCards.vue';
import TransactionDetailModal from '../../components/personal/transactions/TransactionDetailModal.vue';
import FilterPanel from '../../components/personal/transactions/FilterPanel.vue';
import RateCards from '../../components/personal/rates/RateCards.vue';
import CurrencyConverter from '../../components/personal/rates/CurrencyConverter.vue';
import PersonalInfoForm from '../../components/personal/profile/PersonalInfoForm.vue';
import VerificationStatus from '../../components/personal/profile/VerificationStatus.vue';
import BankAccountList from '../../components/personal/profile/BankAccountList.vue';
import SecuritySettings from '../../components/personal/profile/SecuritySettings.vue';
import { useAccountStore } from '../../stores/account';
import { useTransactionsStore } from '../../stores/transactions';
import { useExchangeRatesStore } from '../../stores/exchangeRates';
import { useProfileStore } from '../../stores/profile';
import { exportTransactionsToCSV, exportTransactionsToPDF } from '../../utils/export';

const accountStore = useAccountStore();
const transactionsStore = useTransactionsStore();
const exchangeRatesStore = useExchangeRatesStore();
const profileStore = useProfileStore();

const activeDepositTab = ref('crypto');
const depositTabs = [
  { id: 'crypto', label: 'Crypto', icon: 'fab fa-bitcoin' },
  { id: 'vietqr', label: 'VietQR', icon: 'fas fa-qrcode' },
  { id: 'online', label: 'Online Payment', icon: 'fas fa-credit-card' },
];

const activeTab = ref('all');
const filters = ref({});
const showDetailModal = ref(false);
const selectedTransaction = ref(null);

const formattedAvailable = computed(() =>
  accountStore.balance.available?.toLocaleString('vi-VN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }) || '0.00'
);

const filteredTransactions = computed(() => {
  let transactions = transactionsStore.transactions;

  if (activeTab.value === 'deposits') {
    transactions = transactions.filter(t => t.type === 'deposit' || t.type === 'withdrawal');
  } else if (activeTab.value === 'orders') {
    transactions = transactions.filter(t => t.type === 'trading' || t.type === 'order');
  }

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

onMounted(async () => {
  try {
    await Promise.all([
      accountStore.fetchBalance(),
      transactionsStore.fetchTransactions(),
      profileStore.fetchProfile(),
      profileStore.fetchBankAccounts(),
    ]);
    exchangeRatesStore.startAutoRefresh();
  } catch (error) {
    console.error('Error initializing unified personal view:', error);
  }
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
    if (error.message?.includes('jsPDF')) {
      alert('PDF export cần cài đặt thư viện jsPDF. Vui lòng liên hệ admin.');
    } else {
      alert('Không thể xuất file PDF. Vui lòng thử lại.');
    }
  }
};
</script>

<style scoped>
.glass-panel {
  background: linear-gradient(135deg, rgba(30, 41, 59, 0.9), rgba(76, 29, 149, 0.35));
  border: 1px solid rgba(139, 92, 246, 0.2);
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.35);
}
</style>

