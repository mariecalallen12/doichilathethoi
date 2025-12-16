<script setup>
import Table from '../ui/Table.vue';
import Badge from '../ui/Badge.vue';
import Button from '../ui/Button.vue';

const props = defineProps({
  invoices: {
    type: Array,
    default: () => [],
  },
  loading: Boolean,
  pagination: {
    type: Object,
    default: null,
  },
});

const emit = defineEmits(['view', 'edit', 'delete', 'approve', 'reject', 'page-change']);

const headers = [
  { key: 'invoice_number', label: 'Số hóa đơn', sortable: true },
  { key: 'user_id', label: 'User ID', sortable: true },
  { key: 'amount', label: 'Số tiền', sortable: true },
  { key: 'status', label: 'Trạng thái', sortable: true },
  { key: 'due_date', label: 'Ngày đến hạn', sortable: true },
  { key: 'created_at', label: 'Ngày tạo', sortable: true },
  { key: 'actions', label: 'Thao tác', sortable: false },
];

const getStatusType = (status) => {
  const statusMap = {
    draft: 'default',
    pending: 'pending',
    paid: 'approved',
    overdue: 'error',
    cancelled: 'rejected',
  };
  return statusMap[status] || 'default';
};

const getStatusText = (status) => {
  const textMap = {
    draft: 'Nháp',
    pending: 'Chờ thanh toán',
    paid: 'Đã thanh toán',
    overdue: 'Quá hạn',
    cancelled: 'Đã hủy',
  };
  return textMap[status] || status;
};
</script>

<template>
  <Table
    :headers="headers"
    :data="invoices"
    :loading="loading"
    :pagination="pagination"
    @page-change="emit('page-change', $event)"
  >
    <template #default="{ data }">
      <tr
        v-for="invoice in data"
        :key="invoice.id"
        class="border-b border-white/5 hover:bg-white/5 transition-colors"
      >
        <td class="px-4 py-3 text-white/80 text-sm font-mono font-semibold">
          {{ invoice.invoice_number || invoice.id }}
        </td>
        <td class="px-4 py-3 text-white/80 text-sm">{{ invoice.user_id }}</td>
        <td class="px-4 py-3 text-white font-semibold">${{ invoice.amount?.toLocaleString() }}</td>
        <td class="px-4 py-3">
          <Badge :type="getStatusType(invoice.status)">
            {{ getStatusText(invoice.status) }}
          </Badge>
        </td>
        <td class="px-4 py-3 text-white/60 text-sm">
          {{ invoice.due_date ? new Date(invoice.due_date).toLocaleDateString('vi-VN') : 'N/A' }}
        </td>
        <td class="px-4 py-3 text-white/60 text-sm">
          {{ new Date(invoice.created_at).toLocaleDateString('vi-VN') }}
        </td>
        <td class="px-4 py-3">
          <div class="flex items-center gap-2">
            <Button
              variant="ghost"
              size="sm"
              icon="fas fa-eye"
              @click="emit('view', invoice.id)"
            >
            </Button>
            <Button
              v-if="invoice.status === 'draft' || invoice.status === 'pending'"
              variant="ghost"
              size="sm"
              icon="fas fa-edit"
              @click="emit('edit', invoice.id)"
            >
            </Button>
            <Button
              v-if="invoice.status === 'pending'"
              variant="ghost"
              size="sm"
              icon="fas fa-check text-green-400"
              @click="emit('approve', invoice.id)"
            >
            </Button>
            <Button
              v-if="invoice.status === 'pending' || invoice.status === 'draft'"
              variant="ghost"
              size="sm"
              icon="fas fa-times text-red-400"
              @click="emit('reject', invoice.id)"
            >
            </Button>
            <Button
              v-if="invoice.status === 'draft'"
              variant="ghost"
              size="sm"
              icon="fas fa-trash text-red-400"
              @click="emit('delete', invoice.id)"
            >
            </Button>
          </div>
        </td>
      </tr>
    </template>
  </Table>
</template>

