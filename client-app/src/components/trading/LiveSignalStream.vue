<template>
  <div class="live-signal-stream bg-gray-900/80 backdrop-blur-sm p-6 rounded-lg shadow-2xl">
    <h2 class="text-2xl font-bold text-white mb-4 flex items-center gap-2">
      <span class="w-3 h-3 bg-red-500 rounded-full animate-pulse"></span>
      LIVE Signal Stream
    </h2>
    
    <div class="bg-gray-800/50 rounded-lg p-4 max-h-96 overflow-y-auto">
      <div v-if="stream.length === 0" class="text-center py-8 text-gray-400">
        Waiting for live signals...
      </div>
      
      <div v-else class="space-y-2">
        <div 
          v-for="(signal, index) in stream" 
          :key="index"
          class="flex justify-between items-center bg-gray-700/30 p-3 rounded hover:bg-gray-600/30 transition-all animate-fadeIn"
        >
          <div class="flex items-center gap-3">
            <div class="text-xs text-gray-400 font-mono">{{ formatTime(signal.timestamp) }}</div>
            <div class="font-bold text-white">{{ signal.symbol }}</div>
            <div :class="[
              'px-2 py-1 rounded text-xs font-bold',
              signal.signal.direction === 'BULLISH' ? 'bg-green-500 text-white' :
              signal.signal.direction === 'BEARISH' ? 'bg-red-500 text-white' :
              'bg-gray-500 text-white'
            ]">
              {{ signal.signal.direction }}
            </div>
          </div>
          
          <div class="text-right">
            <div class="text-white font-semibold text-sm">{{ signal.signal.current_price }}</div>
            <div :class="[
              'text-xs font-bold',
              parseFloat(signal.signal.price_change_24h) >= 0 ? 'text-green-400' : 'text-red-400'
            ]">
              {{ signal.signal.price_change_24h }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  stream: {
    type: Array,
    default: () => []
  }
});

function formatTime(timestamp) {
  const date = new Date(timestamp);
  return date.toLocaleTimeString('en-US', { 
    hour: '2-digit', 
    minute: '2-digit', 
    second: '2-digit',
    hour12: false 
  });
}
</script>

<style scoped>
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fadeIn {
  animation: fadeIn 0.3s ease-out;
}
</style>
