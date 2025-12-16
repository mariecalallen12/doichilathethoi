<script setup>
import { ref, watch } from 'vue';
import Modal from '../ui/Modal.vue';
import Input from '../ui/Input.vue';
import Button from '../ui/Button.vue';
import Select from '../ui/Select.vue';

const props = defineProps({
  show: Boolean,
  loading: Boolean,
});

const emit = defineEmits(['close', 'update:show', 'submit']);

const formData = ref({
  email: '',
  password: '',
  display_name: '',
  status: 'active',
});

const errors = ref({});

const statusOptions = [
  { value: 'active', label: 'Hoạt động' },
  { value: 'suspended', label: 'Tạm khóa' },
  { value: 'banned', label: 'Cấm' },
];

const validateEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

const validatePassword = (password) => {
  if (password.length < 8) {
    return 'Mật khẩu phải có ít nhất 8 ký tự';
  }
  if (!/(?=.*[a-z])/.test(password)) {
    return 'Mật khẩu phải có ít nhất một chữ thường';
  }
  if (!/(?=.*[A-Z])/.test(password)) {
    return 'Mật khẩu phải có ít nhất một chữ hoa';
  }
  if (!/(?=.*\d)/.test(password)) {
    return 'Mật khẩu phải có ít nhất một số';
  }
  return null;
};

const validate = () => {
  errors.value = {};
  
  if (!formData.value.email) {
    errors.value.email = 'Email là bắt buộc';
  } else if (!validateEmail(formData.value.email)) {
    errors.value.email = 'Email không hợp lệ';
  }
  
  if (!formData.value.password) {
    errors.value.password = 'Mật khẩu là bắt buộc';
  } else {
    const passwordError = validatePassword(formData.value.password);
    if (passwordError) {
      errors.value.password = passwordError;
    }
  }
  
  if (!formData.value.display_name) {
    errors.value.display_name = 'Tên hiển thị là bắt buộc';
  }
  
  return Object.keys(errors.value).length === 0;
};

const handleSubmit = () => {
  if (!validate()) {
    return;
  }
  
  emit('submit', { ...formData.value });
};

const resetForm = () => {
  formData.value = {
    email: '',
    password: '',
    display_name: '',
    status: 'active',
  };
  errors.value = {};
};

watch(
  () => props.show,
  (show) => {
    if (!show) {
      resetForm();
    }
  }
);
</script>

<template>
  <Modal
    :show="show"
    title="Thêm người dùng mới"
    size="md"
    @update:show="emit('update:show', $event)"
    @close="emit('close')"
  >
    <div class="space-y-4">
      <Input
        v-model="formData.email"
        label="Email *"
        type="email"
        placeholder="user@example.com"
        :error="errors.email"
      />
      
      <Input
        v-model="formData.password"
        label="Mật khẩu *"
        type="password"
        placeholder="Nhập mật khẩu"
        :error="errors.password"
      />
      <p class="text-white/40 text-xs">
        Mật khẩu phải có ít nhất 8 ký tự, bao gồm chữ hoa, chữ thường và số
      </p>
      
      <Input
        v-model="formData.display_name"
        label="Tên hiển thị *"
        placeholder="Tên người dùng"
        :error="errors.display_name"
      />
      
      <Select
        v-model="formData.status"
        :options="statusOptions"
        label="Trạng thái"
      />
      
      <div class="flex items-center justify-end gap-3 pt-4 border-t border-white/10">
        <Button variant="outline" @click="emit('close')">Hủy</Button>
        <Button variant="primary" :loading="loading" @click="handleSubmit">
          Tạo người dùng
        </Button>
      </div>
    </div>
  </Modal>
</template>

