<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import api from '../../services/api';
import toastService from '../../services/toast';
import Button from '../ui/Button.vue';
import Input from '../ui/Input.vue';

const props = defineProps({
  show: Boolean,
});

const emit = defineEmits(['close', 'update:show']);

const loading = ref(false);
const saving = ref(false);

// Default field definitions
const defaultFields = [
  {
    key: 'fullName',
    label: 'Họ và Tên',
    enabled: true,
    required: true,
    type: 'text',
    placeholder: 'Nhập họ và tên đầy đủ',
    locked: false, // Cannot disable email and password
  },
  {
    key: 'email',
    label: 'Email',
    enabled: true,
    required: true,
    type: 'email',
    placeholder: 'example@gmail.com',
    locked: true, // Always required and enabled
  },
  {
    key: 'phone',
    label: 'Số Điện Thoại',
    enabled: true,
    required: true,
    type: 'tel',
    placeholder: '+84 xxx xxx xxx',
    locked: false,
  },
  {
    key: 'dateOfBirth',
    label: 'Ngày Sinh',
    enabled: false,
    required: false,
    type: 'date',
    placeholder: '',
    locked: false,
  },
  {
    key: 'password',
    label: 'Mật Khẩu',
    enabled: true,
    required: true,
    type: 'password',
    placeholder: 'Tối thiểu 8 ký tự',
    locked: true, // Always required and enabled
  },
  {
    key: 'confirmPassword',
    label: 'Xác Nhận Mật Khẩu',
    enabled: true,
    required: true,
    type: 'password',
    placeholder: 'Nhập lại mật khẩu',
    locked: false, // But should be enabled if password is enabled
  },
  {
    key: 'country',
    label: 'Quốc Gia',
    enabled: false,  // Locked - always disabled, default value set in backend
    required: false,
    type: 'select',
    placeholder: 'Chọn quốc gia',
    locked: true,  // Cannot be enabled - giá trị mặc định "VN" được set tự động
  },
  {
    key: 'tradingExperience',
    label: 'Kinh Nghiệm Giao Dịch',
    enabled: false,  // Locked - always disabled, default value set in backend
    required: false,
    type: 'select',
    placeholder: 'Chọn mức độ kinh nghiệm',
    locked: true,  // Cannot be enabled - giá trị mặc định "Chưa có kinh nghiệm" được set tự động
  },
  {
    key: 'referralCode',
    label: 'Mã Giới Thiệu',
    enabled: false,  // Locked - always disabled, default value set in backend
    required: false,
    type: 'text',
    placeholder: 'Nhập mã giới thiệu (nếu có)',
    locked: true,  // Cannot be enabled - giá trị mặc định null được set tự động
  },
  {
    key: 'agreeTerms',
    label: 'Đồng ý điều khoản',
    enabled: true,
    required: true,
    type: 'checkbox',
    placeholder: '',
    locked: false,
  },
  {
    key: 'agreeMarketing',
    label: 'Đồng ý nhận marketing',
    enabled: true,
    required: false,
    type: 'checkbox',
    placeholder: '',
    locked: false,
  },
];

const fields = ref([]);

// Computed to check if form has changes
const hasChanges = computed(() => {
  // Compare with original config if needed
  return true; // For now, always allow save
});

// Load configuration from API
const loadConfig = async () => {
  loading.value = true;
  try {
    const response = await api.get('/api/admin/settings/registration-fields');
    // Backend returns: { success: true, data: { fields: [...] } }
    // Unwrap the data property
    let config = null;
    if (response && response.data && response.data.fields) {
      // Nested structure: { data: { fields: [...] } }
      config = response.data;
    } else if (response && response.fields) {
      // Direct structure: { fields: [...] }
      config = response;
    } else if (response && response.data) {
      // Try response.data directly
      config = response.data;
    }
    
    if (config && config.fields) {
      // Merge with defaults to ensure all fields are present
      const loadedFields = config.fields;
      fields.value = defaultFields.map(defaultField => {
        const loadedField = loadedFields.find(f => f.key === defaultField.key);
        if (loadedField) {
          return {
            ...defaultField,
            ...loadedField,
            // Ensure locked fields stay enabled and required
            enabled: defaultField.locked ? true : loadedField.enabled,
            required: defaultField.locked ? true : loadedField.required,
          };
        }
        return defaultField;
      });
    } else {
      // Use defaults if no config exists
      fields.value = JSON.parse(JSON.stringify(defaultFields));
    }
  } catch (error) {
    console.error('Failed to load registration fields config:', error);
    // Use defaults on error
    fields.value = JSON.parse(JSON.stringify(defaultFields));
    toastService.warning('Không thể tải cấu hình. Sử dụng cấu hình mặc định.');
  } finally {
    loading.value = false;
  }
};

// Save configuration
const saveConfig = async () => {
  saving.value = true;
  try {
    const config = {
      fields: fields.value.map(field => ({
        key: field.key,
        label: field.label,
        enabled: field.enabled,
        required: field.required,
        type: field.type,
        placeholder: field.placeholder || '',
      })),
    };

    await api.put('/api/admin/settings/registration-fields', config);
    toastService.success('Đã lưu cấu hình thành công');
    emit('close');
  } catch (error) {
    console.error('Failed to save registration fields config:', error);
    toastService.error(error.message || 'Không thể lưu cấu hình');
  } finally {
    saving.value = false;
  }
};

// Toggle field enabled
const toggleEnabled = (field) => {
  // Prevent enabling/disabling locked fields
  if (field.locked) {
    if (field.key === 'country' || field.key === 'tradingExperience' || field.key === 'referralCode') {
      toastService.warning(`Trường "${field.label}" đã bị khóa. Giá trị mặc định được set tự động ở backend và không thể thay đổi.`);
    } else {
    toastService.warning('Trường này không thể tắt');
    }
    return;
  }
  
  // If disabling, also make it not required
  if (field.enabled) {
    field.enabled = false;
    field.required = false;
  } else {
    field.enabled = true;
  }
  
  // Special handling for confirmPassword
  if (field.key === 'password' && !field.enabled) {
    const confirmField = fields.value.find(f => f.key === 'confirmPassword');
    if (confirmField) {
      confirmField.enabled = false;
      confirmField.required = false;
    }
  }
  
  // If password is enabled, ensure confirmPassword is enabled
  if (field.key === 'password' && field.enabled) {
    const confirmField = fields.value.find(f => f.key === 'confirmPassword');
    if (confirmField) {
      confirmField.enabled = true;
    }
  }
};

// Toggle field required
const toggleRequired = (field) => {
  if (field.locked) {
    toastService.warning('Trường này luôn bắt buộc');
    return;
  }
  
  if (!field.enabled) {
    toastService.warning('Vui lòng bật trường trước khi đặt là bắt buộc');
    return;
  }
  
  field.required = !field.required;
};

// Update field label
const updateLabel = (field, newLabel) => {
  if (!newLabel.trim()) {
    toastService.warning('Label không được để trống');
    return;
  }
  field.label = newLabel.trim();
};

onMounted(() => {
  if (props.show) {
    loadConfig();
  }
});

// Watch for show prop changes
watch(() => props.show, (newVal) => {
  if (newVal) {
    loadConfig();
  }
});
</script>

<template>
  <div v-if="show" class="space-y-6">
    <div class="mb-6">
      <h3 class="text-lg font-semibold text-white mb-2">Cấu hình trường đăng ký</h3>
      <p class="text-sm text-white/60">
        Quản lý các trường hiển thị trong form đăng ký. Email và Mật khẩu luôn bắt buộc.
      </p>
    </div>

    <div v-if="loading" class="text-center py-8">
      <i class="fas fa-spinner fa-spin text-purple-400 text-2xl"></i>
      <p class="text-white/60 mt-2">Đang tải cấu hình...</p>
    </div>

    <div v-else class="space-y-4 max-h-[60vh] overflow-y-auto pr-2">
      <div
        v-for="field in fields"
        :key="field.key"
        class="bg-slate-800/50 rounded-lg p-4 border border-white/10 hover:border-purple-500/30 transition-colors"
      >
        <div class="flex items-start justify-between gap-4">
          <!-- Left: Field Info -->
          <div class="flex-1 space-y-3">
            <!-- Field Key (readonly) -->
            <div>
              <div class="flex items-center gap-2">
              <label class="text-xs text-white/40 uppercase tracking-wide">Mã trường</label>
                <span v-if="field.locked && (field.key === 'country' || field.key === 'tradingExperience' || field.key === 'referralCode')" 
                      class="text-xs px-2 py-0.5 bg-yellow-500/20 text-yellow-400 rounded border border-yellow-500/30">
                  Đã khóa
                </span>
              </div>
              <p class="text-sm text-white/80 font-mono">{{ field.key }}</p>
              <p v-if="field.locked && (field.key === 'country' || field.key === 'tradingExperience' || field.key === 'referralCode')" 
                 class="text-xs text-yellow-400/80 mt-1">
                Giá trị mặc định được set tự động ở backend
              </p>
            </div>

            <!-- Label Input -->
            <div>
              <label class="block text-sm font-medium text-white mb-1">
                Tên hiển thị
              </label>
              <Input
                :model-value="field.label"
                @update:model-value="updateLabel(field, $event)"
                :disabled="field.locked"
                placeholder="Nhập tên hiển thị"
                class="w-full"
              />
            </div>

            <!-- Type and Placeholder -->
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-xs text-white/40 mb-1">Loại</label>
                <p class="text-sm text-white/80">{{ field.type }}</p>
              </div>
              <div v-if="field.placeholder">
                <label class="block text-xs text-white/40 mb-1">Placeholder</label>
                <p class="text-sm text-white/80 truncate">{{ field.placeholder }}</p>
              </div>
            </div>
          </div>

          <!-- Right: Toggles -->
          <div class="flex flex-col items-end gap-3">
            <!-- Enabled Toggle -->
            <div class="flex items-center gap-2">
              <label class="text-sm text-white/80">Hiển thị</label>
              <button
                @click="toggleEnabled(field)"
                :disabled="field.locked"
                :class="[
                  'relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 focus:ring-offset-slate-900',
                  field.enabled
                    ? 'bg-purple-600'
                    : 'bg-slate-600',
                  field.locked ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'
                ]"
              >
                <span
                  :class="[
                    'inline-block h-4 w-4 transform rounded-full bg-white transition-transform',
                    field.enabled ? 'translate-x-6' : 'translate-x-1'
                  ]"
                />
              </button>
            </div>

            <!-- Required Toggle -->
            <div class="flex items-center gap-2">
              <label class="text-sm text-white/80">Bắt buộc</label>
              <button
                @click="toggleRequired(field)"
                :disabled="field.locked || !field.enabled"
                :class="[
                  'relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 focus:ring-offset-slate-900',
                  field.required
                    ? 'bg-red-600'
                    : 'bg-slate-600',
                  (field.locked || !field.enabled) ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'
                ]"
              >
                <span
                  :class="[
                    'inline-block h-4 w-4 transform rounded-full bg-white transition-transform',
                    field.required ? 'translate-x-6' : 'translate-x-1'
                  ]"
                />
              </button>
            </div>

            <!-- Locked Indicator -->
            <div v-if="field.locked" class="flex items-center gap-1 text-xs text-yellow-400">
              <i class="fas fa-lock"></i>
              <span>Khóa</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Actions -->
    <div class="flex items-center justify-end gap-3 pt-4 border-t border-white/10">
      <Button
        variant="secondary"
        @click="$emit('close')"
        :disabled="saving"
      >
        Hủy
      </Button>
      <Button
        variant="primary"
        @click="saveConfig"
        :disabled="saving || loading"
        :loading="saving"
      >
        <i class="fas fa-save mr-2"></i>
        Lưu cấu hình
      </Button>
    </div>
  </div>
</template>

<style scoped>
/* Custom scrollbar */
.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: rgba(147, 51, 234, 0.5);
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: rgba(147, 51, 234, 0.7);
}
</style>

