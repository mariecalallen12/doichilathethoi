<script setup>
import Table from '../ui/Table.vue';
import Badge from '../ui/Badge.vue';
import Button from '../ui/Button.vue';

const props = defineProps({
  payments: {
    type: Array,
    default: () => [],
  },
  loading: Boolean,
  pagination: {
    type: Object,
    default: null,
  },
});

const emit = defineEmits(['view', 'process', 'refund', 'page-change']);

const headers = [
  { key: 'payment_id', label: 'Payment ID', sortable: true },
  { key: 'invoice_id', label: 'Invoice ID', sortable: true },
  { key: 'user_id', label: 'User ID', sortable: true },
  { key: 'amount', label: 'Số tiền', sortable: true },
  { key: 'payment_method', label: 'Phương thức', sortable: true },
  { key: 'status', label: 'Trạng thái', sortable: true },
  { key: 'transaction_id', label: 'Transaction ID', sortable: true },
  { key: 'created_at', label: 'Ngày tạo', sortable: true },
  { key: 'actions', label: 'Thao tác', sortable: false },
];

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
    bank_transfer: 'Chuyển khoản',
    credit_card: 'Thẻ tín dụng',
    debit_card: 'Thẻ ghi nợ',
    e_wallet: 'Ví điện tử',
    crypto: 'Tiền điện tử',
  };
  return methodMap[method] || method;
};
</script>

<template>
  <Table
    :headers="headers"
    :data="payments"
    :loading="loading"
    :pagination="pagination"
    @page-change="emit('page-change', $event)"
  >
    <template #default="{ data }">
      <tr
        v-for="payment in data"
        :key="payment.id"
        class="border-b border-white/5 hover:bg-white/5 transition-colors"
      >
        <td class="px-4 py-3 text-white/80 text-sm font-mono font-semibold">
          {{ payment.payment_id || payment.id }}
        </td>
        <td class="px-4 py-3 text-white/80 text-sm font-mono">
          {{ payment.invoice_id || 'N/A' }}
        </td>
        <td class="px-4 py-3 text-white/80 text-sm">{{ payment.user_id }}</td>
        <td class="px-4 py-3 text-white font-semibold">${{ payment.amount?.toLocaleString() }}</td>
        <td class="px-4 py-3 text-white/80 text-sm">
          {{ getMethodText(payment.payment_method) }}
        </td>
        <td class="px-4 py-3">
          <Badge :type="getStatusType(payment.status)">
            {{ getStatusText(payment.status) }}
          </Badge>
        </td>
        <td class="px-4 py-3 text-white/60 text-sm font-mono text-xs">
          {{ payment.transaction_id || 'N/A' }}
        </td>
        <td class="px-4 py-3 text-white/60 text-sm">
          {{ new Date(payment.created_at).toLocaleDateString('vi-VN') }}
        </td>
        <td class="px-4 py-3">
          <div class="flex items-center gap-2">
            <Button
              variant="ghost"
              size="sm"
              icon="fas fa-eye"
              @click="emit('view', payment.id)"
            >
            </Button>
            <Button
              v-if="payment.status === 'pending' || payment.status === 'processing'"
              variant="ghost"
              size="sm"
              icon="fas fa-check text-green-400"
              @click="emit('process', payment.id)"
            >
            </Button>
            <Button
              v-if="payment.status === 'completed'"
              variant="ghost"
              size="sm"
              icon="fas fa-undo text-yellow-400"
              @click="emit('refund', payment.id)"
            >
            </Button>
          </div>
        </td>
      </tr>
    </template>
  </Table>
</template>

