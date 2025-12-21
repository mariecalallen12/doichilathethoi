<template>
  <div class="market-analysis-dashboard bg-gray-900/80 backdrop-blur-sm p-6 rounded-lg shadow-2xl mb-6">
    <h2 class="text-2xl font-bold text-white mb-4">📊 Market Analysis Dashboard</h2>
    
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <!-- Total Signals -->
      <div class="bg-gradient-to-br from-purple-900/50 to-purple-800/50 p-4 rounded-lg border border-purple-500/30">
        <div class="text-sm text-gray-300 mb-1">Total Signals</div>
        <div class="text-3xl font-bold text-white">{{ analysis.total_signals || 0 }}</div>
      </div>
      
      <!-- Bullish Signals -->
      <div class="bg-gradient-to-br from-green-900/50 to-green-800/50 p-4 rounded-lg border border-green-500/30">
        <div class="text-sm text-gray-300 mb-1">Bullish Signals</div>
        <div class="text-3xl font-bold text-green-400">{{ analysis.bullish_signals || 0 }}</div>
      </div>
      
      <!-- Bearish Signals -->
      <div class="bg-gradient-to-br from-red-900/50 to-red-800/50 p-4 rounded-lg border border-red-500/30">
        <div class="text-sm text-gray-300 mb-1">Bearish Signals</div>
        <div class="text-3xl font-bold text-red-400">{{ analysis.bearish_signals || 0 }}</div>
      </div>
      
      <!-- Market Volatility -->
      <div class="bg-gradient-to-br from-yellow-900/50 to-yellow-800/50 p-4 rounded-lg border border-yellow-500/30">
        <div class="text-sm text-gray-300 mb-1">Volatility</div>
        <div class="text-3xl font-bold text-yellow-400">{{ analysis.volatility || 'N/A' }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  analysis: {
    type: Object,
    default: () => ({})
  }
});
</script>
