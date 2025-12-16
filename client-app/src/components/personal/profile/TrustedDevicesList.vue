<template>
  <div class="glass-panel rounded-lg p-6">
    <div class="flex items-center justify-between mb-6">
      <div>
        <h3 class="text-lg font-bold text-white flex items-center">
          <i class="fas fa-desktop mr-2 text-purple-400"></i>
          Thiết Bị Đáng Tin Cậy
        </h3>
        <p class="text-purple-300 text-xs mt-1">
          Quản lý các thiết bị đã đăng nhập vào tài khoản của bạn
        </p>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="text-center py-8">
      <div class="text-purple-300">Đang tải...</div>
    </div>

    <!-- Devices List -->
    <div v-else-if="devices.length > 0" class="space-y-3">
      <div
        v-for="device in devices"
        :key="device.id"
        class="bg-slate-800/50 rounded-lg p-4 border border-purple-500/20 hover:border-purple-500/40 transition-all"
      >
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-4 flex-1">
            <!-- Device Icon -->
            <div class="w-12 h-12 bg-purple-500/20 rounded-lg flex items-center justify-center">
              <i :class="getDeviceIcon(device.deviceType)" class="text-2xl text-purple-400"></i>
            </div>

            <!-- Device Info -->
            <div class="flex-1">
              <div class="flex items-center space-x-2 mb-1">
                <span class="text-white font-medium">{{ device.deviceName || getDeviceName(device) }}</span>
                <span
                  v-if="device.isCurrent"
                  class="px-2 py-0.5 bg-green-500/20 text-green-400 text-xs rounded"
                >
                  Thiết bị hiện tại
                </span>
                <span
                  v-if="device.isTrusted"
                  class="px-2 py-0.5 bg-blue-500/20 text-blue-400 text-xs rounded"
                >
                  Đáng tin cậy
                </span>
              </div>
              <div class="text-purple-300 text-xs space-y-1">
                <div>{{ device.browser }} trên {{ device.os }}</div>
                <div>{{ device.ipAddress }}</div>
                <div>{{ device.location || 'Không xác định' }}</div>
                <div class="text-purple-400/60">
                  Hoạt động lần cuối: {{ formatDate(device.lastActive) }}
                </div>
              </div>
            </div>
          </div>

          <!-- Actions -->
          <div class="flex items-center space-x-2">
            <button
              v-if="!device.isCurrent && !device.isTrusted"
              @click="trustDevice(device.id)"
              class="px-3 py-1.5 bg-blue-500/20 text-blue-300 rounded text-xs hover:bg-blue-500/30 transition-all"
              title="Đánh dấu là thiết bị đáng tin cậy"
            >
              <i class="fas fa-shield-alt mr-1"></i>Tin cậy
            </button>
            <button
              v-if="!device.isCurrent"
              @click="revokeDevice(device.id)"
              class="px-3 py-1.5 bg-red-500/20 text-red-300 rounded text-xs hover:bg-red-500/30 transition-all"
              title="Thu hồi quyền truy cập"
            >
              <i class="fas fa-ban mr-1"></i>Thu hồi
            </button>
            <button
              v-if="device.isTrusted && !device.isCurrent"
              @click="untrustDevice(device.id)"
              class="px-3 py-1.5 bg-yellow-500/20 text-yellow-300 rounded text-xs hover:bg-yellow-500/30 transition-all"
              title="Bỏ đánh dấu đáng tin cậy"
            >
              <i class="fas fa-times-circle mr-1"></i>Bỏ tin cậy
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="text-center py-8">
      <div class="text-purple-300 text-sm">Chưa có thiết bị nào được lưu</div>
    </div>

    <!-- Add Device Nickname Modal -->
    <div
      v-if="showNicknameModal"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
      @click.self="showNicknameModal = false"
    >
      <div class="glass-panel rounded-lg p-6 max-w-md w-full mx-4">
        <h4 class="text-lg font-bold text-white mb-4">Đặt tên cho thiết bị</h4>
        <input
          v-model="deviceNickname"
          type="text"
          placeholder="Ví dụ: Laptop cá nhân, Điện thoại..."
          class="w-full px-4 py-3 bg-slate-800/50 border border-purple-500/30 rounded-lg text-white placeholder-purple-300/50 focus:border-purple-500/50 focus:outline-none mb-4"
        />
        <div class="flex space-x-3">
          <button
            @click="showNicknameModal = false"
            class="flex-1 px-4 py-2 bg-slate-800/50 border border-purple-500/30 text-purple-300 rounded-lg font-medium hover:bg-purple-500/20 transition-all"
          >
            Hủy
          </button>
          <button
            @click="saveNickname"
            class="flex-1 px-4 py-2 bg-gradient-to-r from-purple-500 to-indigo-500 text-white rounded-lg font-medium hover:from-purple-600 hover:to-indigo-600 transition-all"
          >
            Lưu
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useProfileStore } from '../../../stores/profile';

const profileStore = useProfileStore();
const devices = ref([]);
const isLoading = ref(false);
const showNicknameModal = ref(false);
const selectedDeviceId = ref(null);
const deviceNickname = ref('');

onMounted(async () => {
  await fetchDevices();
});

async function fetchDevices() {
  isLoading.value = true;
  try {
    const response = await fetch('/api/client/trusted-devices', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
      },
    });
    
    const data = await response.json();
    devices.value = data.devices || data || [];
  } catch (error) {
    console.error('Failed to fetch trusted devices:', error);
    // No mock data - show empty list if API fails
    devices.value = [];
  } finally {
    isLoading.value = false;
  }
}

function getDeviceIcon(deviceType) {
  const icons = {
    desktop: 'fas fa-desktop',
    mobile: 'fas fa-mobile-alt',
    tablet: 'fas fa-tablet-alt',
  };
  return icons[deviceType] || 'fas fa-laptop';
}

function getDeviceName(device) {
  return `${device.browser} trên ${device.os}`;
}

function formatDate(date) {
  if (!date) return 'Không xác định';
  const d = new Date(date);
  const now = new Date();
  const diff = now - d;
  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(diff / 3600000);
  const days = Math.floor(diff / 86400000);

  if (minutes < 1) return 'Vừa xong';
  if (minutes < 60) return `${minutes} phút trước`;
  if (hours < 24) return `${hours} giờ trước`;
  if (days < 7) return `${days} ngày trước`;
  return d.toLocaleDateString('vi-VN');
}

async function trustDevice(deviceId) {
  try {
    const response = await fetch(`/api/client/trusted-devices/${deviceId}/trust`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
      },
    });
    
    if (response.ok) {
      await fetchDevices();
      alert('Đã đánh dấu thiết bị là đáng tin cậy');
    }
  } catch (error) {
    console.error('Failed to trust device:', error);
    alert('Không thể đánh dấu thiết bị. Vui lòng thử lại.');
  }
}

async function untrustDevice(deviceId) {
  try {
    const response = await fetch(`/api/client/trusted-devices/${deviceId}/untrust`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
      },
    });
    
    if (response.ok) {
      await fetchDevices();
      alert('Đã bỏ đánh dấu thiết bị');
    }
  } catch (error) {
    console.error('Failed to untrust device:', error);
    alert('Không thể bỏ đánh dấu thiết bị. Vui lòng thử lại.');
  }
}

async function revokeDevice(deviceId) {
  if (!confirm('Bạn có chắc chắn muốn thu hồi quyền truy cập của thiết bị này?')) {
    return;
  }

  try {
    const response = await fetch(`/api/client/trusted-devices/${deviceId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
      },
    });
    
    if (response.ok) {
      await fetchDevices();
      alert('Đã thu hồi quyền truy cập thiết bị');
    }
  } catch (error) {
    console.error('Failed to revoke device:', error);
    alert('Không thể thu hồi thiết bị. Vui lòng thử lại.');
  }
}

function openNicknameModal(deviceId) {
  selectedDeviceId.value = deviceId;
  const device = devices.value.find(d => d.id === deviceId);
  deviceNickname.value = device?.deviceName || '';
  showNicknameModal.value = true;
}

async function saveNickname() {
  if (!selectedDeviceId.value) return;

  try {
    const response = await fetch(`/api/client/trusted-devices/${selectedDeviceId.value}`, {
      method: 'PATCH',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        deviceName: deviceNickname.value,
      }),
    });
    
    if (response.ok) {
      await fetchDevices();
      showNicknameModal.value = false;
      alert('Đã lưu tên thiết bị');
    }
  } catch (error) {
    console.error('Failed to save nickname:', error);
    alert('Không thể lưu tên thiết bị. Vui lòng thử lại.');
  }
}
</script>
