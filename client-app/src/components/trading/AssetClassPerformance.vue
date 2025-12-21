<template>
  <div class="asset-class-performance bg-gray-900/80 backdrop-blur-sm p-6 rounded-lg shadow-2xl mb-6">
    <h2 class="text-2xl font-bold text-white mb-4">📊 Asset Class Performance</h2>
    
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div 
        v-for="(data, assetClass) in analysis" 
        :key="assetClass"
        class="bg-gray-800/50 p-4 rounded-lg border border-gray-700/50 hover:border-purple-500/50 transition-all"
      >
        <h3 class="text-lg font-semibold text-white mb-3">{{ assetClass }}</h3>
        
        <div class="space-y-2">
          <div class="flex justify-between">
            <span class="text-gray-400 text-sm">Average Change:</span>
            <span :class="[
              'font-bold text-sm',
              data.average_change >= 0 ? 'text-green-400' : 'text-red-400'
            ]">
              {{ data.average_change >= 0 ? '+' : '' }}{{ data.average_change }}%
            </span>
          </div>
          
          <div class="flex justify-between">
            <span class="text-gray-400 text-sm">Bullish Signals:</span>
            <span class="text-green-400 font-bold text-sm">{{ data.bullish_count }}</span>
          </div>
          
          <div class="flex justify-between">
            <span class="text-gray-400 text-sm">Bearish Signals:</span>
            <span class="text-red-400 font-bold text-sm">{{ data.bearish_count }}</span>
          </div>
          
          <div class="mt-3 pt-3 border-t border-gray-700">
            <div class="flex justify-between items-center">
              <span class="text-gray-400 text-sm">Sentiment:</span>
              <span :class="[
                'font-bold text-sm px-2 py-1 rounded',
                data.sentiment === 'BULLISH' ? 'bg-green-900/50 text-green-400' :
                data.sentiment === 'BEARISH' ? 'bg-red-900/50 text-red-400' :
                'bg-gray-700 text-gray-400'
              ]">
                {{ data.sentiment }}
              </span>
            </div>
          </div>
        </div>
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
