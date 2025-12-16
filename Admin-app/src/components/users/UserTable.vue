<script setup>
import { ref } from 'vue';
import Table from '../ui/Table.vue';
import Badge from '../ui/Badge.vue';
import Button from '../ui/Button.vue';

const props = defineProps({
  users: {
    type: Array,
    default: () => [],
  },
  loading: Boolean,
  selectedUsers: {
    type: Array,
    default: () => [],
  },
  pagination: {
    type: Object,
    default: null,
  },
});

const emit = defineEmits(['select', 'select-all', 'view', 'update-status', 'page-change']);

const headers = [
  { key: 'select', label: '', sortable: false },
  { key: 'uid', label: 'UID', sortable: true },
  { key: 'email', label: 'Email', sortable: true },
  { key: 'display_name', label: 'Tên hiển thị', sortable: true },
  { key: 'status', label: 'Trạng thái', sortable: true },
  { key: 'email_verified', label: 'Xác thực Email', sortable: true },
  { key: 'join_date', label: 'Ngày đăng ký', sortable: true },
  { key: 'last_login', label: 'Lần đăng nhập cuối', sortable: true },
  { key: 'actions', label: 'Thao tác', sortable: false },
];

const getStatusType = (status) => {
  const statusMap = {
    active: 'active',
    suspended: 'suspended',
    banned: 'banned',
  };
  return statusMap[status] || 'default';
};

const getStatusText = (status) => {
  const textMap = {
    active: 'Hoạt động',
    suspended: 'Tạm khóa',
    banned: 'Cấm',
  };
  return textMap[status] || status;
};

const formatDate = (date) => {
  if (!date) return 'N/A';
  return new Date(date).toLocaleDateString('vi-VN');
};

const isSelected = (userId) => {
  return props.selectedUsers.includes(userId);
};

const toggleSelect = (userId) => {
  emit('select', userId);
};

const toggleSelectAll = () => {
  emit('select-all');
};
</script>

<template>
  <Table
    :headers="headers"
    :data="users"
    :loading="loading"
    :pagination="pagination"
    @page-change="emit('page-change', $event)"
    @sort="emit('sort', $event)"
  >
    <template #default="{ data }">
      <tr
        v-for="user in data"
        :key="user.id"
        class="border-b border-white/5 hover:bg-white/5 transition-colors"
      >
        <td class="px-4 py-3">
          <input
            type="checkbox"
            :checked="isSelected(user.id)"
            @change="toggleSelect(user.id)"
            class="w-4 h-4 rounded border-white/30 bg-white/10 text-primary focus:ring-primary/50"
          />
        </td>
        <td class="px-4 py-3 text-white/80 text-sm">{{ user.uid || user.id }}</td>
        <td class="px-4 py-3 text-white/80 text-sm">{{ user.email }}</td>
        <td class="px-4 py-3">
          <div class="flex items-center gap-2">
            <img
              v-if="user.avatar"
              :src="user.avatar"
              :alt="user.display_name"
              class="w-8 h-8 rounded-full"
            />
            <div
              v-else
              class="w-8 h-8 rounded-full bg-gradient-button flex items-center justify-center"
            >
              <i class="fas fa-user text-white text-xs"></i>
            </div>
            <span class="text-white/80 text-sm">{{ user.display_name || user.full_name }}</span>
          </div>
        </td>
        <td class="px-4 py-3">
          <Badge :type="getStatusType(user.status)">
            {{ getStatusText(user.status) }}
          </Badge>
        </td>
        <td class="px-4 py-3">
          <Badge :type="user.email_verified ? 'success' : 'warning'">
            {{ user.email_verified ? 'Đã xác thực' : 'Chưa xác thực' }}
          </Badge>
        </td>
        <td class="px-4 py-3 text-white/60 text-sm">{{ formatDate(user.join_date || user.created_at) }}</td>
        <td class="px-4 py-3 text-white/60 text-sm">{{ formatDate(user.last_login) }}</td>
        <td class="px-4 py-3">
          <div class="flex items-center gap-2">
            <Button
              variant="ghost"
              size="sm"
              icon="fas fa-eye"
              @click="emit('view', user.id)"
            >
            </Button>
            <Button
              variant="ghost"
              size="sm"
              icon="fas fa-edit"
              @click="emit('update-status', user.id)"
            >
            </Button>
          </div>
        </td>
      </tr>
    </template>
  </Table>
</template>

