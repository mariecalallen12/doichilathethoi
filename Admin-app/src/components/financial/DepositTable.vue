<script setup>
import Table from '../ui/Table.vue';
import Badge from '../ui/Badge.vue';
import Button from '../ui/Button.vue';

const props = defineProps({
  deposits: {
    type: Array,
    default: () => [],
  },
  loading: Boolean,
  pagination: {
    type: Object,
    default: null,
  },
});

const emit = defineEmits(['view', 'approve', 'reject', 'view-receipt', 'page-change']);

const headers = [
  { key: 'deposit_id', label: 'Deposit ID', sortable: true },
  { key: 'user_id', label: 'User ID', sortable: true },
  { key: 'amount', label: 'Số tiền', sortable: true },
  { key: 'method', label: 'Phương thức', sortable: true },
  { key: 'status', label: 'Trạng thái', sortable: true },
  { key: 'transaction_id', label: 'Transaction ID', sortable: true },
  { key: 'timestamp', label: 'Thời gian', sortable: true },
  { key: 'actions', label: 'Thao tác', sortable: false },
];

const getStatusType = (status) => {
  const statusMap = {
    pending: 'pending',
    approved: 'approved',
    rejected: 'rejected',
  };
  return statusMap[status] || 'default';
};
</script>

<template>
  <Table
    :headers="headers"
    :data="deposits"
    :loading="loading"
    :pagination="pagination"
    @page-change="emit('page-change', $event)"
  >
    <template #default="{ data }">
      <tr
        v-for="deposit in data"
        :key="deposit.id"
        class="border-b border-white/5 hover:bg-white/5 transition-colors"
      >
        <td class="px-4 py-3 text-white/80 text-sm font-mono">{{ deposit.deposit_id || deposit.id }}</td>
        <td class="px-4 py-3 text-white/80 text-sm">{{ deposit.user_id }}</td>
        <td class="px-4 py-3 text-white font-semibold">${{ deposit.amount?.toLocaleString() }}</td>
        <td class="px-4 py-3 text-white/80 text-sm">{{ deposit.method }}</td>
        <td class="px-4 py-3">
          <Badge :type="getStatusType(deposit.status)">
            {{ deposit.status }}
          </Badge>
        </td>
        <td class="px-4 py-3 text-white/60 text-sm font-mono text-xs">{{ deposit.transaction_id || 'N/A' }}</td>
        <td class="px-4 py-3 text-white/60 text-sm">{{ new Date(deposit.timestamp || deposit.created_at).toLocaleDateString('vi-VN') }}</td>
        <td class="px-4 py-3">
          <div class="flex items-center gap-2">
            <Button
              variant="ghost"
              size="sm"
              icon="fas fa-eye"
              @click="emit('view', deposit.id)"
            >
            </Button>
            <Button
              v-if="deposit.receipt_url"
              variant="ghost"
              size="sm"
              icon="fas fa-file-image"
              @click="emit('view-receipt', deposit.id)"
            >
            </Button>
            <Button
              v-if="deposit.status === 'pending'"
              variant="ghost"
              size="sm"
              icon="fas fa-check text-green-400"
              @click="emit('approve', deposit.id)"
            >
            </Button>
            <Button
              v-if="deposit.status === 'pending'"
              variant="ghost"
              size="sm"
              icon="fas fa-times text-red-400"
              @click="emit('reject', deposit.id)"
            >
            </Button>
          </div>
        </td>
      </tr>
    </template>
  </Table>
</template>

