<template>
  <div class="top-movers bg-gray-900/80 backdrop-blur-sm p-6 rounded-lg shadow-2xl mb-6">
    <h2 class="text-2xl font-bold text-white mb-4">🚀 Top Movers</h2>
    
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Top Gainers -->
      <div class="bg-green-900/10 border border-green-500/30 rounded-lg p-4">
        <h3 class="text-lg font-semibold text-green-400 mb-3 flex items-center gap-2">
          <span>📈</span> Top Gainers
        </h3>
        
        <div class="space-y-2">
          <div 
            v-for="(gainer, index) in gainers" 
            :key="gainer.symbol"
            class="flex justify-between items-center bg-gray-800/50 p-3 rounded hover:bg-gray-700/50 transition-all"
          >
            <div class="flex items-center gap-3">
              <span class="text-gray-400 font-bold">{{ index + 1 }}</span>
              <div>
                <div class="text-white font-bold">{{ gainer.symbol }}</div>
                <div class="text-xs text-gray-400">{{ gainer.asset_class }}</div>
              </div>
            </div>
            <div class="text-right">
              <div class="text-white font-semibold">{{ gainer.current_price }}</div>
              <div class="text-green-400 font-bold text-sm">+{{ gainer.price_change_24h }}</div>
            </div>
          </div>
        </div>
        
        <div v-if="gainers.length === 0" class="text-center py-4 text-gray-500">
          No gainers data
        </div>
      </div>
      
      <!-- Top Losers -->
      <div class="bg-red-900/10 border border-red-500/30 rounded-lg p-4">
        <h3 class="text-lg font-semibold text-red-400 mb-3 flex items-center gap-2">
          <span>📉</span> Top Losers
        </h3>
        
        <div class="space-y-2">
          <div 
            v-for="(loser, index) in losers" 
            :key="loser.symbol"
            class="flex justify-between items-center bg-gray-800/50 p-3 rounded hover:bg-gray-700/50 transition-all"
          >
            <div class="flex items-center gap-3">
              <span class="text-gray-400 font-bold">{{ index + 1 }}</span>
              <div>
                <div class="text-white font-bold">{{ loser.symbol }}</div>
                <div class="text-xs text-gray-400">{{ loser.asset_class }}</div>
              </div>
            </div>
            <div class="text-right">
              <div class="text-white font-semibold">{{ loser.current_price }}</div>
              <div class="text-red-400 font-bold text-sm">{{ loser.price_change_24h }}</div>
            </div>
          </div>
        </div>
        
        <div v-if="losers.length === 0" class="text-center py-4 text-gray-500">
          No losers data
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  gainers: {
    type: Array,
    default: () => []
  },
  losers: {
    type: Array,
    default: () => []
  }
});
</script>
