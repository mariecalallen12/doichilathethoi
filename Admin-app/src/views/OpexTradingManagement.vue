<template>
  <div class="opex-trading-management p-6">
    <div class="mb-6">
      <h1 class="text-3xl font-bold text-white mb-2">Trading Management</h1>
      <p class="text-gray-400">Manage trading operations with OPEX Core</p>
    </div>

    <!-- Statistics Cards -->
    <TradingStatsCards :stats="stats" />

    <!-- Main Content Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
      <!-- Active Orders -->
      <div class="bg-slate-800 rounded-lg p-6">
        <h2 class="text-xl font-semibold text-white mb-4">Active Orders</h2>
        <OrderList 
          :orders="activeOrders"
          @edit-order="handleEditOrder"
          @cancel-order="handleCancelOrder"
        />
      </div>

      <!-- Open Positions -->
      <div class="bg-slate-800 rounded-lg p-6">
        <h2 class="text-xl font-semibold text-white mb-4">Open Positions</h2>
        <PositionList 
          :positions="openPositions"
          @edit-position="handleEditPosition"
          @close-position="handleClosePosition"
        />
      </div>
    </div>

    <!-- Market Data Overview -->
    <div class="mt-6 bg-slate-800 rounded-lg p-6">
      <h2 class="text-xl font-semibold text-white mb-4">Market Data Overview</h2>
      <MarketDataOverview />
    </div>

    <!-- Admin Controls -->
    <div class="mt-6 grid grid-cols-1 lg:grid-cols-2 gap-6">
      <PriceEditor @price-updated="handlePriceUpdated" />
      <BalanceEditor @balance-updated="handleBalanceUpdated" />
    </div>

    <!-- Adjustment History -->
    <div class="mt-6 bg-slate-800 rounded-lg p-6">
      <h2 class="text-xl font-semibold text-white mb-4">Adjustment History</h2>
      <AdjustmentHistory :adjustments="adjustments" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../services/api'
import TradingStatsCards from '../components/opex-trading/TradingStatsCards.vue'
import OrderList from '../components/opex-trading/OrderList.vue'
import PositionList from '../components/opex-trading/PositionList.vue'
import MarketDataOverview from '../components/opex-trading/MarketDataOverview.vue'
import PriceEditor from '../components/opex-trading/PriceEditor.vue'
import BalanceEditor from '../components/opex-trading/BalanceEditor.vue'
import AdjustmentHistory from '../components/opex-trading/AdjustmentHistory.vue'

const stats = ref({
  totalOrders: 0,
  activeOrders: 0,
  totalPositions: 0,
  openPositions: 0,
  totalVolume: 0
})

const activeOrders = ref([])
const openPositions = ref([])
const adjustments = ref([])

onMounted(async () => {
  await fetchData()
})

async function fetchData() {
  try {
    // Fetch statistics, orders, positions, and adjustments
    // These would be API calls to admin endpoints
    // For now, using placeholder data
  } catch (error) {
    console.error('Failed to fetch data:', error)
  }
}

function handleEditOrder(order) {
  // Open order editor modal
  console.log('Edit order:', order)
}

function handleCancelOrder(orderId) {
  // Cancel order via admin API
  console.log('Cancel order:', orderId)
}

function handleEditPosition(position) {
  // Open position editor modal
  console.log('Edit position:', position)
}

function handleClosePosition(positionId) {
  // Force close position via admin API
  console.log('Close position:', positionId)
}

function handlePriceUpdated(update) {
  console.log('Price updated:', update)
  // Refresh market data
}

function handleBalanceUpdated(update) {
  console.log('Balance updated:', update)
  // Refresh user data
}
</script>

<style scoped>
.opex-trading-management {
  background: linear-gradient(135deg, #1e293b 0%, #312e81 100%);
  min-height: 100vh;
}
</style>

