<template>
  <div class="space-y-6">
    <!-- Asset Selection -->
    <div class="glass-panel rounded-lg p-6">
      <h3 class="text-lg font-bold text-white mb-4">Chọn Loại Tài Sản</h3>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <button
          v-for="asset in assets"
          :key="asset.symbol"
          @click="selectAsset(asset)"
          :class="[
            'p-4 rounded-lg border-2 transition-all',
            selectedAsset?.symbol === asset.symbol
              ? 'border-purple-500 bg-purple-500/20'
              : 'border-purple-500/30 bg-slate-800/50 hover:border-purple-500/50'
          ]"
        >
          <div class="text-white font-bold text-lg mb-2">{{ asset.symbol }}</div>
          <div class="text-purple-300 text-xs mb-1">{{ asset.name }}</div>
          <div class="text-purple-300 text-xs">Min: ${{ asset.minAmount }}</div>
        </button>
      </div>
    </div>

    <!-- Network Selection -->
    <div v-if="selectedAsset" class="glass-panel rounded-lg p-6">
      <h3 class="text-lg font-bold text-white mb-4">Chọn Mạng Lưới</h3>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <button
          v-for="network in selectedAsset.networks"
          :key="network"
          @click="selectNetwork(network)"
          :class="[
            'p-4 rounded-lg border-2 transition-all',
            selectedNetwork === network
              ? 'border-purple-500 bg-purple-500/20'
              : 'border-purple-500/30 bg-slate-800/50 hover:border-purple-500/50'
          ]"
        >
          <div class="text-white font-bold">{{ network }}</div>
        </button>
      </div>
    </div>

    <!-- Address Display -->
    <div v-if="selectedAsset && selectedNetwork" class="glass-panel rounded-lg p-6">
      <h3 class="text-lg font-bold text-white mb-4">Địa Chỉ Ví</h3>
      
      <!-- Warning -->
      <div class="mb-4 p-4 bg-yellow-500/20 border border-yellow-500/30 rounded-lg">
        <div class="flex items-start space-x-3">
          <i class="fas fa-exclamation-triangle text-yellow-400 mt-1"></i>
          <div class="text-yellow-300 text-sm">
            <div class="font-bold mb-1">Cảnh báo về network mismatch</div>
            <div>Vui lòng đảm bảo bạn chọn đúng network khi gửi tiền. Gửi sai network có thể dẫn đến mất tiền.</div>
          </div>
        </div>
      </div>

      <!-- QR Code and Address -->
      <div class="flex flex-col md:flex-row items-center md:items-start space-y-6 md:space-y-0 md:space-x-6">
        <QRCodeDisplay v-if="walletAddress" :address="walletAddress" />
        
        <div class="flex-1 w-full">
          <div class="mb-4">
            <label class="text-purple-300 text-sm mb-2 block">Địa chỉ ví</label>
            <div class="flex items-center space-x-2 bg-slate-800/50 rounded-lg px-4 py-3">
              <code class="text-white text-sm font-mono break-all flex-1">
                <span v-if="walletAddress">{{ walletAddress }}</span>
                <span v-else class="text-purple-300/60 italic">Vui lòng chọn tài sản và mạng lưới để tạo địa chỉ nạp</span>
              </code>
            </div>
            <div v-if="isLoading" class="mt-2 text-purple-300 text-xs">Đang tạo địa chỉ nạp...</div>
            <div v-if="errorMessage" class="mt-2 text-red-400 text-xs">{{ errorMessage }}</div>
          </div>

          <!-- Transaction Info -->
          <div class="space-y-3">
            <div class="flex justify-between items-center p-3 bg-slate-800/50 rounded-lg">
              <span class="text-purple-300 text-sm">Network</span>
              <span class="text-white font-medium">{{ selectedNetwork }}</span>
            </div>
            <div class="flex justify-between items-center p-3 bg-slate-800/50 rounded-lg">
              <span class="text-purple-300 text-sm">Phí giao dịch</span>
              <span class="text-white font-medium">Network dependent</span>
            </div>
            <div class="flex justify-between items-center p-3 bg-slate-800/50 rounded-lg">
              <span class="text-purple-300 text-sm">Thời gian xử lý</span>
              <span class="text-white font-medium">10-30 phút</span>
            </div>
            <div class="flex justify-between items-center p-3 bg-slate-800/50 rounded-lg">
              <span class="text-purple-300 text-sm">Số tiền tối thiểu</span>
              <span class="text-white font-medium">${{ selectedAsset.minAmount }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';
import QRCodeDisplay from '../shared/QRCodeDisplay.vue';
import { clientApi } from '../../../services/api/client';

const selectedAsset = ref(null);
const selectedNetwork = ref(null);
const walletAddress = ref('');
const isLoading = ref(false);
const errorMessage = ref('');

const assets = [
  {
    symbol: 'USDT',
    name: 'Tether',
    networks: ['ERC20', 'TRC20', 'BEP20'],
    minAmount: 10,
  },
  {
    symbol: 'BTC',
    name: 'Bitcoin',
    networks: ['Bitcoin'],
    minAmount: 20,
  },
  {
    symbol: 'ETH',
    name: 'Ethereum',
    networks: ['Ethereum'],
    minAmount: 15,
  },
];

const resetState = () => {
  walletAddress.value = '';
  errorMessage.value = '';
};

const fetchDepositAddress = async () => {
  if (!selectedAsset.value || !selectedNetwork.value) return;
  isLoading.value = true;
  errorMessage.value = '';
  walletAddress.value = '';

  try {
    const data = await clientApi.createCryptoDepositAddress({
      currency: selectedAsset.value.symbol,
      network: selectedNetwork.value,
    });
    walletAddress.value = data.address || '';
  } catch (error) {
    console.error('Failed to create crypto deposit address:', error);
    errorMessage.value =
      error.message || 'Không thể tạo địa chỉ nạp crypto. Vui lòng thử lại.';
  } finally {
    isLoading.value = false;
  }
};

const selectAsset = (asset) => {
  selectedAsset.value = asset;
  selectedNetwork.value = null;
  resetState();
};

const selectNetwork = (network) => {
  selectedNetwork.value = network;
  resetState();
  fetchDepositAddress();
};

watch(
  () => [selectedAsset.value, selectedNetwork.value],
  () => {
    // Khi thay đổi asset/network, địa chỉ sẽ được refresh bởi fetchDepositAddress
  }
);
</script>
