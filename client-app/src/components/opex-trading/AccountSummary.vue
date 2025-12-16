<template>
  <div class="bg-slate-800/50 backdrop-blur-sm rounded-lg border border-purple-500/20 p-4">
    <h2 class="text-lg font-semibold text-white mb-4">Account Summary</h2>
    <div class="space-y-3">
      <div class="flex justify-between">
        <span class="text-purple-200/80">Available Balance</span>
        <span class="text-white font-semibold">$0.00</span>
      </div>
      <div class="flex justify-between">
        <span class="text-purple-200/80">Used Margin</span>
        <span class="text-white font-semibold">$0.00</span>
      </div>
      <div class="flex justify-between">
        <span class="text-purple-200/80">Unrealized P&L</span>
        <span :class="[
          'font-semibold',
          totalPnl >= 0 ? 'text-green-400' : 'text-red-400'
        ]">
          {{ totalPnl >= 0 ? '+' : '' }}{{ totalPnl.toFixed(2) }}
        </span>
      </div>
      <div class="flex justify-between">
        <span class="text-purple-200/80">Equity</span>
        <span class="text-white font-semibold">$0.00</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useOpexTradingStore } from '../../stores/opex_trading'

const tradingStore = useOpexTradingStore()
const totalPnl = computed(() => tradingStore.totalUnrealizedPnl)
</script>

