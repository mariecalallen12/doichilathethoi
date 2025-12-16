<script setup>
import Modal from '../ui/Modal.vue';
import Card from '../ui/Card.vue';
import Badge from '../ui/Badge.vue';
import Button from '../ui/Button.vue';

const props = defineProps({
  show: Boolean,
  payment: {
    type: Object,
    default: null,
  },
});

const emit = defineEmits(['close', 'update:show', 'process', 'refund']);

const getStatusType = (status) => {
  const statusMap = {
    pending: 'pending',
    processing: 'pending',
    completed: 'approved',
    failed: 'error',
    refunded: 'rejected',
  };
  return statusMap[status] || 'default';
};

const getStatusText = (status) => {
  const textMap = {
    pending: 'Chờ xử lý',
    processing: 'Đang xử lý',
    completed: 'Hoàn thành',
    failed: 'Thất bại',
    refunded: 'Đã hoàn tiền',
  };
  return textMap[status] || status;
};

const getMethodText = (method) => {
  const methodMap = {
    bank_transfer: 'Chuyển khoản ngân hàng',
    credit_card: 'Thẻ tín dụng',
    debit_card: 'Thẻ ghi nợ',
    e_wallet: 'Ví điện tử',
    crypto: 'Tiền điện tử',
  };
  return methodMap[method] || method;
};
</script>

<template>
  <Modal
    :show="show"
    title="Chi tiết thanh toán"
    size="lg"
    @update:show="emit('update:show', $event)"
    @close="emit('close')"
  >
    <div v-if="payment" class="space-y-4">
      <!-- Payment Header -->
      <div class="flex items-start justify-between">
        <div>
          <h3 class="text-2xl font-bold text-white mb-2">
            Payment #{{ payment.payment_id || payment.id }}
          </h3>
          <p class="text-white/60">Invoice ID: {{ payment.invoice_id || 'N/A' }}</p>
        </div>
        <Badge :type="getStatusType(payment.status)">
          {{ getStatusText(payment.status) }}
        </Badge>
      </div>

      <!-- Payment Info -->
      <div class="grid grid-cols-2 gap-4">
        <Card padding="p-4">
          <p class="text-white/60 text-sm mb-1">Số tiền</p>
          <p class="text-white text-2xl font-bold">${{ payment.amount?.toLocaleString() }}</p>
        </Card>
        <Card padding="p-4">
          <p class="text-white/60 text-sm mb-1">Phương thức thanh toán</p>
          <p class="text-white font-semibold">{{ getMethodText(payment.payment_method) }}</p>
        </Card>
        <Card padding="p-4">
          <p class="text-white/60 text-sm mb-1">User ID</p>
          <p class="text-white font-semibold">{{ payment.user_id }}</p>
        </Card>
        <Card padding="p-4">
          <p class="text-white/60 text-sm mb-1">Transaction ID</p>
          <p class="text-white font-mono text-sm">{{ payment.transaction_id || 'N/A' }}</p>
        </Card>
        <Card padding="p-4">
          <p class="text-white/60 text-sm mb-1">Ngày tạo</p>
          <p class="text-white font-semibold">
            {{ new Date(payment.created_at).toLocaleDateString('vi-VN') }}
          </p>
        </Card>
        <Card padding="p-4" v-if="payment.processed_at">
          <p class="text-white/60 text-sm mb-1">Ngày xử lý</p>
          <p class="text-white font-semibold">
            {{ new Date(payment.processed_at).toLocaleDateString('vi-VN') }}
          </p>
        </Card>
      </div>

      <!-- Payment Details -->
      <Card v-if="payment.details" padding="p-4">
        <p class="text-white/60 text-sm mb-2">Chi tiết</p>
        <pre class="text-white text-sm whitespace-pre-wrap">{{ JSON.stringify(payment.details, null, 2) }}</pre>
      </Card>

      <!-- Error Message -->
      <Card v-if="payment.error_message" padding="p-4" class="border-red-500/50">
        <p class="text-red-400 text-sm font-semibold mb-1">Lỗi</p>
        <p class="text-red-300 text-sm">{{ payment.error_message }}</p>
      </Card>

      <!-- Actions -->
      <div class="flex items-center justify-end gap-3 pt-4 border-t border-white/10">
        <Button variant="outline" @click="emit('close')">Đóng</Button>
        <Button
          v-if="payment.status === 'pending' || payment.status === 'processing'"
          variant="primary"
          @click="emit('process', payment.id)"
        >
          Xử lý thanh toán
        </Button>
        <Button
          v-if="payment.status === 'completed'"
          variant="warning"
          @click="emit('refund', payment.id)"
        >
          Hoàn tiền
        </Button>
      </div>
    </div>
    <div v-else class="text-center py-8">
      <i class="fas fa-spinner fa-spin text-primary text-3xl"></i>
    </div>
  </Modal>
</template>

