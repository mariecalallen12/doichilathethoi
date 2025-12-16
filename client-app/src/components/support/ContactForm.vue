<template>
  <div class="bg-gradient-to-br from-slate-800/50 to-slate-900/50 rounded-xl p-6 border border-purple-500/20">
    <h2 class="text-2xl font-bold text-white mb-6">Gửi Tin Nhắn</h2>
    
    <form @submit.prevent="handleSubmit" class="space-y-4">
      <div>
        <label class="block text-sm text-gray-400 mb-2">Họ và tên *</label>
        <input
          v-model="formData.name"
          type="text"
          required
          class="w-full px-4 py-3 bg-slate-700 border border-purple-500/20 rounded-lg text-white focus:outline-none focus:border-purple-400"
          placeholder="Nhập họ và tên"
        />
      </div>

      <div>
        <label class="block text-sm text-gray-400 mb-2">Email *</label>
        <input
          v-model="formData.email"
          type="email"
          required
          class="w-full px-4 py-3 bg-slate-700 border border-purple-500/20 rounded-lg text-white focus:outline-none focus:border-purple-400"
          placeholder="your@email.com"
        />
      </div>

      <div>
        <label class="block text-sm text-gray-400 mb-2">Số điện thoại</label>
        <input
          v-model="formData.phone"
          type="tel"
          class="w-full px-4 py-3 bg-slate-700 border border-purple-500/20 rounded-lg text-white focus:outline-none focus:border-purple-400"
          placeholder="+84 123 456 789"
        />
      </div>

      <div>
        <label class="block text-sm text-gray-400 mb-2">Chủ đề *</label>
        <select
          v-model="formData.subject"
          required
          class="w-full px-4 py-3 bg-slate-700 border border-purple-500/20 rounded-lg text-white focus:outline-none focus:border-purple-400"
        >
          <option value="">Chọn chủ đề</option>
          <option value="general">Câu hỏi chung</option>
          <option value="account">Tài khoản</option>
          <option value="trading">Giao dịch</option>
          <option value="technical">Hỗ trợ kỹ thuật</option>
          <option value="other">Khác</option>
        </select>
      </div>

      <div>
        <label class="block text-sm text-gray-400 mb-2">Tin nhắn *</label>
        <textarea
          v-model="formData.message"
          required
          rows="6"
          class="w-full px-4 py-3 bg-slate-700 border border-purple-500/20 rounded-lg text-white focus:outline-none focus:border-purple-400 resize-none"
          placeholder="Nhập tin nhắn của bạn..."
        ></textarea>
      </div>

      <button
        type="submit"
        :disabled="isSubmitting"
        class="w-full px-6 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-lg hover:from-purple-700 hover:to-indigo-700 transition-all disabled:opacity-50"
      >
        <i class="fas fa-paper-plane mr-2"></i>
        {{ isSubmitting ? 'Đang gửi...' : 'Gửi Tin Nhắn' }}
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const emit = defineEmits(['submit']);

const isSubmitting = ref(false);
const formData = ref({
  name: '',
  email: '',
  phone: '',
  subject: '',
  message: ''
});

const handleSubmit = async () => {
  isSubmitting.value = true;
  try {
    await emit('submit', formData.value);
    // Reset form
    formData.value = {
      name: '',
      email: '',
      phone: '',
      subject: '',
      message: ''
    };
  } finally {
    isSubmitting.value = false;
  }
};
</script>

<style scoped>
/* Contact form styles */
</style>

