<template>
  <div class="bg-gradient-to-br from-slate-800/50 to-slate-900/50 rounded-xl p-6 border border-purple-500/20">
    <h2 class="text-2xl font-bold text-white mb-6">Gửi Khiếu Nại</h2>
    
    <form @submit.prevent="handleSubmit" class="space-y-4">
      <div>
        <label class="block text-sm text-gray-400 mb-2">Loại khiếu nại *</label>
        <select
          v-model="formData.type"
          required
          class="w-full px-4 py-3 bg-slate-700 border border-purple-500/20 rounded-lg text-white focus:outline-none focus:border-purple-400"
        >
          <option value="">Chọn loại khiếu nại</option>
          <option value="account">Tài khoản</option>
          <option value="trading">Giao dịch</option>
          <option value="deposit">Nạp tiền</option>
          <option value="withdraw">Rút tiền</option>
          <option value="technical">Kỹ thuật</option>
          <option value="other">Khác</option>
        </select>
      </div>

      <div>
        <label class="block text-sm text-gray-400 mb-2">Tiêu đề *</label>
        <input
          v-model="formData.title"
          type="text"
          required
          class="w-full px-4 py-3 bg-slate-700 border border-purple-500/20 rounded-lg text-white focus:outline-none focus:border-purple-400"
          placeholder="Nhập tiêu đề khiếu nại"
        />
      </div>

      <div>
        <label class="block text-sm text-gray-400 mb-2">Mô tả chi tiết *</label>
        <textarea
          v-model="formData.description"
          required
          rows="6"
          class="w-full px-4 py-3 bg-slate-700 border border-purple-500/20 rounded-lg text-white focus:outline-none focus:border-purple-400 resize-none"
          placeholder="Mô tả chi tiết về khiếu nại của bạn..."
        ></textarea>
      </div>

      <div>
        <label class="block text-sm text-gray-400 mb-2">Đính kèm tài liệu (nếu có)</label>
        <input
          type="file"
          multiple
          @change="handleFileChange"
          class="w-full px-4 py-3 bg-slate-700 border border-purple-500/20 rounded-lg text-white text-sm"
          accept=".pdf,.jpg,.jpeg,.png,.doc,.docx"
        />
        <div v-if="formData.files.length > 0" class="mt-2 text-sm text-gray-400">
          Đã chọn {{ formData.files.length }} file(s)
        </div>
      </div>

      <button
        type="submit"
        :disabled="isSubmitting"
        class="w-full px-6 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-lg hover:from-purple-700 hover:to-indigo-700 transition-all disabled:opacity-50"
      >
        <i class="fas fa-paper-plane mr-2"></i>
        {{ isSubmitting ? 'Đang gửi...' : 'Gửi Khiếu Nại' }}
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const emit = defineEmits(['submit']);

const isSubmitting = ref(false);
const formData = ref({
  type: '',
  title: '',
  description: '',
  files: []
});

const handleFileChange = (event) => {
  formData.value.files = Array.from(event.target.files);
};

const handleSubmit = async () => {
  isSubmitting.value = true;
  try {
    await emit('submit', formData.value);
    // Reset form
    formData.value = {
      type: '',
      title: '',
      description: '',
      files: []
    };
  } finally {
    isSubmitting.value = false;
  }
};
</script>

<style scoped>
/* Complaint form styles */
</style>

