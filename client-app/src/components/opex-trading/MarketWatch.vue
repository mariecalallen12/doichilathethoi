<template>
  <div class="bg-slate-800/50 backdrop-blur-sm rounded-lg border border-purple-500/20 p-4">
    <h2 class="text-lg font-semibold text-white mb-4">Market Watch</h2>
    <div class="space-y-2">
      <div
        v-for="symbol in symbols"
        :key="symbol.symbol"
        @click="$emit('symbol-selected', symbol.symbol)"
        :class="[
          'p-3 rounded-lg cursor-pointer transition-all',
          selectedSymbol === symbol.symbol
            ? 'bg-purple-600/30 border border-purple-400'
            : 'bg-slate-700/50 hover:bg-slate-700/70'
        ]"
      >
        <div class="flex justify-between items-center">
          <span class="text-white font-medium">{{ symbol.symbol }}</span>
          <span :class="[
            'text-sm font-semibold',
            symbol.change >= 0 ? 'text-green-400' : 'text-red-400'
          ]">
            {{ symbol.change >= 0 ? '+' : '' }}{{ symbol.change.toFixed(2) }}%
          </span>
        </div>
        <div class="text-purple-200/80 text-sm mt-1">
          ${{ symbol.price.toLocaleString() }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../services/api/client'
import { debugLog } from '../../utils/sessionManager'

defineProps({
  selectedSymbol: {
    type: String,
    default: 'BTCUSDT'
  }
})

defineEmits(['symbol-selected'])

const symbols = ref([])

onMounted(async () => {
  debugLog('MarketWatch.vue:onMounted', 'MarketWatch mounted, fetching symbols', { url: '/api/market/symbols' })
  try {
    // Validate api is available and has get method
    if (!api || typeof api.get !== 'function') {
      throw new Error('API client is not properly initialized. Please refresh the page.')
    }
    
    const response = await api.get('/market/symbols')
    debugLog('MarketWatch.vue:fetchSymbols', 'MarketWatch symbols success', { status: response.status, dataLength: response.data?.length })
    
    // Validate response structure
    if (!response || !response.data) {
      throw new Error('Invalid response from server')
    }
    
    // Transform symbols and add mock price data (will be replaced with real data)
    if (Array.isArray(response.data)) {
      symbols.value = response.data.map(s => ({
        ...s,
        price: s.price || Math.random() * 50000 + 20000,
        change: s.change || (Math.random() - 0.5) * 10
      }))
    } else {
      // Fallback data if API returns unexpected format
      console.warn('API returned unexpected format, using fallback data')
      symbols.value = [
        { symbol: 'BTCUSDT', price: 43250, change: 2.98 },
        { symbol: 'ETHUSDT', price: 2650, change: 1.73 },
        { symbol: 'BNBUSDT', price: 315, change: 2.77 }
      ]
    }
  } catch (error) {
    debugLog('MarketWatch.vue:fetchSymbols', 'MarketWatch symbols error', { status: error?.response?.status, statusText: error?.response?.statusText, detail: error?.response?.data?.detail, url: error?.config?.url })
    console.error('Failed to fetch symbols:', error)
    
    // Check for specific API errors
    if (error.message && error.message.includes('is not a function')) {
      console.error('API client error: The API client may not be properly initialized. This is likely a configuration issue.')
    }
    
    // Fallback data on error
    symbols.value = [
      { symbol: 'BTCUSDT', price: 43250, change: 2.98 },
      { symbol: 'ETHUSDT', price: 2650, change: 1.73 },
      { symbol: 'BNBUSDT', price: 315, change: 2.77 }
    ]
  }
})
</script>

