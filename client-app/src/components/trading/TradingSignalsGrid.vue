<template>
  <div class="trading-signals-grid bg-gray-900/80 backdrop-blur-sm p-6 rounded-lg shadow-2xl mb-6">
    <h2 class="text-2xl font-bold text-white mb-4">📈 Trading Signals</h2>
    
    <div v-if="loading" class="text-center py-8">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500 mx-auto"></div>
      <p class="text-gray-400 mt-4">Loading signals...</p>
    </div>
    
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      <div 
        v-for="(signal, symbol) in signals" 
        :key="symbol"
        :class="[
          'signal-card p-4 rounded-lg border-2 transition-all duration-300 hover:scale-105 cursor-pointer',
          signal.direction === 'BULLISH' ? 'bg-green-900/20 border-green-500/50 hover:border-green-400' :
          signal.direction === 'BEARISH' ? 'bg-red-900/20 border-red-500/50 hover:border-red-400' :
          'bg-gray-800/50 border-gray-600/50 hover:border-gray-500'
        ]"
      >
        <!-- Symbol & Asset Class -->
        <div class="flex justify-between items-start mb-3">
          <div>
            <h3 class="text-lg font-bold text-white">{{ symbol }}</h3>
            <span class="text-xs text-gray-400">{{ signal.asset_class }}</span>
          </div>
          <div :class="[
            'px-2 py-1 rounded text-xs font-bold',
            signal.direction === 'BULLISH' ? 'bg-green-500 text-white' :
            signal.direction === 'BEARISH' ? 'bg-red-500 text-white' :
            'bg-gray-500 text-white'
          ]">
            {{ signal.direction }}
          </div>
        </div>
        
        <!-- Current Price -->
        <div class="mb-3">
          <div class="text-2xl font-bold text-white">{{ signal.current_price }}</div>
          <div :class="[
            'text-sm font-semibold',
            parseFloat(signal.price_change_24h) >= 0 ? 'text-green-400' : 'text-red-400'
          ]">
            {{ signal.price_change_24h }}
          </div>
        </div>
        
        <!-- Strength Indicator -->
        <div class="mb-2">
          <div class="flex justify-between text-xs text-gray-400 mb-1">
            <span>Strength</span>
            <span>{{ signal.strength }}%</span>
          </div>
          <div class="w-full bg-gray-700 rounded-full h-2">
            <div 
              :class="[
                'h-2 rounded-full transition-all duration-500',
                signal.strength >= 70 ? 'bg-green-500' :
                signal.strength >= 40 ? 'bg-yellow-500' :
                'bg-red-500'
              ]"
              :style="{ width: signal.strength + '%' }"
            ></div>
          </div>
        </div>
        
        <!-- Binary Code -->
        <div class="flex justify-between items-center text-xs">
          <span class="text-gray-400">Binary:</span>
          <span :class="[
            'font-mono font-bold',
            signal.binary_code === '1' ? 'text-green-400' : 'text-red-400'
          ]">
            {{ signal.binary_code }}
          </span>
        </div>
      </div>
    </div>
    
    <div v-if="!loading && Object.keys(signals).length === 0" class="text-center py-8 text-gray-400">
      No trading signals available
    </div>
  </div>
</template>

<script setup>
defineProps({
  signals: {
    type: Object,
    default: () => ({})
  },
  loading: {
    type: Boolean,
    default: false
  }
});
</script>

<style scoped>
.signal-card {
  backdrop-filter: blur(10px);
}
</style>
