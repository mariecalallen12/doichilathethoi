<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div>
      <h1 class="text-3xl font-bold text-white mb-2">Nạp Tiền</h1>
      <p class="text-purple-300">Nạp tiền vào tài khoản của bạn</p>
    </div>

    <!-- Tabs -->
    <div class="glass-panel rounded-lg p-1">
      <div class="flex space-x-1">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="[
            'flex-1 px-4 py-3 rounded-lg font-medium transition-all',
            activeTab === tab.id
              ? 'bg-gradient-to-r from-purple-500 to-indigo-500 text-white'
              : 'text-purple-300 hover:text-white hover:bg-purple-500/10'
          ]"
        >
          <i :class="[tab.icon, 'mr-2']"></i>
          {{ tab.label }}
        </button>
      </div>
    </div>

    <!-- Tab Content -->
    <div>
      <CryptoDeposit v-if="activeTab === 'crypto'" />
      <VietQRDeposit v-if="activeTab === 'vietqr'" />
      <OnlinePaymentDeposit v-if="activeTab === 'online'" />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import CryptoDeposit from '../../components/personal/deposit/CryptoDeposit.vue';
import VietQRDeposit from '../../components/personal/deposit/VietQRDeposit.vue';
import OnlinePaymentDeposit from '../../components/personal/deposit/OnlinePaymentDeposit.vue';

const activeTab = ref('crypto');

const tabs = [
  {
    id: 'crypto',
    label: 'Crypto',
    icon: 'fab fa-bitcoin',
  },
  {
    id: 'vietqr',
    label: 'VietQR',
    icon: 'fas fa-qrcode',
  },
  {
    id: 'online',
    label: 'Online Payment',
    icon: 'fas fa-credit-card',
  },
];
</script>

