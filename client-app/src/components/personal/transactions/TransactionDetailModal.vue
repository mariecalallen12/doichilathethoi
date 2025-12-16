<template>
  <div
    v-if="isOpen && transaction"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4"
    @click.self="close"
  >
    <div class="glass-panel rounded-lg p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
      <!-- Header -->
      <div class="flex items-center justify-between mb-6">
        <h3 class="text-xl font-bold text-white flex items-center">
          <i :class="getTransactionIcon(transaction.type)" class="mr-2 text-purple-400"></i>
          Chi Tiết Giao Dịch
        </h3>
        <button
          @click="close"
          class="text-purple-300 hover:text-white transition-colors"
        >
          <i class="fas fa-times text-xl"></i>
        </button>
      </div>

      <!-- Transaction Info -->
      <div class="space-y-6">
        <!-- Status Badge -->
        <div class="flex items-center justify-center">
          <StatusBadge :status="transaction.status" />
        </div>

        <!-- Main Info -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="bg-slate-800/50 rounded-lg p-4">
            <div class="text-purple-300 text-xs mb-1">Loại giao dịch</div>
            <div class="text-white font-medium">{{ getTransactionTypeLabel(transaction.type) }}</div>
          </div>
          <div class="bg-slate-800/50 rounded-lg p-4">
            <div class="text-purple-300 text-xs mb-1">Trạng thái</div>
            <div class="text-white font-medium">{{ getStatusLabel(transaction.status) }}</div>
          </div>
          <div class="bg-slate-800/50 rounded-lg p-4">
            <div class="text-purple-300 text-xs mb-1">Số tiền</div>
            <div class="text-white font-medium text-lg">
              {{ formatAmount(transaction.amount, transaction.currency) }}
            </div>
          </div>
          <div class="bg-slate-800/50 rounded-lg p-4">
            <div class="text-purple-300 text-xs mb-1">Tiền tệ</div>
            <div class="text-white font-medium">{{ transaction.currency || 'N/A' }}</div>
          </div>
        </div>

        <!-- Date & Time -->
        <div class="bg-slate-800/50 rounded-lg p-4">
          <div class="text-purple-300 text-xs mb-1">Ngày/Giờ</div>
          <div class="text-white font-medium">
            {{ formatDateTime(transaction.date || transaction.created_at) }}
          </div>
        </div>

        <!-- Reference ID -->
        <div class="bg-slate-800/50 rounded-lg p-4">
          <div class="flex items-center justify-between">
            <div>
              <div class="text-purple-300 text-xs mb-1">Mã tham chiếu</div>
              <div class="text-white font-mono text-sm">{{ transaction.id || transaction.reference || 'N/A' }}</div>
            </div>
            <button
              @click="copyReference"
              class="px-3 py-1 bg-purple-500/20 text-purple-300 rounded text-xs hover:bg-purple-500/30 transition-all"
            >
              <i class="fas fa-copy mr-1"></i>Copy
            </button>
          </div>
        </div>

        <!-- Fee -->
        <div v-if="transaction.fee" class="bg-slate-800/50 rounded-lg p-4">
          <div class="text-purple-300 text-xs mb-1">Phí giao dịch</div>
          <div class="text-white font-medium">
            {{ formatAmount(transaction.fee, transaction.currency) }}
          </div>
        </div>

        <!-- Net Amount -->
        <div v-if="transaction.net_amount || (transaction.amount && transaction.fee)" class="bg-slate-800/50 rounded-lg p-4">
          <div class="text-purple-300 text-xs mb-1">Số tiền thực nhận</div>
          <div class="text-white font-medium text-lg">
            {{ formatAmount(
              transaction.net_amount || (transaction.amount - (transaction.fee || 0)),
              transaction.currency
            ) }}
          </div>
        </div>

        <!-- Description -->
        <div v-if="transaction.description" class="bg-slate-800/50 rounded-lg p-4">
          <div class="text-purple-300 text-xs mb-1">Mô tả</div>
          <div class="text-white">{{ transaction.description }}</div>
        </div>

        <!-- Additional Info -->
        <div v-if="transaction.metadata || transaction.additional_info" class="bg-slate-800/50 rounded-lg p-4">
          <div class="text-purple-300 text-xs mb-2">Thông tin bổ sung</div>
          <div class="text-white text-sm space-y-1">
            <div v-if="transaction.metadata?.method">
              <span class="text-purple-300">Phương thức:</span> {{ transaction.metadata.method }}
            </div>
            <div v-if="transaction.metadata?.network">
              <span class="text-purple-300">Network:</span> {{ transaction.metadata.network }}
            </div>
            <div v-if="transaction.metadata?.wallet_address">
              <span class="text-purple-300">Địa chỉ ví:</span>
              <code class="text-xs font-mono">{{ transaction.metadata.wallet_address }}</code>
            </div>
            <div v-if="transaction.metadata?.bank_account">
              <span class="text-purple-300">Tài khoản ngân hàng:</span> {{ transaction.metadata.bank_account }}
            </div>
            <div v-if="transaction.metadata?.transaction_hash">
              <span class="text-purple-300">Transaction Hash:</span>
              <code class="text-xs font-mono break-all">{{ transaction.metadata.transaction_hash }}</code>
            </div>
          </div>
        </div>

        <!-- Actions -->
        <div class="flex space-x-3 pt-4 border-t border-purple-500/20">
          <button
            v-if="transaction.status === 'pending'"
            @click="cancelTransaction"
            class="flex-1 px-4 py-2 bg-red-500/20 border border-red-500/30 text-red-300 rounded-lg font-medium hover:bg-red-500/30 transition-all"
          >
            <i class="fas fa-times-circle mr-2"></i>Hủy giao dịch
          </button>
          <button
            @click="exportReceipt"
            class="flex-1 px-4 py-2 bg-blue-500/20 border border-blue-500/30 text-blue-300 rounded-lg font-medium hover:bg-blue-500/30 transition-all"
          >
            <i class="fas fa-download mr-2"></i>Xuất biên lai
          </button>
          <button
            @click="close"
            class="flex-1 px-4 py-2 bg-slate-800/50 border border-purple-500/30 text-purple-300 rounded-lg font-medium hover:bg-purple-500/20 transition-all"
          >
            Đóng
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import StatusBadge from '../shared/StatusBadge.vue';
import { formatCurrency, formatNumber } from '../../../services/utils/formatters';

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false,
  },
  transaction: {
    type: Object,
    default: null,
  },
});

const emit = defineEmits(['close', 'cancel', 'export']);

function close() {
  emit('close');
}

function getTransactionIcon(type) {
  const icons = {
    deposit: 'fas fa-arrow-down',
    withdrawal: 'fas fa-arrow-up',
    trading: 'fas fa-exchange-alt',
    order: 'fas fa-shopping-cart',
    fee: 'fas fa-coins',
  };
  return icons[type] || 'fas fa-receipt';
}

function getTransactionTypeLabel(type) {
  const labels = {
    deposit: 'Nạp tiền',
    withdrawal: 'Rút tiền',
    trading: 'Giao dịch',
    order: 'Đặt lệnh',
    fee: 'Phí',
  };
  return labels[type] || type;
}

function getStatusLabel(status) {
  const labels = {
    completed: 'Hoàn thành',
    pending: 'Đang xử lý',
    failed: 'Thất bại',
    cancelled: 'Đã hủy',
    processing: 'Đang xử lý',
  };
  return labels[status] || status;
}

function formatAmount(amount, currency = 'USD') {
  if (amount === null || amount === undefined) return 'N/A';
  return formatCurrency(amount, currency);
}

function formatDateTime(date) {
  if (!date) return 'N/A';
  const d = new Date(date);
  return d.toLocaleString('vi-VN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function copyReference() {
  const ref = props.transaction?.id || props.transaction?.reference;
  if (ref) {
    navigator.clipboard.writeText(ref).then(() => {
      alert('Đã sao chép mã tham chiếu');
    });
  }
}

function cancelTransaction() {
  if (confirm('Bạn có chắc chắn muốn hủy giao dịch này?')) {
    emit('cancel', props.transaction);
  }
}

function exportReceipt() {
  emit('export', props.transaction);
}
</script>
