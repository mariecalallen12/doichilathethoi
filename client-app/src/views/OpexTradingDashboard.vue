<template>
  <div class="opex-trading-dashboard min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
    <!-- Header -->
    <div class="bg-slate-800/50 backdrop-blur-sm border-b border-purple-500/20">
      <div class="container mx-auto px-4 py-4">
        <h1 class="text-2xl font-bold text-white">Trading Dashboard</h1>
        <p class="text-purple-200/80">Real-time trading with OPEX Core</p>
      </div>
    </div>

    <!-- Main Content -->
    <div class="container mx-auto px-4 py-6">
      <div class="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <!-- Left Column: Market Watch & Order Panel -->
        <div class="lg:col-span-1 space-y-6">
          <!-- Market Watch -->
          <MarketWatch 
            :selected-symbol="selectedSymbol"
            @symbol-selected="handleSymbolSelected"
          />

          <!-- Order Panel -->
          <OrderPanel 
            :symbol="selectedSymbol"
            @order-placed="handleOrderPlaced"
          />
        </div>

        <!-- Center Column: Chart & Order Book -->
        <div class="lg:col-span-2 space-y-6">
          <!-- Trading Chart -->
          <TradingChart :symbol="selectedSymbol" />

          <!-- Order Book -->
          <OrderBook :symbol="selectedSymbol" />
        </div>

        <!-- Right Column: Positions & Order History -->
        <div class="lg:col-span-1 space-y-6">
          <!-- Account Summary -->
          <AccountSummary />

          <!-- Positions List -->
          <PositionList 
            :positions="openPositions"
            @close-position="handleClosePosition"
          />

          <!-- Order History -->
          <OrderHistory :orders="orders" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useOpexTradingStore } from '../stores/opex_trading'
import MarketWatch from '../components/opex-trading/MarketWatch.vue'
import OrderPanel from '../components/opex-trading/OrderPanel.vue'
import TradingChart from '../components/opex-trading/TradingChart.vue'
import OrderBook from '../components/opex-trading/OrderBook.vue'
import AccountSummary from '../components/opex-trading/AccountSummary.vue'
import PositionList from '../components/opex-trading/PositionList.vue'
import OrderHistory from '../components/opex-trading/OrderHistory.vue'
import { connectWebSocket } from '../services/opex_websocket'

const tradingStore = useOpexTradingStore()
const selectedSymbol = ref('BTCUSDT')

const orders = computed(() => tradingStore.orders)
const openPositions = computed(() => tradingStore.openPositions)

onMounted(async () => {
  // #region agent log
  fetch('http://localhost:7242/ingest/a94652aa-f954-45ed-8dd8-1c88a5bdb78d',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'OpexTradingDashboard.vue:75',message:'Trading dashboard mounted',data:{pathname:window.location.pathname},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'C'})).catch(()=>{});
  // #endregion
  try {
    // Fetch initial data with error handling
    try {
      // #region agent log
      fetch('http://localhost:7242/ingest/a94652aa-f954-45ed-8dd8-1c88a5bdb78d',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'OpexTradingDashboard.vue:79',message:'Calling fetchOrders',data:{},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'C'})).catch(()=>{});
      // #endregion
      await tradingStore.fetchOrders()
      // #region agent log
      fetch('http://localhost:7242/ingest/a94652aa-f954-45ed-8dd8-1c88a5bdb78d',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'OpexTradingDashboard.vue:82',message:'fetchOrders completed',data:{},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'C'})).catch(()=>{});
      // #endregion
    } catch (error) {
      // #region agent log
      fetch('http://localhost:7242/ingest/a94652aa-f954-45ed-8dd8-1c88a5bdb78d',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'OpexTradingDashboard.vue:85',message:'fetchOrders error',data:{errorMessage:error?.message,errorStatus:error?.response?.status},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'C'})).catch(()=>{});
      // #endregion
      console.error('Failed to fetch orders:', error)
      // Continue even if orders fail
    }
    
    try {
      // #region agent log
      fetch('http://localhost:7242/ingest/a94652aa-f954-45ed-8dd8-1c88a5bdb78d',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'OpexTradingDashboard.vue:91',message:'Calling fetchPositions',data:{},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'C'})).catch(()=>{});
      // #endregion
      await tradingStore.fetchPositions()
      // #region agent log
      fetch('http://localhost:7242/ingest/a94652aa-f954-45ed-8dd8-1c88a5bdb78d',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'OpexTradingDashboard.vue:94',message:'fetchPositions completed',data:{},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'C'})).catch(()=>{});
      // #endregion
    } catch (error) {
      // #region agent log
      fetch('http://localhost:7242/ingest/a94652aa-f954-45ed-8dd8-1c88a5bdb78d',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'OpexTradingDashboard.vue:97',message:'fetchPositions error',data:{errorMessage:error?.message,errorStatus:error?.response?.status},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'C'})).catch(()=>{});
      // #endregion
      console.error('Failed to fetch positions:', error)
      // Continue even if positions fail
    }
    
    // Connect WebSocket for real-time updates
    try {
      connectWebSocket({
        onOrderUpdate: (order) => tradingStore.updateOrder(order),
        onPositionUpdate: (position) => tradingStore.updatePosition(position),
        onConnected: () => tradingStore.setWsConnected(true),
        onDisconnected: () => tradingStore.setWsConnected(false),
        onError: (error) => {
          console.error('OPEX WebSocket error in dashboard:', error)
          tradingStore.setWsConnected(false)
        }
      })
    } catch (error) {
      console.error('Failed to connect WebSocket:', error)
      // Continue without WebSocket connection
    }
  } catch (error) {
    console.error('Error initializing trading dashboard:', error)
    
    // Check for specific API errors
    if (error.message && error.message.includes('is not a function')) {
      console.error('API client error: The API client may not be properly initialized. Please refresh the page.')
    }
    
    // Don't throw - let the component render with error state
  }
})

onUnmounted(() => {
  // Disconnect WebSocket
  // WebSocket cleanup will be handled by the service
})

function handleSymbolSelected(symbol) {
  selectedSymbol.value = symbol
  tradingStore.setSelectedSymbol(symbol)
  tradingStore.fetchOrders(symbol)
  tradingStore.fetchPositions(symbol)
}

async function handleOrderPlaced(order) {
  await tradingStore.placeOrder(order)
  // Refresh orders list
  await tradingStore.fetchOrders(selectedSymbol.value)
}

async function handleClosePosition(positionId) {
  await tradingStore.closePosition(positionId)
  // Refresh positions list
  await tradingStore.fetchPositions(selectedSymbol.value)
}
</script>

<style scoped>
.opex-trading-dashboard {
  font-family: 'Inter', sans-serif;
}
</style>

