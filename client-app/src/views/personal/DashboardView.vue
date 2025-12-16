<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div>
      <h1 class="text-3xl font-bold text-white mb-2">Dashboard Tổng Quan</h1>
      <p class="text-purple-300">Tổng quan về tài chính và hoạt động của bạn</p>
    </div>

    <!-- Summary Cards -->
    <SummaryCards />

    <!-- Balance Overview -->
    <BalanceOverview />

    <!-- Stats Summary -->
    <StatsSummary />

    <!-- Quick Actions -->
    <QuickActions />

    <!-- Two Column Layout -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Recent Activity -->
      <RecentActivity @view-detail="handleViewDetail" />

      <!-- Exchange Rate Preview -->
      <ExchangeRatePreview />
    </div>

    <!-- Security Panel -->
    <SecurityPanel />
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import BalanceOverview from '../../components/personal/dashboard/BalanceOverview.vue';
import SummaryCards from '../../components/personal/dashboard/SummaryCards.vue';
import QuickActions from '../../components/personal/dashboard/QuickActions.vue';
import RecentActivity from '../../components/personal/dashboard/RecentActivity.vue';
import SecurityPanel from '../../components/personal/dashboard/SecurityPanel.vue';
import ExchangeRatePreview from '../../components/personal/dashboard/ExchangeRatePreview.vue';
import StatsSummary from '../../components/personal/dashboard/StatsSummary.vue';
import { useRouter } from 'vue-router';
import { useAccountStore } from '../../stores/account';
import { useTransactionsStore } from '../../stores/transactions';
import { clientApi } from '../../services/api/client';

const router = useRouter();
const accountStore = useAccountStore();
const transactionsStore = useTransactionsStore();

onMounted(async () => {
  // Fetch dashboard overview, balance and recent transactions
  try {
    // Gọi dashboard tổng thể để đồng bộ nhanh overview + số dư + activity
    try {
      const dashboard = await clientApi.getDashboard();
      const data = dashboard.data || dashboard;

      // Nếu dashboard trả về balances, dùng nó cập nhật lại store balance
      if (data.balances) {
        // Tạm thời chỉ gọi lại fetchBalance để dùng logic mapping chuẩn
        await accountStore.fetchBalance();
      }

      // Recent activity trên UI sử dụng trực tiếp từ transactionsStore,
      // nên ta vẫn fetch Transactions riêng.
    } catch (e) {
      // Nếu dashboard thất bại, vẫn tiếp tục fetch balance và transactions riêng
      console.error('Error fetching client dashboard:', e);
    }

    await Promise.all([
      accountStore.fetchBalance(),
      transactionsStore.fetchTransactions({ limit: 10 }),
    ]);
  } catch (error) {
    console.error('Error fetching dashboard data:', error);
  }
});

const handleViewDetail = (transaction) => {
  router.push({
    name: 'TransactionHistory',
    query: { id: transaction.id },
  });
};
</script>
