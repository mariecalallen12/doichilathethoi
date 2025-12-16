<template>
  <div class="flex items-center space-x-2">
    <span v-if="!hidden" class="font-orbitron text-2xl font-bold text-white">
      {{ formattedAmount }}
    </span>
    <span v-else class="font-orbitron text-2xl font-bold text-white">
      ••••••
    </span>
    <button
      @click="toggleVisibility"
      class="p-1 text-purple-300 hover:text-white transition-colors"
      :title="hidden ? 'Hiển thị số dư' : 'Ẩn số dư'"
    >
      <i :class="hidden ? 'fas fa-eye' : 'fas fa-eye-slash'"></i>
    </button>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { formatCurrency, formatNumber } from '../../../services/utils/formatters';

const props = defineProps({
  amount: {
    type: Number,
    required: true,
  },
  currency: {
    type: String,
    default: 'USD',
  },
  showCurrency: {
    type: Boolean,
    default: true,
  },
});

const hidden = ref(false);

const toggleVisibility = () => {
  hidden.value = !hidden.value;
};

const formattedAmount = computed(() => {
  if (props.currency === 'VND') {
    return `${formatNumber(props.amount)} ₫`;
  }
  if (props.currency === 'BTC') {
    return `₿${formatNumber(props.amount, 8)}`;
  }
  if (props.currency === 'ETH') {
    return `Ξ${formatNumber(props.amount, 6)}`;
  }
  if (props.showCurrency) {
    return formatCurrency(props.amount, props.currency);
  }
  return `$${formatNumber(props.amount)}`;
});
</script>

