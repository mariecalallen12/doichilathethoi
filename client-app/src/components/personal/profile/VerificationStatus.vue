<template>
  <div class="glass-panel rounded-lg p-6">
    <h3 class="text-lg font-bold text-white mb-6 flex items-center">
      <i class="fas fa-shield-check mr-2 text-purple-400"></i>
      Trạng Thái Xác Thực
    </h3>

    <div class="space-y-4">
      <!-- Email Verification -->
      <div class="flex items-center justify-between p-4 bg-slate-800/50 rounded-lg">
        <div class="flex items-center space-x-3">
          <div class="w-10 h-10 bg-purple-500/20 rounded-lg flex items-center justify-center">
            <i class="fas fa-envelope text-purple-300"></i>
          </div>
          <div>
            <div class="text-white font-medium">Xác thực Email</div>
            <div class="text-purple-300 text-xs">{{ profileStore.profile.email }}</div>
          </div>
        </div>
        <div class="flex items-center space-x-2">
          <StatusBadge :status="emailVerified ? 'completed' : 'pending'" />
          <button
            v-if="!emailVerified"
            class="px-3 py-1 text-xs bg-purple-500/20 text-purple-300 rounded hover:bg-purple-500/30 transition-colors"
          >
            Gửi lại
          </button>
        </div>
      </div>

      <!-- Phone Verification -->
      <div class="flex items-center justify-between p-4 bg-slate-800/50 rounded-lg">
        <div class="flex items-center space-x-3">
          <div class="w-10 h-10 bg-green-500/20 rounded-lg flex items-center justify-center">
            <i class="fas fa-phone text-green-300"></i>
          </div>
          <div>
            <div class="text-white font-medium">Xác thực Số điện thoại</div>
            <div class="text-purple-300 text-xs">{{ profileStore.profile.phone }}</div>
          </div>
        </div>
        <div class="flex items-center space-x-2">
          <StatusBadge :status="phoneVerified ? 'completed' : 'pending'" />
          <button
            v-if="!phoneVerified"
            class="px-3 py-1 text-xs bg-green-500/20 text-green-300 rounded hover:bg-green-500/30 transition-colors"
          >
            Gửi OTP
          </button>
        </div>
      </div>

      <!-- Identity Verification -->
      <div class="flex items-center justify-between p-4 bg-slate-800/50 rounded-lg">
        <div class="flex items-center space-x-3">
          <div class="w-10 h-10 bg-blue-500/20 rounded-lg flex items-center justify-center">
            <i class="fas fa-id-card text-blue-300"></i>
          </div>
          <div>
            <div class="text-white font-medium">Xác thực Danh tính</div>
            <div class="text-purple-300 text-xs">Đã tải lên 2/3 tài liệu</div>
          </div>
        </div>
        <div class="flex items-center space-x-2">
          <StatusBadge :status="identityStatus" />
          <button
            v-if="identityStatus !== 'completed'"
            class="px-3 py-1 text-xs bg-blue-500/20 text-blue-300 rounded hover:bg-blue-500/30 transition-colors"
          >
            {{ identityStatus === 'rejected' ? 'Gửi lại' : 'Hoàn tất' }}
          </button>
        </div>
      </div>

      <!-- Bank Account Verification -->
      <div class="flex items-center justify-between p-4 bg-slate-800/50 rounded-lg">
        <div class="flex items-center space-x-3">
          <div class="w-10 h-10 bg-yellow-500/20 rounded-lg flex items-center justify-center">
            <i class="fas fa-university text-yellow-300"></i>
          </div>
          <div>
            <div class="text-white font-medium">Xác thực Tài khoản Ngân hàng</div>
            <div class="text-purple-300 text-xs">Đã liên kết 1/3 tài khoản</div>
          </div>
        </div>
        <div class="flex items-center space-x-2">
          <StatusBadge :status="bankVerified ? 'completed' : 'pending'" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useProfileStore } from '../../../stores/profile';
import StatusBadge from '../shared/StatusBadge.vue';

const profileStore = useProfileStore();

const emailVerified = ref(false);
const phoneVerified = ref(false);
const identityStatus = ref('pending'); // 'completed', 'pending', 'rejected'
const bankVerified = ref(false);

if (profileStore.profile) {
  emailVerified.value = !!profileStore.profile.emailVerified;
  phoneVerified.value = !!profileStore.profile.phoneVerified;
}
</script>
