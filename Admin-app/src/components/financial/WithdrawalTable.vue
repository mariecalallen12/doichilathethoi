<script setup>
import Table from '../ui/Table.vue';
import Badge from '../ui/Badge.vue';
import Button from '../ui/Button.vue';

const props = defineProps({
  withdrawals: {
    type: Array,
    default: () => [],
  },
  loading: Boolean,
  pagination: {
    type: Object,
    default: null,
  },
});

const emit = defineEmits(['view', 'approve', 'reject', 'page-change']);

const headers = [
  { key: 'withdrawal_id', label: 'Withdrawal ID', sortable: true },
  { key: 'user_id', label: 'User ID', sortable: true },
  { key: 'amount', label: 'Số tiền', sortable: true },
  { key: 'method', label: 'Phương thức', sortable: true },
  { key: 'destination', label: 'Đích đến', sortable: false },
  { key: 'status', label: 'Trạng thái', sortable: true },
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

const formatDestination = (withdrawal) => {
  if (withdrawal.method === 'Bank Transfer') {
    return `${withdrawal.bank_name} ****${withdrawal.account_number?.slice(-4)}`;
  } else if (withdrawal.method === 'Crypto') {
    const address = withdrawal.wallet_address || '';
    return `${address.slice(0, 6)}...${address.slice(-4)}`;
  }
  return 'N/A';
};
</script>

<template>
  <Table
    :headers="headers"
    :data="withdrawals"
    :loading="loading"
    :pagination="pagination"
    @page-change="emit('page-change', $event)"
  >
    <template #default="{ data }">
      <tr
        v-for="withdrawal in data"
        :key="withdrawal.id"
        class="border-b border-white/5 hover:bg-white/5 transition-colors"
      >
        <td class="px-4 py-3 text-white/80 text-sm font-mono">{{ withdrawal.withdrawal_id || withdrawal.id }}</td>
        <td class="px-4 py-3 text-white/80 text-sm">{{ withdrawal.user_id }}</td>
        <td class="px-4 py-3 text-white font-semibold">${{ withdrawal.amount?.toLocaleString() }}</td>
        <td class="px-4 py-3 text-white/80 text-sm">{{ withdrawal.method }}</td>
        <td class="px-4 py-3 text-white/60 text-sm font-mono text-xs">{{ formatDestination(withdrawal) }}</td>
        <td class="px-4 py-3">
          <Badge :type="getStatusType(withdrawal.status)">
            {{ withdrawal.status }}
          </Badge>
        </td>
        <td class="px-4 py-3 text-white/60 text-sm">{{ new Date(withdrawal.timestamp || withdrawal.created_at).toLocaleDateString('vi-VN') }}</td>
        <td class="px-4 py-3">
          <div class="flex items-center gap-2">
            <Button
              variant="ghost"
              size="sm"
              icon="fas fa-eye"
              @click="emit('view', withdrawal.id)"
            >
            </Button>
            <Button
              v-if="withdrawal.status === 'pending'"
              variant="ghost"
              size="sm"
              icon="fas fa-check text-green-400"
              @click="emit('approve', withdrawal.id)"
            >
            </Button>
            <Button
              v-if="withdrawal.status === 'pending'"
              variant="ghost"
              size="sm"
              icon="fas fa-times text-red-400"
              @click="emit('reject', withdrawal.id)"
            >
            </Button>
          </div>
        </td>
      </tr>
    </template>
  </Table>
</template>

