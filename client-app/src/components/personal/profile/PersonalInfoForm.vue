<template>
  <div class="glass-panel rounded-lg p-6">
    <h3 class="text-lg font-bold text-white mb-6 flex items-center">
      <i class="fas fa-user mr-2 text-purple-400"></i>
      Thông Tin Hồ Sơ Cá Nhân
    </h3>

    <form @submit.prevent="handleSubmit" class="space-y-6">
      <!-- Profile Picture -->
      <div class="flex items-center space-x-6">
        <div class="w-24 h-24 rounded-full bg-gradient-to-r from-purple-400 to-indigo-400 flex items-center justify-center overflow-hidden">
          <img v-if="profilePicture" :src="profilePicture" alt="Profile" class="w-full h-full object-cover" />
          <i v-else class="fas fa-user text-white text-3xl"></i>
        </div>
        <div>
          <label class="block">
            <input
              type="file"
              accept="image/*"
              @change="handleFileChange"
              class="hidden"
            />
            <span class="px-4 py-2 bg-purple-500/20 border border-purple-500/30 rounded-lg text-purple-300 hover:bg-purple-500/30 cursor-pointer transition-all">
              <i class="fas fa-upload mr-2"></i>Upload ảnh đại diện
            </span>
          </label>
          <div class="text-purple-300 text-xs mt-2">JPG, PNG tối đa 2MB</div>
        </div>
      </div>

      <!-- Full Name -->
      <div>
        <label class="text-purple-300 text-sm mb-2 block">Họ và tên</label>
        <input
          v-model="formData.fullName"
          type="text"
          required
          class="w-full px-4 py-3 bg-slate-800/50 border border-purple-500/30 rounded-lg text-white placeholder-purple-300/50 focus:border-purple-500/50 focus:outline-none"
        />
      </div>

      <!-- Phone -->
      <div>
        <label class="text-purple-300 text-sm mb-2 block">Số điện thoại</label>
        <input
          v-model="formData.phone"
          type="tel"
          placeholder="+84 xxx xxx xxx"
          required
          class="w-full px-4 py-3 bg-slate-800/50 border border-purple-500/30 rounded-lg text-white placeholder-purple-300/50 focus:border-purple-500/50 focus:outline-none"
        />
      </div>

      <!-- Email -->
      <div>
        <label class="text-purple-300 text-sm mb-2 block">Email</label>
        <div class="flex items-center space-x-2">
          <input
            v-model="formData.email"
            type="email"
            required
            class="flex-1 px-4 py-3 bg-slate-800/50 border border-purple-500/30 rounded-lg text-white placeholder-purple-300/50 focus:border-purple-500/50 focus:outline-none"
          />
          <StatusBadge :status="emailVerified ? 'completed' : 'pending'" />
        </div>
      </div>

      <!-- Date of Birth -->
      <div>
        <label class="text-purple-300 text-sm mb-2 block">Ngày sinh</label>
        <input
          v-model="formData.dateOfBirth"
          type="date"
          required
          class="w-full px-4 py-3 bg-slate-800/50 border border-purple-500/30 rounded-lg text-white focus:border-purple-500/50 focus:outline-none"
        />
      </div>

      <!-- Nationality -->
      <div>
        <label class="text-purple-300 text-sm mb-2 block">Quốc tịch</label>
        <select
          v-model="formData.nationality"
          class="w-full px-4 py-3 bg-slate-800/50 border border-purple-500/30 rounded-lg text-white focus:border-purple-500/50 focus:outline-none"
        >
          <option value="VN">Việt Nam</option>
          <option value="US">United States</option>
          <option value="GB">United Kingdom</option>
          <option value="CN">China</option>
        </select>
      </div>

      <!-- Address -->
      <div>
        <label class="text-purple-300 text-sm mb-2 block">Địa chỉ</label>
        <textarea
          v-model="formData.address"
          rows="3"
          placeholder="Số nhà, đường, phường/xã, quận/huyện, tỉnh/thành phố"
          class="w-full px-4 py-3 bg-slate-800/50 border border-purple-500/30 rounded-lg text-white placeholder-purple-300/50 focus:border-purple-500/50 focus:outline-none"
        ></textarea>
      </div>

      <!-- Submit Button -->
      <div class="flex space-x-4">
        <button
          type="submit"
          :disabled="isLoading"
          class="flex-1 px-6 py-3 bg-gradient-to-r from-purple-500 to-indigo-500 text-white rounded-lg font-medium hover:from-purple-600 hover:to-indigo-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <span v-if="isLoading">
            <i class="fas fa-spinner fa-spin mr-2"></i>Đang lưu...
          </span>
          <span v-else>Lưu Thay Đổi</span>
        </button>
        <button
          type="button"
          @click="resetForm"
          class="px-6 py-3 bg-slate-700 text-white rounded-lg hover:bg-slate-600 transition-all"
        >
          Đặt lại
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useProfileStore } from '../../../stores/profile';
import StatusBadge from '../shared/StatusBadge.vue';

const profileStore = useProfileStore();
const formData = ref({
  fullName: '',
  phone: '',
  email: '',
  dateOfBirth: '',
  nationality: 'VN',
  address: '',
});
const profilePicture = ref(null);
const emailVerified = ref(true);
const isLoading = ref(false);

const handleFileChange = (event) => {
  const file = event.target.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = (e) => {
      profilePicture.value = e.target.result;
    };
    reader.readAsDataURL(file);
  }
};

const handleSubmit = async () => {
  isLoading.value = true;
  try {
    await profileStore.updateProfile(formData.value);
    // Show success message
  } catch (error) {
    console.error('Failed to update profile:', error);
  } finally {
    isLoading.value = false;
  }
};

const resetForm = () => {
  formData.value = { ...profileStore.profile };
};

onMounted(async () => {
  await profileStore.fetchProfile();
  formData.value = { ...profileStore.profile };
});
</script>

