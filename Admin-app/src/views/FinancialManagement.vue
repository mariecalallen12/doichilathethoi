<script setup>
import { ref, onMounted, watch } from 'vue';
import api from '../services/api';
import toastService from '../services/toast';
import FinancialStatsCards from '../components/financial/FinancialStatsCards.vue';
import DepositTable from '../components/financial/DepositTable.vue';
import WithdrawalTable from '../components/financial/WithdrawalTable.vue';
import InvoiceTable from '../components/financial/InvoiceTable.vue';
import InvoiceForm from '../components/financial/InvoiceForm.vue';
import InvoiceDetailsModal from '../components/financial/InvoiceDetailsModal.vue';
import PaymentTable from '../components/financial/PaymentTable.vue';
import PaymentDetailsModal from '../components/financial/PaymentDetailsModal.vue';
import ReceiptViewer from '../components/financial/ReceiptViewer.vue';
import CustomerWalletBalancesTable from '../components/financial/CustomerWalletBalancesTable.vue';
import Card from '../components/ui/Card.vue';
import Button from '../components/ui/Button.vue';

// Initialize with null values - will be populated from API
const stats = ref({
  totalDeposits: null,
  totalWithdrawals: null,
  pendingDeposits: null,
  pendingWithdrawals: null,
});

const activeTab = ref('deposits');
const deposits = ref([]);
const withdrawals = ref([]);
const invoices = ref([]);
const payments = ref([]);
const customerWalletBalances = ref([]);
const walletBalancesSummary = ref({});
const loading = ref(false);
const walletBalancesTableRef = ref(null);
const showReceiptModal = ref(false);
const receiptUrl = ref('');
const showInvoiceForm = ref(false);
const showInvoiceModal = ref(false);
const selectedInvoice = ref(null);
const invoiceFilters = ref({
  status: 'all',
  user_id: '',
  date_from: '',
  date_to: '',
});
const showPaymentModal = ref(false);
const selectedPayment = ref(null);
const paymentFilters = ref({
  status: 'all',
  payment_method: 'all',
  user_id: '',
  date_from: '',
  date_to: '',
});

const pagination = ref({
  page: 1,
  limit: 50,
  total: 0,
});

const tabs = [
  { id: 'deposits', label: 'Nạp tiền', icon: 'fa-arrow-down' },
  { id: 'withdrawals', label: 'Rút tiền', icon: 'fa-arrow-up' },
  { id: 'invoices', label: 'Hóa đơn', icon: 'fa-file-invoice' },
  { id: 'payments', label: 'Thanh toán', icon: 'fa-credit-card' },
  { id: 'wallet-balances', label: 'Số dư ví khách hàng', icon: 'fa-wallet' },
];

const fetchDeposits = async () => {
  loading.value = true;
  try {
    const response = await api.get('/api/admin/deposits', {
      page: pagination.value.page,
      limit: pagination.value.limit,
    });
    
    const data = response.data?.data || response.data || {};
    deposits.value = data.deposits || data.transactions || [];
    if (data.total !== undefined) {
      pagination.value.total = data.total;
    }
    
    // Update stats
    if (data.stats) {
      stats.value.pendingDeposits = data.stats.pending || 0;
      stats.value.totalDeposits = data.stats.total || 0;
    }
  } catch (error) {
    toastService.error('Không thể tải danh sách nạp tiền');
    console.error('Fetch deposits error:', error);
  } finally {
    loading.value = false;
  }
};

const fetchWithdrawals = async () => {
  loading.value = true;
  try {
    const response = await api.get('/api/admin/withdrawals', {
      page: pagination.value.page,
      limit: pagination.value.limit,
    });
    
    const data = response.data?.data || response.data || {};
    withdrawals.value = data.withdrawals || data.transactions || [];
    if (data.total !== undefined) {
      pagination.value.total = data.total;
    }
    
    // Update stats
    if (data.stats) {
      stats.value.pendingWithdrawals = data.stats.pending || 0;
      stats.value.totalWithdrawals = data.stats.total || 0;
    }
  } catch (error) {
    toastService.error('Không thể tải danh sách rút tiền');
    console.error('Fetch withdrawals error:', error);
  } finally {
    loading.value = false;
  }
};

const handleApproveDeposit = async (id) => {
  try {
    await api.post(`/api/admin/deposits/${id}/approve`);
    toastService.success('Đã phê duyệt nạp tiền');
    await fetchDeposits();
  } catch (error) {
    toastService.error('Không thể phê duyệt');
    console.error('Approve deposit error:', error);
  }
};

const handleRejectDeposit = async (id) => {
  try {
    await api.post(`/api/admin/deposits/${id}/reject`);
    toastService.success('Đã từ chối nạp tiền');
    await fetchDeposits();
  } catch (error) {
    toastService.error('Không thể từ chối');
    console.error('Reject deposit error:', error);
  }
};

const handleApproveWithdrawal = async (id) => {
  try {
    await api.post(`/api/admin/withdrawals/${id}/approve`);
    toastService.success('Đã phê duyệt rút tiền');
    await fetchWithdrawals();
  } catch (error) {
    toastService.error('Không thể phê duyệt');
    console.error('Approve withdrawal error:', error);
  }
};

const handleRejectWithdrawal = async (id) => {
  try {
    await api.post(`/api/admin/withdrawals/${id}/reject`);
    toastService.success('Đã từ chối rút tiền');
    await fetchWithdrawals();
  } catch (error) {
    toastService.error('Không thể từ chối');
    console.error('Reject withdrawal error:', error);
  }
};

const handleViewReceipt = (depositId) => {
  const deposit = deposits.value.find(d => d.id === depositId);
  if (deposit?.receipt_url) {
    receiptUrl.value = deposit.receipt_url;
    showReceiptModal.value = true;
  }
};

const fetchInvoices = async () => {
  loading.value = true;
  try {
    const params = {
      page: pagination.value.page,
      limit: pagination.value.limit,
    };
    
    if (invoiceFilters.value.status !== 'all') {
      params.status = invoiceFilters.value.status;
    }
    if (invoiceFilters.value.user_id) {
      params.user_id = invoiceFilters.value.user_id;
    }
    if (invoiceFilters.value.date_from) {
      params.date_from = invoiceFilters.value.date_from;
    }
    if (invoiceFilters.value.date_to) {
      params.date_to = invoiceFilters.value.date_to;
    }
    
    const response = await api.get('/api/admin/invoices', params);
    const data = response.data?.data || response.data || {};
    invoices.value = data.invoices || [];
    if (data.total !== undefined) {
      pagination.value.total = data.total;
    }
  } catch (error) {
    toastService.error('Không thể tải danh sách hóa đơn');
    console.error('Fetch invoices error:', error);
  } finally {
    loading.value = false;
  }
};

const handleCreateInvoice = () => {
  selectedInvoice.value = null;
  showInvoiceForm.value = true;
};

const handleViewInvoice = async (invoiceId) => {
  loading.value = true;
  try {
    const response = await api.get(`/api/admin/invoices/${invoiceId}`);
    const data = response.data?.data || response.data || {};
    selectedInvoice.value = data;
    showInvoiceModal.value = true;
  } catch (error) {
    toastService.error('Không thể tải chi tiết hóa đơn');
    console.error('Fetch invoice error:', error);
  } finally {
    loading.value = false;
  }
};

const handleEditInvoice = async (invoiceId) => {
  loading.value = true;
  try {
    const response = await api.get(`/api/admin/invoices/${invoiceId}`);
    const data = response.data?.data || response.data || {};
    selectedInvoice.value = data;
    showInvoiceForm.value = true;
    showInvoiceModal.value = false;
  } catch (error) {
    toastService.error('Không thể tải hóa đơn');
    console.error('Fetch invoice error:', error);
  } finally {
    loading.value = false;
  }
};

const handleSubmitInvoice = async (invoiceData) => {
  loading.value = true;
  try {
    if (selectedInvoice.value) {
      await api.put(`/api/admin/invoices/${selectedInvoice.value.id}`, invoiceData);
      toastService.success('Đã cập nhật hóa đơn');
    } else {
      await api.post('/api/admin/invoices', invoiceData);
      toastService.success('Đã tạo hóa đơn');
    }
    showInvoiceForm.value = false;
    selectedInvoice.value = null;
    await fetchInvoices();
  } catch (error) {
    toastService.error(error.message || 'Không thể lưu hóa đơn');
    console.error('Save invoice error:', error);
  } finally {
    loading.value = false;
  }
};

const handleDeleteInvoice = async (invoiceId) => {
  if (!confirm('Bạn có chắc chắn muốn xóa hóa đơn này?')) {
    return;
  }
  
  loading.value = true;
  try {
    await api.delete(`/api/admin/invoices/${invoiceId}`);
    toastService.success('Đã xóa hóa đơn');
    showInvoiceModal.value = false;
    await fetchInvoices();
  } catch (error) {
    toastService.error('Không thể xóa hóa đơn');
    console.error('Delete invoice error:', error);
  } finally {
    loading.value = false;
  }
};

const handleApproveInvoice = async (invoiceId) => {
  loading.value = true;
  try {
    await api.post(`/api/admin/invoices/${invoiceId}/approve`);
    toastService.success('Đã phê duyệt hóa đơn');
    showInvoiceModal.value = false;
    await fetchInvoices();
  } catch (error) {
    toastService.error('Không thể phê duyệt hóa đơn');
    console.error('Approve invoice error:', error);
  } finally {
    loading.value = false;
  }
};

const handleRejectInvoice = async (invoiceId) => {
  loading.value = true;
  try {
    await api.post(`/api/admin/invoices/${invoiceId}/reject`);
    toastService.success('Đã từ chối hóa đơn');
    showInvoiceModal.value = false;
    await fetchInvoices();
  } catch (error) {
    toastService.error('Không thể từ chối hóa đơn');
    console.error('Reject invoice error:', error);
  } finally {
    loading.value = false;
  }
};

const handleInvoicePageChange = (page) => {
  pagination.value.page = page;
  fetchInvoices();
};

const fetchPayments = async () => {
  loading.value = true;
  try {
    const params = {
      page: pagination.value.page,
      limit: pagination.value.limit,
    };
    
    if (paymentFilters.value.status !== 'all') {
      params.status = paymentFilters.value.status;
    }
    if (paymentFilters.value.payment_method !== 'all') {
      params.payment_method = paymentFilters.value.payment_method;
    }
    if (paymentFilters.value.user_id) {
      params.user_id = paymentFilters.value.user_id;
    }
    if (paymentFilters.value.date_from) {
      params.date_from = paymentFilters.value.date_from;
    }
    if (paymentFilters.value.date_to) {
      params.date_to = paymentFilters.value.date_to;
    }
    
    const response = await api.get('/api/admin/payments', params);
    const data = response.data?.data || response.data || {};
    payments.value = data.payments || [];
    if (data.total !== undefined) {
      pagination.value.total = data.total;
    }
  } catch (error) {
    toastService.error('Không thể tải danh sách thanh toán');
    console.error('Fetch payments error:', error);
  } finally {
    loading.value = false;
  }
};

const handleViewPayment = async (paymentId) => {
  loading.value = true;
  try {
    const response = await api.get(`/api/admin/payments/${paymentId}`);
    const data = response.data?.data || response.data || {};
    selectedPayment.value = data;
    showPaymentModal.value = true;
  } catch (error) {
    toastService.error('Không thể tải chi tiết thanh toán');
    console.error('Fetch payment error:', error);
  } finally {
    loading.value = false;
  }
};

const handleProcessPayment = async (paymentId) => {
  loading.value = true;
  try {
    await api.post(`/api/admin/payments/${paymentId}/process`);
    toastService.success('Đã xử lý thanh toán');
    showPaymentModal.value = false;
    await fetchPayments();
  } catch (error) {
    toastService.error('Không thể xử lý thanh toán');
    console.error('Process payment error:', error);
  } finally {
    loading.value = false;
  }
};

const handleRefundPayment = async (paymentId) => {
  if (!confirm('Bạn có chắc chắn muốn hoàn tiền cho thanh toán này?')) {
    return;
  }
  
  loading.value = true;
  try {
    await api.post(`/api/admin/payments/${paymentId}/refund`);
    toastService.success('Đã hoàn tiền');
    showPaymentModal.value = false;
    await fetchPayments();
  } catch (error) {
    toastService.error('Không thể hoàn tiền');
    console.error('Refund payment error:', error);
  } finally {
    loading.value = false;
  }
};

const handlePaymentPageChange = (page) => {
  pagination.value.page = page;
  fetchPayments();
};

const fetchCustomerWalletBalances = async () => {
  loading.value = true;
  try {
    const params = {
      page: pagination.value.page,
      limit: pagination.value.limit,
    };
    
    // Get filter values from table component if available
    if (walletBalancesTableRef.value && walletBalancesTableRef.value.getFilters) {
      const filters = walletBalancesTableRef.value.getFilters();
      Object.assign(params, filters);
    }
    
    const response = await api.getCustomerWalletBalances(params);
    const data = response.data || response;
    customerWalletBalances.value = Array.isArray(data) ? data : (data.data || []);
    walletBalancesSummary.value = data.summary || {};
    
    if (data.pagination) {
      pagination.value.total = data.pagination.total || 0;
    }
    
    // Update table component
    if (walletBalancesTableRef.value) {
      walletBalancesTableRef.value.setData(customerWalletBalances.value, walletBalancesSummary.value);
    }
  } catch (error) {
    toastService.error('Không thể tải số dư ví khách hàng');
    console.error('Fetch customer wallet balances error:', error);
  } finally {
    loading.value = false;
  }
};

const handleWalletBalancesRefresh = () => {
  fetchCustomerWalletBalances();
};

const handleWalletBalancesPageChange = (page) => {
  pagination.value.page = page;
  fetchCustomerWalletBalances();
};

watch(activeTab, (newTab) => {
  if (newTab === 'deposits') fetchDeposits();
  if (newTab === 'withdrawals') fetchWithdrawals();
  if (newTab === 'invoices') fetchInvoices();
  if (newTab === 'payments') fetchPayments();
  if (newTab === 'wallet-balances') fetchCustomerWalletBalances();
});

onMounted(() => {
  if (activeTab.value === 'deposits') fetchDeposits();
  if (activeTab.value === 'withdrawals') fetchWithdrawals();
  if (activeTab.value === 'invoices') fetchInvoices();
  if (activeTab.value === 'payments') fetchPayments();
  if (activeTab.value === 'wallet-balances') fetchCustomerWalletBalances();
});
</script>

<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div>
      <h1 class="text-3xl font-bold text-white mb-2">Quản lý tài chính</h1>
      <p class="text-white/60">Quản lý nạp tiền, rút tiền, hóa đơn và thanh toán</p>
    </div>

    <!-- Stats Cards -->
    <FinancialStatsCards :stats="stats" />

    <!-- Tabs -->
    <div class="flex items-center gap-2 border-b border-white/10">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        :class="[
          'px-4 py-2 font-medium transition-colors border-b-2 flex items-center gap-2',
          activeTab === tab.id
            ? 'text-primary border-primary'
            : 'text-white/60 border-transparent hover:text-white',
        ]"
        @click="activeTab = tab.id"
      >
        <i :class="['fas', tab.icon]"></i>
        {{ tab.label }}
      </button>
    </div>

    <!-- Deposits Tab -->
    <Card v-if="activeTab === 'deposits'">
      <DepositTable
        :deposits="deposits"
        :loading="loading"
        :pagination="pagination"
        @approve="handleApproveDeposit"
        @reject="handleRejectDeposit"
        @view-receipt="handleViewReceipt"
      />
    </Card>

    <!-- Withdrawals Tab -->
    <Card v-if="activeTab === 'withdrawals'">
      <WithdrawalTable
        :withdrawals="withdrawals"
        :loading="loading"
        :pagination="pagination"
        @approve="handleApproveWithdrawal"
        @reject="handleRejectWithdrawal"
      />
    </Card>

    <!-- Invoices Tab -->
    <div v-if="activeTab === 'invoices'" class="space-y-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-4">
          <select
            v-model="invoiceFilters.status"
            class="px-4 py-2 rounded-lg bg-white/10 border border-white/20 text-white"
            @change="fetchInvoices"
          >
            <option value="all">Tất cả trạng thái</option>
            <option value="draft">Nháp</option>
            <option value="pending">Chờ thanh toán</option>
            <option value="paid">Đã thanh toán</option>
            <option value="overdue">Quá hạn</option>
            <option value="cancelled">Đã hủy</option>
          </select>
          <input
            v-model="invoiceFilters.user_id"
            type="text"
            placeholder="Tìm theo User ID"
            class="px-4 py-2 rounded-lg bg-white/10 border border-white/20 text-white placeholder-white/40"
            @keyup.enter="fetchInvoices"
          />
        </div>
        <Button variant="primary" icon="fas fa-plus" @click="handleCreateInvoice">
          Tạo hóa đơn
        </Button>
      </div>
      <Card>
        <InvoiceTable
          :invoices="invoices"
          :loading="loading"
          :pagination="pagination"
          @view="handleViewInvoice"
          @edit="handleEditInvoice"
          @delete="handleDeleteInvoice"
          @approve="handleApproveInvoice"
          @reject="handleRejectInvoice"
          @page-change="handleInvoicePageChange"
        />
    </Card>
    </div>

    <!-- Payments Tab -->
    <div v-if="activeTab === 'payments'" class="space-y-4">
      <div class="flex items-center gap-4">
        <select
          v-model="paymentFilters.status"
          class="px-4 py-2 rounded-lg bg-white/10 border border-white/20 text-white"
          @change="fetchPayments"
        >
          <option value="all">Tất cả trạng thái</option>
          <option value="pending">Chờ xử lý</option>
          <option value="processing">Đang xử lý</option>
          <option value="completed">Hoàn thành</option>
          <option value="failed">Thất bại</option>
          <option value="refunded">Đã hoàn tiền</option>
        </select>
        <select
          v-model="paymentFilters.payment_method"
          class="px-4 py-2 rounded-lg bg-white/10 border border-white/20 text-white"
          @change="fetchPayments"
        >
          <option value="all">Tất cả phương thức</option>
          <option value="bank_transfer">Chuyển khoản</option>
          <option value="credit_card">Thẻ tín dụng</option>
          <option value="debit_card">Thẻ ghi nợ</option>
          <option value="e_wallet">Ví điện tử</option>
          <option value="crypto">Tiền điện tử</option>
        </select>
        <input
          v-model="paymentFilters.user_id"
          type="text"
          placeholder="Tìm theo User ID"
          class="px-4 py-2 rounded-lg bg-white/10 border border-white/20 text-white placeholder-white/40"
          @keyup.enter="fetchPayments"
        />
      </div>
      <Card>
        <PaymentTable
          :payments="payments"
          :loading="loading"
          :pagination="pagination"
          @view="handleViewPayment"
          @process="handleProcessPayment"
          @refund="handleRefundPayment"
          @page-change="handlePaymentPageChange"
        />
    </Card>
    </div>

    <!-- Customer Wallet Balances Tab -->
    <Card v-if="activeTab === 'wallet-balances'">
      <CustomerWalletBalancesTable
        ref="walletBalancesTableRef"
        :loading="loading"
        :pagination="pagination"
        @page-change="handleWalletBalancesPageChange"
        @refresh="handleWalletBalancesRefresh"
      />
    </Card>

    <!-- Receipt Viewer Modal -->
    <ReceiptViewer
      :show="showReceiptModal"
      :receipt-url="receiptUrl"
      @update:show="showReceiptModal = $event"
      @close="showReceiptModal = false"
    />

    <!-- Invoice Form Modal -->
    <InvoiceForm
      :show="showInvoiceForm"
      :invoice="selectedInvoice"
      :loading="loading"
      @update:show="showInvoiceForm = $event"
      @close="showInvoiceForm = false; selectedInvoice = null"
      @submit="handleSubmitInvoice"
    />

    <!-- Invoice Details Modal -->
    <InvoiceDetailsModal
      :show="showInvoiceModal"
      :invoice="selectedInvoice"
      @update:show="showInvoiceModal = $event"
      @close="showInvoiceModal = false; selectedInvoice = null"
      @edit="handleEditInvoice"
      @approve="handleApproveInvoice"
      @reject="handleRejectInvoice"
      @delete="handleDeleteInvoice"
    />

    <!-- Payment Details Modal -->
    <PaymentDetailsModal
      :show="showPaymentModal"
      :payment="selectedPayment"
      @update:show="showPaymentModal = $event"
      @close="showPaymentModal = false; selectedPayment = null"
      @process="handleProcessPayment"
      @refund="handleRefundPayment"
    />
  </div>
</template>

