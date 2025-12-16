<template>
  <div class="space-y-4">
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div
        v-for="symbol in symbols"
        :key="symbol.symbol"
        class="bg-slate-700/50 rounded-lg p-4"
      >
        <div class="text-white font-semibold mb-1">{{ symbol.symbol }}</div>
        <div class="text-2xl font-bold text-purple-400">${{ symbol.price.toLocaleString() }}</div>
        <div :class="[
          'text-sm',
          symbol.change >= 0 ? 'text-green-400' : 'text-red-400'
        ]">
          {{ symbol.change >= 0 ? '+' : '' }}{{ symbol.change.toFixed(2) }}%
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../services/api'

const symbols = ref([])

onMounted(async () => {
  try {
    const response = await api.get('/api/market/symbols')
    // Add mock price data (will be replaced with real data from OPEX)
    symbols.value = response.data.slice(0, 6).map(s => ({
      ...s,
      price: Math.random() * 50000 + 20000,
      change: (Math.random() - 0.5) * 10
    }))
  } catch (error) {
    console.error('Failed to fetch symbols:', error)
  }
})
</script>

