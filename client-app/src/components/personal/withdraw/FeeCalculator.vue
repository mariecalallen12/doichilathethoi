<template>
  <div v-if="amount > 0" class="glass-panel rounded-lg p-4 bg-slate-800/50">
    <div class="space-y-2">
      <div class="flex justify-between items-center">
        <span class="text-purple-300 text-sm">Số tiền yêu cầu</span>
        <span class="text-white font-medium">{{ formatAmount(amount) }}</span>
      </div>
      <div class="flex justify-between items-center">
        <span class="text-purple-300 text-sm">Phí rút</span>
        <span class="text-yellow-400 font-medium">{{ formatAmount(fee) }}</span>
      </div>
      <div class="pt-2 border-t border-purple-500/20">
        <div class="flex justify-between items-center">
          <span class="text-white font-bold">Số tiền thực nhận</span>
          <span class="text-green-400 font-orbitron font-bold text-lg">{{ formatAmount(netAmount) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { formatCurrency, formatNumber } from '../../../services/utils/formatters';

const props = defineProps({
  amount: {
    type: Number,
    default: 0,
  },
  method: {
    type: String,
    default: 'crypto',
  },
});

const feeRate = computed(() => {
  if (props.method === 'bank') {
    return 0.01; // 1% + 10,000 VND fixed
  }
  return 0.02; // 2% for crypto
});

const fee = computed(() => {
  if (props.amount <= 0) return 0;
  if (props.method === 'bank') {
    return props.amount * feeRate.value + 10000; // 1% + 10,000 VND
  }
  return props.amount * feeRate.value; // 2% for crypto
});

const netAmount = computed(() => {
  return Math.max(0, props.amount - fee.value);
});

const formatAmount = (amt) => {
  if (props.method === 'bank') {
    return `${formatNumber(amt)} ₫`;
  }
  return formatCurrency(amt, 'USD');
};
</script>

