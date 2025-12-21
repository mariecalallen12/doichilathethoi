<template>
  <div class="trading-recommendations bg-gray-900/80 backdrop-blur-sm p-6 rounded-lg shadow-2xl mb-6">
    <h2 class="text-2xl font-bold text-white mb-4">💡 Trading Recommendations</h2>
    
    <div class="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4">
      <div 
        v-for="(rec, symbol) in recommendations" 
        :key="symbol"
        :class="[
          'recommendation-card p-4 rounded-lg border-2 transition-all duration-300 hover:scale-105',
          rec.action === 'BUY' ? 'bg-green-900/20 border-green-500/50 hover:border-green-400' :
          rec.action === 'SELL' ? 'bg-red-900/20 border-red-500/50 hover:border-red-400' :
          'bg-gray-800/50 border-gray-600/50 hover:border-gray-500'
        ]"
      >
        <div class="flex justify-between items-start mb-3">
          <h3 class="text-lg font-bold text-white">{{ symbol }}</h3>
          <span :class="[
            'px-3 py-1 rounded-full text-xs font-bold',
            rec.action === 'BUY' ? 'bg-green-500 text-white' :
            rec.action === 'SELL' ? 'bg-red-500 text-white' :
            'bg-gray-500 text-white'
          ]">
            {{ rec.action }}
          </span>
        </div>
        
        <div class="space-y-2 text-sm">
          <div class="flex justify-between">
            <span class="text-gray-400">Entry Price:</span>
            <span class="text-white font-semibold">{{ rec.entry_price }}</span>
          </div>
          
          <div class="flex justify-between">
            <span class="text-gray-400">Target:</span>
            <span class="text-green-400 font-semibold">{{ rec.target }}</span>
          </div>
          
          <div class="flex justify-between">
            <span class="text-gray-400">Stop Loss:</span>
            <span class="text-red-400 font-semibold">{{ rec.stop_loss }}</span>
          </div>
          
          <div class="flex justify-between">
            <span class="text-gray-400">Risk/Reward:</span>
            <span class="text-purple-400 font-semibold">{{ rec.risk_reward }}</span>
          </div>
          
          <div class="mt-3 pt-3 border-t border-gray-700">
            <div class="text-gray-300 text-xs">{{ rec.reason }}</div>
          </div>
        </div>
      </div>
    </div>
    
    <div v-if="Object.keys(recommendations).length === 0" class="text-center py-8 text-gray-400">
      No recommendations available
    </div>
  </div>
</template>

<script setup>
defineProps({
  recommendations: {
    type: Object,
    default: () => ({})
  }
});
</script>

<style scoped>
.recommendation-card {
  backdrop-filter: blur(10px);
}
</style>
