<template>
  <div class="binary-sentiment-board bg-gray-900/80 backdrop-blur-sm p-6 rounded-lg shadow-2xl mb-6">
    <h2 class="text-2xl font-bold text-white mb-4">📊 Binary Market Sentiment</h2>
    
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Binary String Display -->
      <div class="col-span-2 bg-gray-800/50 p-4 rounded-lg">
        <h3 class="text-lg font-semibold text-gray-300 mb-3">Binary Signal Stream</h3>
        <div class="font-mono text-2xl text-green-400 break-all leading-relaxed">
          {{ binaryArray.join('') || 'Loading...' }}
        </div>
        <div class="mt-3 text-sm text-gray-400">
          <span class="text-green-400">1</span> = BULLISH (BUY) &nbsp;|&nbsp; 
          <span class="text-red-400">0</span> = BEARISH (SELL)
        </div>
      </div>
      
      <!-- Market Sentiment Gauge -->
      <div class="bg-gray-800/50 p-4 rounded-lg">
        <h3 class="text-lg font-semibold text-gray-300 mb-3">Overall Sentiment</h3>
        
        <div class="flex flex-col items-center justify-center h-40">
          <div :class="[
            'text-5xl font-bold mb-2',
            marketSentiment === 'BULLISH' ? 'text-green-400' :
            marketSentiment === 'BEARISH' ? 'text-red-400' :
            'text-yellow-400'
          ]">
            {{ marketSentiment }}
          </div>
          
          <div class="w-full bg-gray-700 rounded-full h-4 mt-4">
            <div 
              class="bg-gradient-to-r from-red-500 via-yellow-500 to-green-500 h-4 rounded-full transition-all duration-500"
              :style="{ width: sentimentPercentage + '%' }"
            ></div>
          </div>
          
          <div class="flex justify-between w-full mt-2 text-xs text-gray-400">
            <span>{{ bearishCount }} Bearish</span>
            <span>{{ bullishCount }} Bullish</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  binaryArray: {
    type: Array,
    default: () => []
  },
  marketSentiment: {
    type: String,
    default: 'UNKNOWN'
  }
});

const bullishCount = computed(() => props.binaryArray.filter(b => b === 1).length);
const bearishCount = computed(() => props.binaryArray.filter(b => b === 0).length);
const sentimentPercentage = computed(() => {
  const total = props.binaryArray.length;
  if (total === 0) return 50;
  return (bullishCount.value / total) * 100;
});
</script>
