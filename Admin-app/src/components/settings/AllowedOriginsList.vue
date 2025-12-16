<script setup>
import { ref, onMounted } from 'vue';
import api from '../../services/api';
import toastService from '../../services/toast';
import Card from '../ui/Card.vue';
import Input from '../ui/Input.vue';
import Button from '../ui/Button.vue';
import Badge from '../ui/Badge.vue';

const origins = ref([]);
const newOrigin = ref('');
const loading = ref(false);
const error = ref('');

const validateDomain = (domain) => {
  // Basic domain validation
  const domainRegex = /^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$/;
  const simpleDomainRegex = /^([\da-z\.-]+)\.([a-z\.]{2,6})$/;
  
  if (!domain || domain.trim().length === 0) {
    return 'Domain không được để trống';
  }
  
  const trimmed = domain.trim();
  
  // Remove protocol if present
  let domainOnly = trimmed.replace(/^https?:\/\//, '');
  
  // Remove trailing slash
  domainOnly = domainOnly.replace(/\/$/, '');
  
  if (!simpleDomainRegex.test(domainOnly) && !domainRegex.test(trimmed)) {
    return 'Domain không hợp lệ. Ví dụ: example.com hoặc https://example.com';
  }
  
  return null;
};

const fetchOrigins = async () => {
  loading.value = true;
  try {
    const response = await api.get('/api/admin/settings/cors-origins');
    const data = response.data?.data || response.data || {};
    origins.value = data.origins || data.allowed_origins || [];
  } catch (error) {
    console.error('Fetch origins error:', error);
    toastService.error('Không thể tải danh sách origins');
  } finally {
    loading.value = false;
  }
};

const handleAddOrigin = async () => {
  error.value = '';
  
  const validationError = validateDomain(newOrigin.value);
  if (validationError) {
    error.value = validationError;
    return;
  }
  
  // Normalize domain
  let domain = newOrigin.value.trim();
  if (!domain.startsWith('http://') && !domain.startsWith('https://')) {
    domain = `https://${domain}`;
  }
  domain = domain.replace(/\/$/, '');
  
  // Check if already exists
  if (origins.value.includes(domain)) {
    error.value = 'Domain này đã tồn tại';
    return;
  }
  
  loading.value = true;
  try {
    await api.post('/api/admin/settings/cors-origins', {
      origin: domain,
    });
    toastService.success('Đã thêm domain');
    newOrigin.value = '';
    error.value = '';
    await fetchOrigins();
  } catch (err) {
    console.error('Add origin error:', err);
    toastService.error(err.message || 'Không thể thêm domain');
  } finally {
    loading.value = false;
  }
};

const handleRemoveOrigin = async (origin) => {
  if (!confirm(`Bạn có chắc chắn muốn xóa domain "${origin}"?`)) {
    return;
  }
  
  loading.value = true;
  try {
    await api.delete('/api/admin/settings/cors-origins', {
      data: { origin },
    });
    toastService.success('Đã xóa domain');
    await fetchOrigins();
  } catch (err) {
    console.error('Remove origin error:', err);
    toastService.error(err.message || 'Không thể xóa domain');
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchOrigins();
});
</script>

<template>
  <Card title="Quản lý CORS Origins" padding="p-4">
    <div class="space-y-4">
      <!-- Add Origin Form -->
      <div class="space-y-2">
        <div class="flex items-center gap-2">
          <Input
            v-model="newOrigin"
            placeholder="Nhập domain (ví dụ: example.com hoặc https://example.com)"
            class="flex-1"
            @keyup.enter="handleAddOrigin"
          />
          <Button variant="primary" @click="handleAddOrigin" :loading="loading">
            <i class="fas fa-plus mr-2"></i>
            Thêm
          </Button>
        </div>
        <p v-if="error" class="text-red-400 text-sm">{{ error }}</p>
        <p class="text-white/40 text-xs">
          Nhập domain để cho phép truy cập từ origin này. Ví dụ: example.com, https://app.example.com
        </p>
      </div>
      
      <!-- Origins List -->
      <div v-if="origins.length > 0" class="space-y-2">
        <p class="text-white/60 text-sm font-semibold">Danh sách domains được phép:</p>
        <div class="space-y-2">
          <div
            v-for="(origin, index) in origins"
            :key="index"
            class="flex items-center justify-between p-3 bg-white/5 rounded-lg"
          >
            <div class="flex items-center gap-2">
              <Badge type="default">{{ origin }}</Badge>
            </div>
            <Button
              variant="ghost"
              size="sm"
              icon="fas fa-trash text-red-400"
              @click="handleRemoveOrigin(origin)"
            >
            </Button>
          </div>
        </div>
      </div>
      <div v-else class="text-center py-8 text-white/40">
        <i class="fas fa-globe text-4xl mb-2"></i>
        <p>Chưa có domain nào được thêm</p>
      </div>
    </div>
  </Card>
</template>

