<script setup>
import { computed } from 'vue';
import Modal from '../ui/Modal.vue';
import Card from '../ui/Card.vue';
import Badge from '../ui/Badge.vue';
import Button from '../ui/Button.vue';

const props = defineProps({
  show: Boolean,
  user: {
    type: Object,
    default: null,
  },
  loading: Boolean,
});

const emit = defineEmits(['close', 'update:show', 'update-status']);

const getStatusType = (status) => {
  const statusMap = {
    active: 'active',
    suspended: 'suspended',
    banned: 'banned',
  };
  return statusMap[status] || 'default';
};

const handleStatusUpdate = (newStatus) => {
  emit('update-status', props.user.id, newStatus);
};
</script>

<template>
  <Modal
    :show="show"
    title="Chi tiết người dùng"
    size="xl"
    @update:show="emit('update:show', $event)"
    @close="emit('close')"
  >
    <div v-if="user" class="space-y-6">
      <!-- User Info -->
      <div class="flex items-start gap-6">
        <div class="w-20 h-20 rounded-full bg-gradient-button flex items-center justify-center">
          <i class="fas fa-user text-white text-3xl"></i>
        </div>
        <div class="flex-1">
          <h3 class="text-2xl font-bold text-white mb-2">{{ user.display_name || user.full_name }}</h3>
          <p class="text-white/60 mb-3">{{ user.email }}</p>
          <Badge :type="getStatusType(user.status)">
            {{ user.status }}
          </Badge>
        </div>
      </div>

      <!-- User Details Grid -->
      <div class="grid grid-cols-2 gap-4">
        <Card padding="p-4">
          <p class="text-white/60 text-sm mb-1">UID</p>
          <p class="text-white font-medium">{{ user.uid || user.id }}</p>
        </Card>
        <Card padding="p-4">
          <p class="text-white/60 text-sm mb-1">Email Verification</p>
          <Badge :type="user.email_verified ? 'success' : 'warning'">
            {{ user.email_verified ? 'Đã xác thực' : 'Chưa xác thực' }}
          </Badge>
        </Card>
        <Card padding="p-4">
          <p class="text-white/60 text-sm mb-1">Ngày đăng ký</p>
          <p class="text-white font-medium">{{ new Date(user.join_date || user.created_at).toLocaleDateString('vi-VN') }}</p>
        </Card>
        <Card padding="p-4">
          <p class="text-white/60 text-sm mb-1">Lần đăng nhập cuối</p>
          <p class="text-white font-medium">{{ user.last_login ? new Date(user.last_login).toLocaleDateString('vi-VN') : 'N/A' }}</p>
        </Card>
      </div>

      <!-- Trading Statistics -->
      <Card title="Thống kê giao dịch" padding="p-4">
        <div class="grid grid-cols-3 gap-4">
          <div>
            <p class="text-white/60 text-sm mb-1">Tổng giao dịch</p>
            <p class="text-white text-2xl font-bold">{{ user.total_trades || 0 }}</p>
          </div>
          <div>
            <p class="text-white/60 text-sm mb-1">Tổng giá trị</p>
            <p class="text-white text-2xl font-bold">${{ (user.total_volume || 0).toLocaleString() }}</p>
          </div>
          <div>
            <p class="text-white/60 text-sm mb-1">Win Rate</p>
            <p class="text-white text-2xl font-bold">{{ (user.win_rate || 0).toFixed(1) }}%</p>
          </div>
        </div>
      </Card>

      <!-- Risk Assessment -->
      <Card title="Đánh giá rủi ro" padding="p-4">
        <div class="space-y-3">
          <div class="flex items-center justify-between">
            <span class="text-white/80">Mức độ rủi ro</span>
            <Badge :type="user.risk_level === 'high' ? 'error' : user.risk_level === 'medium' ? 'warning' : 'success'">
              {{ user.risk_level || 'Low' }}
            </Badge>
          </div>
        </div>
      </Card>

      <!-- Actions -->
      <div class="flex items-center justify-end gap-3 pt-4 border-t border-white/10">
        <Button variant="outline" @click="emit('close')">Đóng</Button>
        <Button
          v-if="user.status !== 'active'"
          variant="primary"
          @click="handleStatusUpdate('active')"
        >
          Kích hoạt
        </Button>
        <Button
          v-if="user.status !== 'suspended'"
          variant="warning"
          @click="handleStatusUpdate('suspended')"
        >
          Tạm khóa
        </Button>
        <Button
          v-if="user.status !== 'banned'"
          variant="danger"
          @click="handleStatusUpdate('banned')"
        >
          Cấm
        </Button>
      </div>
    </div>
    <div v-else class="text-center py-8">
      <i class="fas fa-spinner fa-spin text-primary text-3xl"></i>
    </div>
  </Modal>
</template>

