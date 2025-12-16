<script setup>
import Modal from '../ui/Modal.vue';
import Card from '../ui/Card.vue';
import Badge from '../ui/Badge.vue';
import Button from '../ui/Button.vue';

const props = defineProps({
  show: Boolean,
  invoice: {
    type: Object,
    default: null,
  },
});

const emit = defineEmits(['close', 'update:show', 'edit', 'approve', 'reject', 'delete']);

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
  <Modal
    :show="show"
    title="Chi tiết hóa đơn"
    size="xl"
    @update:show="emit('update:show', $event)"
    @close="emit('close')"
  >
    <div v-if="invoice" class="space-y-4">
      <!-- Invoice Header -->
      <div class="flex items-start justify-between">
        <div>
          <h3 class="text-2xl font-bold text-white mb-2">
            Hóa đơn #{{ invoice.invoice_number || invoice.id }}
          </h3>
          <p class="text-white/60">User ID: {{ invoice.user_id }}</p>
        </div>
        <Badge :type="getStatusType(invoice.status)">
          {{ getStatusText(invoice.status) }}
        </Badge>
      </div>

      <!-- Invoice Info -->
      <div class="grid grid-cols-2 gap-4">
        <Card padding="p-4">
          <p class="text-white/60 text-sm mb-1">Số tiền</p>
          <p class="text-white text-2xl font-bold">${{ invoice.amount?.toLocaleString() }}</p>
        </Card>
        <Card padding="p-4">
          <p class="text-white/60 text-sm mb-1">Ngày đến hạn</p>
          <p class="text-white font-semibold">
            {{ invoice.due_date ? new Date(invoice.due_date).toLocaleDateString('vi-VN') : 'N/A' }}
          </p>
        </Card>
        <Card padding="p-4">
          <p class="text-white/60 text-sm mb-1">Ngày tạo</p>
          <p class="text-white font-semibold">
            {{ new Date(invoice.created_at).toLocaleDateString('vi-VN') }}
          </p>
        </Card>
        <Card padding="p-4">
          <p class="text-white/60 text-sm mb-1">Ngày cập nhật</p>
          <p class="text-white font-semibold">
            {{ invoice.updated_at ? new Date(invoice.updated_at).toLocaleDateString('vi-VN') : 'N/A' }}
          </p>
        </Card>
      </div>

      <!-- Description -->
      <Card padding="p-4" v-if="invoice.description">
        <p class="text-white/60 text-sm mb-2">Mô tả</p>
        <p class="text-white">{{ invoice.description }}</p>
      </Card>

      <!-- Invoice Items -->
      <Card v-if="invoice.items && invoice.items.length > 0" title="Chi tiết hóa đơn" padding="p-4">
        <div class="space-y-2">
          <div
            v-for="(item, index) in invoice.items"
            :key="index"
            class="flex items-center justify-between p-3 bg-white/5 rounded-lg"
          >
            <div class="flex-1">
              <p class="text-white font-semibold">{{ item.name }}</p>
              <p class="text-white/60 text-sm">
                {{ item.quantity }} x ${{ item.price?.toLocaleString() }} = 
                ${{ ((item.quantity || 1) * (item.price || 0)).toLocaleString() }}
              </p>
              <p v-if="item.description" class="text-white/40 text-xs mt-1">{{ item.description }}</p>
            </div>
          </div>
        </div>
      </Card>

      <!-- Actions -->
      <div class="flex items-center justify-end gap-3 pt-4 border-t border-white/10">
        <Button variant="outline" @click="emit('close')">Đóng</Button>
        <Button
          v-if="invoice.status === 'draft' || invoice.status === 'pending'"
          variant="primary"
          @click="emit('edit', invoice.id)"
        >
          Sửa
        </Button>
        <Button
          v-if="invoice.status === 'pending'"
          variant="primary"
          @click="emit('approve', invoice.id)"
        >
          Phê duyệt
        </Button>
        <Button
          v-if="invoice.status === 'pending' || invoice.status === 'draft'"
          variant="danger"
          @click="emit('reject', invoice.id)"
        >
          Từ chối
        </Button>
        <Button
          v-if="invoice.status === 'draft'"
          variant="danger"
          @click="emit('delete', invoice.id)"
        >
          Xóa
        </Button>
      </div>
    </div>
    <div v-else class="text-center py-8">
      <i class="fas fa-spinner fa-spin text-primary text-3xl"></i>
    </div>
  </Modal>
</template>

