<template>
  <div class="quick-trade-widget w-80 max-w-[calc(100vw-2rem)] p-6">
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-white font-bold text-lg">Giao dịch nhanh</h3>
      <button
        @click="toggleWidget"
        class="text-white/70 hover:text-white transition-colors"
      >
        <i :class="isExpanded ? 'fas fa-chevron-down' : 'fas fa-chevron-up'"></i>
      </button>
    </div>
    
    <div v-if="isExpanded" class="space-y-4">
      <!-- Asset Selector -->
      <div>
        <label class="block text-sm text-gray-300 mb-2">Tài sản</label>
        <select
          v-model="selectedAsset"
          class="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white"
        >
          <option
            v-for="asset in availableAssets"
            :key="asset.symbol"
            :value="asset.symbol"
          >
            {{ asset.symbol }}
          </option>
        </select>
      </div>
      
      <!-- Order Type -->
      <div>
        <label class="block text-sm text-gray-300 mb-2">Loại lệnh</label>
        <div class="grid grid-cols-2 gap-2">
          <button
            @click="orderType = 'buy'"
            class="px-4 py-2 rounded-lg transition-colors"
            :class="orderType === 'buy' ? 'bg-green-500 text-white' : 'bg-white/10 text-gray-300'"
          >
            Mua
          </button>
          <button
            @click="orderType = 'sell'"
            class="px-4 py-2 rounded-lg transition-colors"
            :class="orderType === 'sell' ? 'bg-red-500 text-white' : 'bg-white/10 text-gray-300'"
          >
            Bán
          </button>
        </div>
      </div>
      
      <!-- Amount Input -->
      <div>
        <label class="block text-sm text-gray-300 mb-2">Số lượng</label>
        <input
          v-model.number="amount"
          type="number"
          step="0.01"
          min="0"
          placeholder="0.00"
          class="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-500"
        />
      </div>
      
      <!-- Price Display -->
      <div class="p-3 bg-white/5 rounded-lg">
        <div class="flex justify-between text-sm mb-1">
          <span class="text-gray-400">Giá hiện tại</span>
          <span class="text-white font-semibold">{{ currentPrice }}</span>
        </div>
        <div class="flex justify-between text-sm">
          <span class="text-gray-400">Tổng giá trị</span>
          <span class="text-white font-semibold">{{ totalValue }}</span>
        </div>
        <div class="flex justify-between text-xs text-purple-200 mt-2">
          <span>Số dư ví khả dụng</span>
          <span class="font-semibold text-white">{{ formattedAvailable }}</span>
        </div>
        <button
          type="button"
          @click="useWalletBalance"
          class="mt-2 w-full px-3 py-2 bg-purple-600/60 hover:bg-purple-600 text-white rounded-lg text-xs font-semibold transition-all"
        >
          Dùng số dư ví
        </button>
      </div>
      
      <!-- Submit Button -->
      <button
        @click="submitOrder"
        class="w-full py-3 bg-gradient-to-r from-purple-500 to-indigo-500 hover:from-purple-600 hover:to-indigo-600 rounded-lg text-white font-semibold transition-all duration-300 shadow-lg hover:shadow-xl"
      >
        {{ orderType === 'buy' ? 'Mua' : 'Bán' }} {{ selectedAsset }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useMarketStore } from '../../stores/market';
import { useAccountStore } from '../../stores/account';
import { formatPrice } from '../../utils/marketFormatters';

const marketStore = useMarketStore();
const accountStore = useAccountStore();
const isExpanded = ref(true);
const selectedAsset = ref('BTC/USD');
const orderType = ref('buy');
const amount = ref(0);

const availableAssets = computed(() => marketStore.instruments.slice(0, 10));

const currentPrice = computed(() => {
  const asset = marketStore.instruments.find(a => a.symbol === selectedAsset.value);
  return asset ? formatPrice(asset.price, 2) : '0.00';
});

const totalValue = computed(() => {
  const asset = marketStore.instruments.find(a => a.symbol === selectedAsset.value);
  if (!asset || !amount.value) return '0.00';
  return formatPrice(asset.price * amount.value, 2);
});

const availableBalance = computed(() => accountStore.balance.available || 0);
const formattedAvailable = computed(() =>
  availableBalance.value.toLocaleString('vi-VN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
);

const toggleWidget = () => {
  isExpanded.value = !isExpanded.value;
};

const submitOrder = () => {
  if (!amount.value || amount.value <= 0) {
    alert('Vui lòng nhập số lượng hợp lệ');
    return;
  }
  
  console.log('Submit order:', {
    asset: selectedAsset.value,
    type: orderType.value,
    amount: amount.value,
    price: currentPrice.value,
  });
  
  // Here you would call the trading API
  alert(`Đã đặt lệnh ${orderType.value === 'buy' ? 'mua' : 'bán'} ${amount.value} ${selectedAsset.value}`);
};

const useWalletBalance = () => {
  if (!availableBalance.value || availableBalance.value <= 0) {
    alert('Bạn chưa có số dư khả dụng trong ví');
    return;
  }
  amount.value = Number(availableBalance.value.toFixed(2));
};
</script>

<style scoped>
@media (max-width: 768px) {
  .quick-trade-widget {
    position: fixed;
    bottom: 1rem;
    right: 1rem;
    left: 1rem;
    width: auto;
    max-width: none;
  }
}
</style>

