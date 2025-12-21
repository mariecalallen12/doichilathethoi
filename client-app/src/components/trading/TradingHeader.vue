<template>
  <div class="trading-header bg-gradient-to-r from-purple-900 via-indigo-900 to-blue-900 p-6 rounded-lg shadow-2xl mb-6">
    <div class="flex justify-between items-center">
      <div>
        <h1 class="text-4xl font-bold text-white mb-2">🎯 Trading Dashboard</h1>
        <p class="text-gray-300">Real-time Trading Signals & Market Analysis</p>
      </div>
      
      <div class="flex gap-4 items-center">
        <!-- WebSocket Status -->
        <div class="bg-gray-800/50 backdrop-blur-sm rounded-lg px-4 py-2">
          <div class="flex items-center gap-2">
            <div :class="['w-3 h-3 rounded-full', connectionStatus.signals ? 'bg-green-500 animate-pulse' : 'bg-red-500']"></div>
            <span class="text-sm text-white">Signals</span>
          </div>
        </div>
        
        <div class="bg-gray-800/50 backdrop-blur-sm rounded-lg px-4 py-2">
          <div class="flex items-center gap-2">
            <div :class="['w-3 h-3 rounded-full', connectionStatus.binary ? 'bg-green-500 animate-pulse' : 'bg-red-500']"></div>
            <span class="text-sm text-white">Binary</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  connectionStatus: {
    type: Object,
    required: true
  }
});
</script>
