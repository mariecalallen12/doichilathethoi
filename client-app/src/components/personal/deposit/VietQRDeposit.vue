<template>
  <div class="space-y-6">
    <!-- Form -->
    <div class="glass-panel rounded-lg p-6">
      <h3 class="text-lg font-bold text-white mb-4">Thông Tin Nạp Tiền</h3>
      
      <div class="space-y-4">
        <div>
          <label class="text-purple-300 text-sm mb-2 block">Số tiền (VND)</label>
          <input
            v-model.number="amount"
            type="number"
            min="10000"
            step="1000"
            placeholder="Nhập số tiền muốn nạp"
            class="w-full px-4 py-3 bg-slate-800/50 border border-purple-500/30 rounded-lg text-white placeholder-purple-300/50 focus:border-purple-500/50 focus:outline-none"
          />
          <div class="text-purple-300 text-xs mt-1">Số tiền tối thiểu: 10,000 VND</div>
        </div>

        <div>
          <label class="text-purple-300 text-sm mb-2 block">Ngân hàng</label>
          <select
            v-model="selectedBank"
            class="w-full px-4 py-3 bg-slate-800/50 border border-purple-500/30 rounded-lg text-white focus:border-purple-500/50 focus:outline-none"
          >
            <option value="">Chọn ngân hàng</option>
            <option v-for="bank in banks" :key="bank.code" :value="bank.code">
              {{ bank.name }}
            </option>
          </select>
        </div>

        <button
          @click="generateQR"
          :disabled="!amount || !selectedBank || amount < 10000 || isLoading"
          class="w-full px-6 py-3 bg-gradient-to-r from-purple-500 to-indigo-500 text-white rounded-lg font-medium hover:from-purple-600 hover:to-indigo-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <span v-if="!isLoading">Tạo Mã QR</span>
          <span v-else>Đang tạo mã QR...</span>
        </button>

        <div v-if="errorMessage" class="text-red-400 text-xs">
          {{ errorMessage }}
        </div>
      </div>
    </div>

    <!-- QR Code Display -->
    <div v-if="qrData" class="glass-panel rounded-lg p-6">
      <h3 class="text-lg font-bold text-white mb-4">Mã QR Chuyển Khoản</h3>
      
      <div class="flex flex-col md:flex-row items-center md:items-start space-y-6 md:space-y-0 md:space-x-6">
        <div class="glass-panel rounded-lg p-6">
          <canvas ref="qrCanvas" class="w-64 h-64"></canvas>
        </div>

        <div class="flex-1 w-full space-y-4">
          <div>
            <div class="text-purple-300 text-sm mb-2">Thông tin chuyển khoản</div>
            <div class="space-y-2">
              <div class="flex justify-between p-3 bg-slate-800/50 rounded-lg">
                <span class="text-purple-300 text-sm">Tên người nhận</span>
                <span class="text-white font-medium">{{ qrData.accountName || 'CMEETRADING' }}</span>
              </div>
              <div class="flex justify-between p-3 bg-slate-800/50 rounded-lg">
                <span class="text-purple-300 text-sm">Số tài khoản</span>
                <span class="text-white font-medium">{{ qrData.accountNumber }}</span>
              </div>
              <div class="flex justify-between p-3 bg-slate-800/50 rounded-lg">
                <span class="text-purple-300 text-sm">Chi nhánh</span>
                <span class="text-white font-medium">{{ qrData.branch }}</span>
              </div>
              <div class="flex justify-between p-3 bg-slate-800/50 rounded-lg">
                <span class="text-purple-300 text-sm">Nội dung</span>
                <span class="text-white font-medium font-mono">{{ qrData.content }}</span>
              </div>
              <div class="flex justify-between p-3 bg-slate-800/50 rounded-lg">
                <span class="text-purple-300 text-sm">Số tiền</span>
                <span class="text-white font-medium font-orbitron">{{ formatVND(amount) }}</span>
              </div>
            </div>
          </div>

          <div class="p-4 bg-blue-500/20 border border-blue-500/30 rounded-lg">
            <div class="text-blue-300 text-sm">
              <i class="fas fa-info-circle mr-2"></i>
              QR code có hiệu lực trong 24 giờ. Vui lòng chuyển khoản trong thời gian này.
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Transaction Tracking -->
    <div v-if="qrData" class="glass-panel rounded-lg p-6">
      <h3 class="text-lg font-bold text-white mb-4">Theo Dõi Giao Dịch</h3>
      <div class="flex items-center justify-between p-4 bg-slate-800/50 rounded-lg">
        <div class="flex items-center space-x-3">
          <div class="w-12 h-12 bg-yellow-500/20 rounded-lg flex items-center justify-center">
            <i class="fas fa-clock text-yellow-400 text-xl"></i>
          </div>
          <div>
            <div class="text-white font-medium">Đang chờ chuyển tiền</div>
            <div class="text-purple-300 text-xs">Hệ thống sẽ tự động xác minh khi nhận được tiền</div>
          </div>
        </div>
        <StatusBadge status="pending" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';
import StatusBadge from '../shared/StatusBadge.vue';
import { formatNumber } from '../../../services/utils/formatters';
import { clientApi } from '../../../services/api/client';

const amount = ref(null);
const selectedBank = ref('');
const qrData = ref(null);
const qrCanvas = ref(null);
const isLoading = ref(false);
const errorMessage = ref('');

const banks = [
  { code: 'VCB', name: 'Vietcombank' },
  { code: 'TCB', name: 'Techcombank' },
  { code: 'BIDV', name: 'BIDV' },
  { code: 'AGB', name: 'Agribank' },
  { code: 'ACB', name: 'ACB' },
  { code: 'VPB', name: 'VPBank' },
];

const generateQR = async () => {
  if (!amount.value || !selectedBank.value || amount.value < 10000) return;
  isLoading.value = true;
  errorMessage.value = '';
  qrData.value = null;

  try {
    const data = await clientApi.generateVietQR({
      amount: amount.value,
      description: `Nạp tiền VietQR - ${selectedBank.value}`,
      orderId: null,
    });

    qrData.value = {
      accountNumber: data.accountNumber,
      accountName: data.accountName || 'CMEETRADING',
      branch: 'Chi nhánh Hồ Chí Minh',
      content: data.description || data.paymentId,
      paymentId: data.paymentId,
      bankCode: data.bankCode,
      paymentUrl: data.paymentUrl,
      qrCode: data.qrCode,
    };

    // Generate QR code (simplified - in production use proper QR library)
    generateQRCode();
  } catch (error) {
    console.error('Failed to generate VietQR:', error);
    errorMessage.value =
      error.message || 'Không thể tạo VietQR. Vui lòng thử lại.';
  } finally {
    isLoading.value = false;
  }
};

const generateQRCode = () => {
  if (!qrCanvas.value || !qrData.value) return;
  
  const canvas = qrCanvas.value;
  const ctx = canvas.getContext('2d');
  
  canvas.width = 256;
  canvas.height = 256;
  
  // Clear canvas
  ctx.fillStyle = '#ffffff';
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  
  // Draw QR pattern (simplified)
  ctx.fillStyle = '#000000';
  const cellSize = canvas.width / 25;
  
  for (let i = 0; i < 25; i++) {
    for (let j = 0; j < 25; j++) {
      if ((i + j) % 3 === 0 || (i * j) % 7 === 0) {
        ctx.fillRect(i * cellSize, j * cellSize, cellSize, cellSize);
      }
    }
  }
};

const formatVND = (amount) => {
  return `${formatNumber(amount)} ₫`;
};

watch([amount, selectedBank], () => {
  if (qrData.value && (amount.value !== qrData.value.amount || selectedBank.value !== qrData.value.bank)) {
    qrData.value = null;
  }
});
</script>
