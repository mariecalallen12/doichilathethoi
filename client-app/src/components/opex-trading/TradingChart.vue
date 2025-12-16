<template>
  <div class="bg-slate-800/50 backdrop-blur-sm rounded-lg border border-purple-500/20 p-4">
    <h2 class="text-lg font-semibold text-white mb-4">{{ symbol }} Chart</h2>
    <div class="h-96 flex items-center justify-center text-purple-200/60">
      TradingView chart integration will be implemented here
    </div>
  </div>
</template>

<script setup>
defineProps({
  symbol: {
    type: String,
    default: 'BTCUSDT'
  }
})
</script>

