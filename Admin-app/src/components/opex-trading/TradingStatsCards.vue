<template>
  <div class="grid grid-cols-1 md:grid-cols-5 gap-4">
    <div class="bg-slate-700 rounded-lg p-4">
      <div class="text-gray-400 text-sm mb-1">Total Orders</div>
      <div class="text-2xl font-bold text-white">{{ stats.totalOrders }}</div>
    </div>
    <div class="bg-slate-700 rounded-lg p-4">
      <div class="text-gray-400 text-sm mb-1">Active Orders</div>
      <div class="text-2xl font-bold text-yellow-400">{{ stats.activeOrders }}</div>
    </div>
    <div class="bg-slate-700 rounded-lg p-4">
      <div class="text-gray-400 text-sm mb-1">Total Positions</div>
      <div class="text-2xl font-bold text-white">{{ stats.totalPositions }}</div>
    </div>
    <div class="bg-slate-700 rounded-lg p-4">
      <div class="text-gray-400 text-sm mb-1">Open Positions</div>
      <div class="text-2xl font-bold text-blue-400">{{ stats.openPositions }}</div>
    </div>
    <div class="bg-slate-700 rounded-lg p-4">
      <div class="text-gray-400 text-sm mb-1">Total Volume</div>
      <div class="text-2xl font-bold text-green-400">${{ stats.totalVolume.toLocaleString() }}</div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  stats: {
    type: Object,
    required: true
  }
})
</script>

