<script setup>
import { ref } from 'vue';
import Input from '../ui/Input.vue';
import Select from '../ui/Select.vue';
import Button from '../ui/Button.vue';

const props = defineProps({
  filters: {
    type: Object,
    default: () => ({
      search: '',
      status: 'all',
      sortBy: 'created_at',
      sortOrder: 'desc',
    }),
  },
});

const emit = defineEmits(['update:filters', 'search', 'export']);

const statusOptions = [
  { value: 'all', label: 'Tất cả' },
  { value: 'active', label: 'Hoạt động' },
  { value: 'suspended', label: 'Tạm khóa' },
  { value: 'banned', label: 'Cấm' },
];

const sortOptions = [
  { value: 'created_at', label: 'Ngày đăng ký' },
  { value: 'email', label: 'Email' },
  { value: 'display_name', label: 'Tên' },
  { value: 'last_login', label: 'Lần đăng nhập cuối' },
];

const localFilters = ref({ ...props.filters });

const updateFilter = (key, value) => {
  localFilters.value[key] = value;
  emit('update:filters', { ...localFilters.value });
};

const handleSearch = () => {
  emit('search', localFilters.value);
};

const exportFormat = ref('excel');

const handleExport = () => {
  emit('export', exportFormat.value);
};
</script>

<template>
  <div class="glass-effect rounded-xl p-4 mb-6">
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <Input
        v-model="localFilters.search"
        placeholder="Tìm theo tên hoặc email..."
        icon="fas fa-search"
        @update:model-value="updateFilter('search', $event)"
      />
      <Select
        v-model="localFilters.status"
        :options="statusOptions"
        placeholder="Lọc theo trạng thái"
        @update:model-value="updateFilter('status', $event)"
      />
      <Select
        v-model="localFilters.sortBy"
        :options="sortOptions"
        placeholder="Sắp xếp theo"
        @update:model-value="updateFilter('sortBy', $event)"
      />
      <div class="flex items-center gap-2">
        <Button variant="primary" @click="handleSearch" icon="fas fa-search">
          Tìm kiếm
        </Button>
        <select
          v-model="exportFormat"
          class="px-3 py-2 rounded-lg bg-white/10 border border-white/20 text-white text-sm"
        >
          <option value="excel">Excel</option>
          <option value="csv">CSV</option>
        </select>
        <Button variant="secondary" @click="handleExport" icon="fas fa-download">
          Xuất
        </Button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.glass-effect {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}
</style>

