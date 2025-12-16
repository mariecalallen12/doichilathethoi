<template>
  <div class="glass-panel rounded-lg p-6">
    <h3 class="text-lg font-bold text-white mb-4 flex items-center">
      <i class="fas fa-shield-alt mr-2 text-purple-400"></i>
      Trạng Thái Bảo Mật
    </h3>

    <div class="space-y-4">
      <!-- KYC Status -->
      <div class="flex items-center justify-between p-4 bg-slate-800/50 rounded-lg">
        <div class="flex items-center space-x-3">
          <div class="w-10 h-10 bg-purple-500/20 rounded-lg flex items-center justify-center">
            <i class="fas fa-id-card text-purple-300"></i>
          </div>
          <div>
            <div class="text-white font-medium">Xác thực danh tính (KYC)</div>
            <div class="text-purple-300 text-xs">Trạng thái xác thực</div>
          </div>
        </div>
        <div class="flex items-center space-x-2">
          <StatusBadge :status="kycStatus" />
          <button
            v-if="kycStatus !== 'completed'"
            class="px-3 py-1 text-xs bg-purple-500/20 text-purple-300 rounded hover:bg-purple-500/30 transition-colors"
          >
            Xác thực
          </button>
        </div>
      </div>

      <!-- 2FA Status -->
      <div class="flex items-center justify-between p-4 bg-slate-800/50 rounded-lg">
        <div class="flex items-center space-x-3">
          <div class="w-10 h-10 bg-green-500/20 rounded-lg flex items-center justify-center">
            <i class="fas fa-key text-green-300"></i>
          </div>
          <div>
            <div class="text-white font-medium">Xác thực 2 yếu tố (2FA)</div>
            <div class="text-purple-300 text-xs">Bảo mật tài khoản</div>
          </div>
        </div>
        <div class="flex items-center space-x-2">
          <StatusBadge :status="twoFAStatus" />
          <button
            v-if="twoFAStatus !== 'completed'"
            class="px-3 py-1 text-xs bg-green-500/20 text-green-300 rounded hover:bg-green-500/30 transition-colors"
          >
            Bật 2FA
          </button>
        </div>
      </div>

      <p class="mt-2 text-xs text-purple-300">
        Hiện tại hệ thống sử dụng xác thực số điện thoại như một lớp 2FA cho các thao tác nhạy cảm (ví dụ: rút tiền, đổi mật khẩu).
      </p>

      <!-- Security Score -->
      <div class="p-4 bg-gradient-to-r from-purple-500/20 to-indigo-500/20 border border-purple-500/30 rounded-lg">
        <div class="flex items-center justify-between mb-2">
          <div class="text-white font-medium">Điểm bảo mật tổng thể</div>
          <div class="font-orbitron text-2xl font-bold text-white">{{ securityScore }}/100</div>
        </div>
        <div class="w-full bg-slate-800/50 rounded-full h-2">
          <div
            :class="[
              'h-2 rounded-full transition-all duration-500',
              securityScore >= 80 ? 'bg-green-500' : securityScore >= 50 ? 'bg-yellow-500' : 'bg-red-500'
            ]"
            :style="{ width: `${securityScore}%` }"
          ></div>
        </div>
        <div class="text-purple-300 text-xs mt-2">
          {{ getSecurityScoreMessage() }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import StatusBadge from '../shared/StatusBadge.vue';
import { clientApi } from '../../../services/api/client';

const kycStatus = ref('pending'); // 'completed', 'pending', 'rejected'
const twoFAStatus = ref('pending'); // 'completed', 'pending'
const baseSecurityScore = ref(20);

const securityScore = computed(() => {
  let score = baseSecurityScore.value;
  if (kycStatus.value === 'completed' || kycStatus.value === 'verified') score += 40;
  if (twoFAStatus.value === 'completed') score += 40;
  return Math.min(score, 100);
});

const getSecurityScoreMessage = () => {
  if (securityScore.value >= 80) {
    return 'Tài khoản của bạn rất an toàn';
  } else if (securityScore.value >= 50) {
    return 'Nên cải thiện bảo mật thêm';
  } else {
    return 'Cần cải thiện bảo mật ngay';
  }
};

onMounted(async () => {
  try {
    const dashboard = await clientApi.getDashboard();
    const data = dashboard.data || dashboard;

    if (data.complianceStatus) {
      // Map complianceStatus backend → kycStatus UI
      const status = String(data.complianceStatus).toLowerCase();
      if (status === 'verified' || status === 'completed' || status === 'approved') {
        kycStatus.value = 'completed';
      } else if (status === 'rejected') {
        kycStatus.value = 'rejected';
      } else {
        kycStatus.value = 'pending';
      }
    }

    if (typeof data.riskScore === 'number') {
      // Dùng riskScore backend như base score
      baseSecurityScore.value = Math.max(0, Math.min(data.riskScore, 100));
    }

    // Map twoFactorEnabled backend → twoFAStatus UI
    if (typeof data.twoFactorEnabled === 'boolean') {
      twoFAStatus.value = data.twoFactorEnabled ? 'completed' : 'pending';
    }
  } catch (e) {
    console.error('Failed to fetch security data from dashboard:', e);
  }
});
</script>
