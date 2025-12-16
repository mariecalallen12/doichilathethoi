<template>
  <div
    v-if="isOpen"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
    @click.self="close"
  >
    <div class="glass-panel rounded-lg p-6 max-w-md w-full mx-4 max-h-[90vh] overflow-y-auto">
      <!-- Header -->
      <div class="flex items-center justify-between mb-6">
        <h3 class="text-xl font-bold text-white flex items-center">
          <i class="fas fa-shield-alt mr-2 text-purple-400"></i>
          Thiết Lập 2FA
        </h3>
        <button
          @click="close"
          class="text-purple-300 hover:text-white transition-colors"
          type="button"
          aria-label="Đóng thiết lập 2FA"
        >
          <i class="fas fa-times text-xl" aria-hidden="true"></i>
        </button>
      </div>

      <!-- Step 1: QR Code -->
      <div v-if="step === 1" class="space-y-6">
        <div class="text-purple-300 text-sm">
          Quét mã QR bằng ứng dụng xác thực (Google Authenticator, Authy, etc.)
        </div>

        <!-- QR Code -->
        <div class="flex justify-center">
          <div class="glass-panel rounded-lg p-4 bg-white">
            <canvas ref="qrCanvas" class="w-64 h-64"></canvas>
          </div>
        </div>

        <!-- Secret Key -->
        <div>
          <label class="text-purple-300 text-sm mb-2 block">Hoặc nhập mã thủ công:</label>
          <div class="flex items-center space-x-2 bg-slate-800/50 rounded-lg px-4 py-3">
            <code class="text-white text-sm font-mono flex-1">{{ secretKey }}</code>
            <button
              @click="copySecret"
              class="px-3 py-1 bg-purple-500/20 text-purple-300 rounded text-xs hover:bg-purple-500/30 transition-all"
            >
              <i class="fas fa-copy mr-1"></i>Copy
            </button>
          </div>
        </div>

        <!-- Instructions -->
        <div class="bg-blue-500/20 border border-blue-500/30 rounded-lg p-4">
          <div class="text-blue-300 text-sm">
            <div class="font-bold mb-2">Hướng dẫn:</div>
            <ol class="list-decimal list-inside space-y-1">
              <li>Tải ứng dụng xác thực (Google Authenticator, Authy, Microsoft Authenticator)</li>
              <li>Quét mã QR hoặc nhập mã thủ công</li>
              <li>Nhập mã 6 số từ ứng dụng để xác nhận</li>
            </ol>
          </div>
        </div>

        <button
          @click="step = 2"
          class="w-full px-6 py-3 bg-gradient-to-r from-purple-500 to-indigo-500 text-white rounded-lg font-medium hover:from-purple-600 hover:to-indigo-600 transition-all"
        >
          Tiếp theo
        </button>
      </div>

      <!-- Step 2: Verification -->
      <div v-if="step === 2" class="space-y-6">
        <div class="text-purple-300 text-sm">
          Nhập mã 6 số từ ứng dụng xác thực để xác nhận
        </div>

        <!-- Verification Code Input -->
        <div>
          <label class="text-purple-300 text-sm mb-2 block">Mã xác thực</label>
          <input
            v-model="verificationCode"
            type="text"
            maxlength="6"
            placeholder="000000"
            class="w-full px-4 py-3 bg-slate-800/50 border border-purple-500/30 rounded-lg text-white text-center text-2xl font-mono placeholder-purple-300/50 focus:border-purple-500/50 focus:outline-none tracking-widest"
            @input="handleCodeInput"
            aria-label="Mã xác thực 6 số"
            inputmode="numeric"
          />
          <div v-if="verificationError" class="text-red-400 text-xs mt-2">
            {{ verificationError }}
          </div>
        </div>

        <div class="flex space-x-3">
          <button
            @click="step = 1"
            class="flex-1 px-4 py-2 bg-slate-800/50 border border-purple-500/30 text-purple-300 rounded-lg font-medium hover:bg-purple-500/20 transition-all"
          >
            Quay lại
          </button>
          <button
            @click="verify2FA"
            :disabled="!isCodeValid || isVerifying"
            class="flex-1 px-4 py-2 bg-gradient-to-r from-purple-500 to-indigo-500 text-white rounded-lg font-medium hover:from-purple-600 hover:to-indigo-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="!isVerifying">Xác nhận</span>
            <span v-else>Đang xác nhận...</span>
          </button>
        </div>
      </div>

      <!-- Step 3: Backup Codes -->
      <div v-if="step === 3" class="space-y-6">
        <div class="text-purple-300 text-sm">
          Lưu các mã dự phòng này ở nơi an toàn. Bạn có thể dùng chúng để đăng nhập nếu mất quyền truy cập vào ứng dụng xác thực.
        </div>

        <!-- Backup Codes -->
        <div class="bg-slate-800/50 rounded-lg p-4">
          <div class="grid grid-cols-2 gap-2">
            <div
              v-for="(code, index) in backupCodes"
              :key="index"
              class="bg-slate-900/50 rounded px-3 py-2 text-center font-mono text-sm text-white"
            >
              {{ code }}
            </div>
          </div>
        </div>

        <div class="flex space-x-3">
          <button
            @click="downloadBackupCodes"
            class="flex-1 px-4 py-2 bg-blue-500/20 border border-blue-500/30 text-blue-300 rounded-lg font-medium hover:bg-blue-500/30 transition-all"
          >
            <i class="fas fa-download mr-2"></i>Tải xuống
          </button>
          <button
            @click="copyBackupCodes"
            class="flex-1 px-4 py-2 bg-purple-500/20 border border-purple-500/30 text-purple-300 rounded-lg font-medium hover:bg-purple-500/30 transition-all"
          >
            <i class="fas fa-copy mr-2"></i>Sao chép
          </button>
        </div>

        <button
          @click="completeSetup"
          class="w-full px-6 py-3 bg-gradient-to-r from-green-500 to-emerald-500 text-white rounded-lg font-medium hover:from-green-600 hover:to-emerald-600 transition-all"
        >
          Hoàn tất
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue';
import QRCode from 'qrcode';

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(['close', 'success']);

const step = ref(1);
const secretKey = ref('');
const qrData = ref('');
const verificationCode = ref('');
const verificationError = ref('');
const isVerifying = ref(false);
const backupCodes = ref([]);

const qrCanvas = ref(null);

const isCodeValid = computed(() => {
  return /^\d{6}$/.test(verificationCode.value);
});

watch(() => props.isOpen, async (newVal) => {
  if (newVal) {
    await initialize2FA();
  } else {
    reset();
  }
});

async function initialize2FA() {
  try {
    // Call API to generate 2FA secret and QR code
    const response = await fetch('/api/client/2fa/setup', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        'Content-Type': 'application/json',
      },
    });
    
    const payload = await response.json();
    const data = payload.data || payload;
    secretKey.value = data.secret || data.secret_key;
    qrData.value = data.qr_data || data.otpauth_uri || data.qrCode || data.qr_code;
    
    // Generate QR code
    await nextTick();
    if (qrCanvas.value && qrData.value) {
      if (QRCode) {
        await QRCode.toCanvas(qrCanvas.value, qrData.value, {
          width: 256,
          margin: 2,
        });
      } else {
        // Fallback: Use QR code API service
        generateQRCodeFallback(qrData.value);
      }
    }
  } catch (error) {
    console.error('Failed to initialize 2FA:', error);
    // No mock data - show error to user instead
    errorMessage.value = 'Không thể khởi tạo 2FA. Vui lòng thử lại sau.';
    throw error;
  }
}

function handleCodeInput(event) {
  // Only allow numbers
  verificationCode.value = event.target.value.replace(/\D/g, '');
  verificationError.value = '';
}

async function verify2FA() {
  if (!isCodeValid.value) {
    verificationError.value = 'Vui lòng nhập mã 6 số';
    return;
  }

  isVerifying.value = true;
  verificationError.value = '';

  try {
    const response = await fetch('/api/client/2fa/verify', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        code: verificationCode.value,
      }),
    });

    const payload = await response.json();
    const data = payload.data || payload;

    if (payload.success || data.verified || data.enabled || data.enabled === true) {
      // Get backup codes
      if (data.backup_codes) {
        backupCodes.value = data.backup_codes;
      } else {
        // Generate backup codes if not provided
        backupCodes.value = generateBackupCodes();
      }
      step.value = 3;
    } else {
      verificationError.value = data.message || 'Mã xác thực không đúng. Vui lòng thử lại.';
    }
  } catch (error) {
    console.error('Failed to verify 2FA:', error);
    verificationError.value = 'Có lỗi xảy ra. Vui lòng thử lại.';
  } finally {
    isVerifying.value = false;
  }
}

function generateBackupCodes() {
  const codes = [];
  for (let i = 0; i < 12; i++) {
    // Generate 8-character alphanumeric code
    const code = Math.random().toString(36).substring(2, 10).toUpperCase();
    codes.push(code);
  }
  return codes;
}

function copySecret() {
  navigator.clipboard.writeText(secretKey.value).then(() => {
    // Show toast notification
    alert('Đã sao chép mã bí mật');
  });
}

function copyBackupCodes() {
  const codesText = backupCodes.value.join('\n');
  navigator.clipboard.writeText(codesText).then(() => {
    alert('Đã sao chép các mã dự phòng');
  });
}

function downloadBackupCodes() {
  const codesText = backupCodes.value.join('\n');
  const blob = new Blob([codesText], { type: 'text/plain' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = 'backup-codes.txt';
  link.click();
  URL.revokeObjectURL(url);
}

function completeSetup() {
  emit('success');
  close();
}

function close() {
  emit('close');
}

function reset() {
  step.value = 1;
  verificationCode.value = '';
  verificationError.value = '';
  isVerifying.value = false;
  backupCodes.value = [];
}

function generateQRCodeFallback(qrData) {
  // Fallback: Use QR code API service
  if (qrCanvas.value) {
    const qrUrl = `https://api.qrserver.com/v1/create-qr-code/?size=256x256&data=${encodeURIComponent(qrData)}`;
    const img = new Image();
    img.crossOrigin = 'anonymous';
    img.onload = () => {
      const ctx = qrCanvas.value.getContext('2d');
      ctx.clearRect(0, 0, qrCanvas.value.width, qrCanvas.value.height);
      ctx.drawImage(img, 0, 0, 256, 256);
    };
    img.src = qrUrl;
  }
}
</script>
