<template>
  <div class="bg-slate-800/50 backdrop-blur-sm rounded-lg border border-purple-500/20 p-4">
    <h2 class="text-lg font-semibold text-white mb-4">Order Book</h2>
    
    <div class="grid grid-cols-2 gap-4">
      <!-- Asks (Sell Orders) -->
      <div>
        <div class="text-red-400 font-semibold mb-2">Asks</div>
        <div class="space-y-1 max-h-64 overflow-y-auto">
          <div
            v-for="(ask, index) in orderbook.asks"
            :key="index"
            class="flex justify-between text-sm py-1 px-2 bg-red-500/10 rounded"
          >
            <span class="text-red-300">{{ ask[1] }}</span>
            <span class="text-white">{{ ask[0].toFixed(2) }}</span>
          </div>
        </div>
      </div>
      
      <!-- Bids (Buy Orders) -->
      <div>
        <div class="text-green-400 font-semibold mb-2">Bids</div>
        <div class="space-y-1 max-h-64 overflow-y-auto">
          <div
            v-for="(bid, index) in orderbook.bids"
            :key="index"
            class="flex justify-between text-sm py-1 px-2 bg-green-500/10 rounded"
          >
            <span class="text-green-300">{{ bid[1] }}</span>
            <span class="text-white">{{ bid[0].toFixed(2) }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import api from '../../services/api/client'

const props = defineProps({
  symbol: {
    type: String,
    default: 'BTCUSDT'
  }
})

const orderbook = ref({
  bids: [],
  asks: []
})

async function fetchOrderbook() {
  // #region agent log
  fetch('http://localhost:7242/ingest/a94652aa-f954-45ed-8dd8-1c88a5bdb78d',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'OrderBook.vue:55',message:'OrderBook fetchOrderbook called',data:{symbol:props.symbol,url:`/api/market/orderbook/${props.symbol}`},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'E'})).catch(()=>{});
  // #endregion
  try {
    // Validate api is available and has get method
    if (!api || typeof api.get !== 'function') {
      throw new Error('API client is not properly initialized. Please refresh the page.')
    }
    
    const response = await api.get(`/api/market/orderbook/${props.symbol}`)
    // #region agent log
    fetch('http://localhost:7242/ingest/a94652aa-f954-45ed-8dd8-1c88a5bdb78d',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'OrderBook.vue:63',message:'OrderBook fetchOrderbook success',data:{status:response.status,hasBids:!!response.data?.bids,hasAsks:!!response.data?.asks},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'E'})).catch(()=>{});
    // #endregion
    
    // Validate response structure
    if (!response || !response.data) {
      throw new Error('Invalid response from server')
    }
    
    if (response.data) {
      orderbook.value = {
        bids: Array.isArray(response.data.bids) ? response.data.bids : [],
        asks: Array.isArray(response.data.asks) ? response.data.asks : []
      }
    }
  } catch (error) {
    // #region agent log
    fetch('http://localhost:7242/ingest/a94652aa-f954-45ed-8dd8-1c88a5bdb78d',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'OrderBook.vue:75',message:'OrderBook fetchOrderbook error',data:{status:error?.response?.status,statusText:error?.response?.statusText,detail:error?.response?.data?.detail,url:error?.config?.url,symbol:props.symbol},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'E'})).catch(()=>{});
    // #endregion
    console.error('Failed to fetch orderbook:', error)
    
    // Check for specific API errors
    if (error.message && error.message.includes('is not a function')) {
      console.error('API client error: The API client may not be properly initialized. This is likely a configuration issue.')
    }
    
    // Keep existing orderbook data on error
    if (orderbook.value.bids.length === 0 && orderbook.value.asks.length === 0) {
      // Only set empty if no data exists
      orderbook.value = { bids: [], asks: [] }
    }
  }
}

onMounted(() => {
  fetchOrderbook()
  // Refresh every 2 seconds
  const interval = setInterval(fetchOrderbook, 2000)
  
  // Cleanup on unmount
  return () => clearInterval(interval)
})

watch(() => props.symbol, () => {
  fetchOrderbook()
})
</script>

