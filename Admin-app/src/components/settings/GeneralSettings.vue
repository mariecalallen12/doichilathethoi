<script setup>
import { ref } from 'vue';
import Input from '../ui/Input.vue';
import Select from '../ui/Select.vue';
import ToggleSwitch from './ToggleSwitch.vue';
import Card from '../ui/Card.vue';

const props = defineProps({
  settings: {
    type: Object,
    default: () => ({}),
  },
});

const emit = defineEmits(['update:settings']);

const localSettings = ref({
  platformName: 'CMEETRADING',
  platformURL: 'https://digitalutopia.com',
  supportEmail: 'support@digitalutopia.com',
  timezone: 'UTC',
  defaultLanguage: 'en',
  maintenanceMode: false,
  allowRegistrations: true,
  autoApproveRegistration: false,  // Auto approve registration setting
  ...props.settings,
});

const timezoneOptions = [
  { value: 'UTC', label: 'UTC' },
  { value: 'America/New_York', label: 'Eastern' },
  { value: 'America/Chicago', label: 'Central' },
  { value: 'America/Denver', label: 'Mountain' },
  { value: 'America/Los_Angeles', label: 'Pacific' },
  { value: 'Europe/London', label: 'London' },
  { value: 'Europe/Paris', label: 'Paris' },
  { value: 'Asia/Tokyo', label: 'Tokyo' },
];

const languageOptions = [
  { value: 'en', label: 'English' },
  { value: 'es', label: 'Spanish' },
  { value: 'fr', label: 'French' },
  { value: 'de', label: 'German' },
  { value: 'zh', label: 'Chinese' },
  { value: 'ja', label: 'Japanese' },
];

const updateSetting = (key, value) => {
  localSettings.value[key] = value;
  emit('update:settings', { ...localSettings.value });
};
</script>

<template>
  <Card title="Cài đặt chung">
    <div class="space-y-4">
      <Input
        v-model="localSettings.platformName"
        label="Tên platform"
        @update:model-value="updateSetting('platformName', $event)"
      />
      <Input
        v-model="localSettings.platformURL"
        label="Platform URL"
        @update:model-value="updateSetting('platformURL', $event)"
      />
      <Input
        v-model="localSettings.supportEmail"
        label="Email hỗ trợ"
        type="email"
        @update:model-value="updateSetting('supportEmail', $event)"
      />
      <Select
        v-model="localSettings.timezone"
        label="Múi giờ"
        :options="timezoneOptions"
        @update:model-value="updateSetting('timezone', $event)"
      />
      <Select
        v-model="localSettings.defaultLanguage"
        label="Ngôn ngữ mặc định"
        :options="languageOptions"
        @update:model-value="updateSetting('defaultLanguage', $event)"
      />
      <div class="border-t border-white/10 pt-4 space-y-2">
        <ToggleSwitch
          v-model="localSettings.maintenanceMode"
          label="Chế độ bảo trì"
          description="Bật chế độ bảo trì để ngăn người dùng truy cập"
          @update:model-value="updateSetting('maintenanceMode', $event)"
        />
        <ToggleSwitch
          v-model="localSettings.allowRegistrations"
          label="Cho phép đăng ký mới"
          description="Cho phép người dùng mới đăng ký tài khoản"
          @update:model-value="updateSetting('allowRegistrations', $event)"
        />
        <ToggleSwitch
          v-model="localSettings.autoApproveRegistration"
          label="Tự động phê duyệt đăng ký"
          description="Tự động phê duyệt tài khoản mới đăng ký (không cần admin xét duyệt)"
          @update:model-value="updateSetting('autoApproveRegistration', $event)"
        />
      </div>
    </div>
  </Card>
</template>

