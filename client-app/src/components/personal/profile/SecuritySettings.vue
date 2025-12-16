<template>
  <div class="glass-panel rounded-lg p-6">
    <h3 class="text-lg font-bold text-white mb-6 flex items-center">
      <i class="fas fa-lock mr-2 text-purple-400"></i>
      Cài Đặt Bảo Mật
    </h3>

    <!-- 2FA Section -->
    <div class="mb-6 pb-6 border-b border-purple-500/20">
      <div class="flex items-center justify-between mb-4">
        <div>
          <div class="text-white font-medium mb-1">Xác thực 2 yếu tố (2FA)</div>
          <div class="text-purple-300 text-xs">Bảo mật tài khoản với ứng dụng xác thực</div>
        </div>
        <StatusBadge :status="twoFAEnabled ? 'completed' : 'pending'" />
      </div>
      <button
        v-if="!twoFAEnabled"
        @click="setup2FA"
        class="px-4 py-2 bg-gradient-to-r from-green-500 to-emerald-500 text-white rounded-lg text-sm font-medium hover:from-green-600 hover:to-emerald-600 transition-all"
      >
        <i class="fas fa-key mr-2"></i>Bật 2FA
      </button>
      <button
        v-else
        @click="disable2FA"
        class="px-4 py-2 bg-red-500/20 text-red-300 rounded-lg text-sm font-medium hover:bg-red-500/30 transition-all"
      >
        <i class="fas fa-ban mr-2"></i>Tắt 2FA
      </button>
    </div>

    <!-- Password Section -->
    <div>
      <div class="mb-4">
        <div class="text-white font-medium mb-1">Đổi mật khẩu</div>
        <div class="text-purple-300 text-xs">Mật khẩu cuối cùng thay đổi: 30 ngày trước</div>
      </div>
      <button
        @click="showChangePassword = true"
        class="px-4 py-2 bg-purple-500/20 border border-purple-500/30 text-purple-300 rounded-lg text-sm font-medium hover:bg-purple-500/30 transition-all"
      >
        <i class="fas fa-key mr-2"></i>Đổi mật khẩu
      </button>
    </div>

    <!-- 2FA Setup Modal -->
    <TwoFactorSetupModal
      :is-open="show2FASetup"
      @close="show2FASetup = false"
      @success="on2FASuccess"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue';
import StatusBadge from '../shared/StatusBadge.vue';
import TwoFactorSetupModal from './TwoFactorSetupModal.vue';
import TrustedDevicesList from './TrustedDevicesList.vue';
import { useProfileStore } from '../../../stores/profile';

const profileStore = useProfileStore();
const twoFAEnabled = ref(false);
const showChangePassword = ref(false);
const show2FASetup = ref(false);

// Check 2FA status on mount
if (profileStore.profile?.twoFactorEnabled !== undefined) {
  twoFAEnabled.value = profileStore.profile.twoFactorEnabled;
}

const setup2FA = () => {
  // Hiện tại backend chưa hỗ trợ endpoint 2FA riêng,
  // nên chỉ mở modal thông tin nếu cần mở rộng sau này.
  show2FASetup.value = true;
};

  const disable2FA = async () => {
  if (confirm('Bạn có chắc chắn muốn tắt 2FA? Điều này sẽ làm giảm bảo mật tài khoản của bạn.')) {
    try {
      const code = prompt('Nhập mã 2FA hoặc một mã backup để tắt 2FA:') || '';
      if (!code.trim()) return;

      const response = await fetch('/api/client/2fa/disable', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ code: code.trim() }),
      });

      const data = await response.json();
      if (response.ok && (data.success || data.data?.enabled === false)) {
        twoFAEnabled.value = false;
        if (profileStore.profile) {
          profileStore.profile.twoFactorEnabled = false;
        }
        alert('Đã tắt 2FA thành công');
      } else {
        alert(data.detail || data.message || 'Không thể tắt 2FA. Vui lòng thử lại.');
      }
    } catch (error) {
      console.error('Failed to disable 2FA:', error);
      alert('Không thể tắt 2FA. Vui lòng thử lại.');
    }
  }
};

const on2FASuccess = () => {
  twoFAEnabled.value = true;
  if (profileStore.profile) {
    profileStore.profile.twoFactorEnabled = true;
  }
  alert('Đã bật 2FA thành công!');
};
</script>
