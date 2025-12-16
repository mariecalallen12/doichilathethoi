/**
 * OPEX Trading Store
 * Pinia store for managing trading state with OPEX integration
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import opexTradingService from '../services/opex_trading'

export const useOpexTradingStore = defineStore('opexTrading', () => {
  // State
  const orders = ref([])
  const positions = ref([])
  const marketData = ref({})
  const selectedSymbol = ref('BTCUSDT')
  const isLoading = ref(false)
  const error = ref(null)
  const wsConnected = ref(false)

  // Getters
  const openOrders = computed(() => 
    orders.value.filter(order => 
      ['pending', 'open', 'partial'].includes(order.status)
    )
  )

  const filledOrders = computed(() => 
    orders.value.filter(order => order.status === 'filled')
  )

  const openPositions = computed(() => 
    positions.value.filter(pos => pos.status === 'open')
  )

  const totalUnrealizedPnl = computed(() => 
    openPositions.value.reduce((sum, pos) => sum + (pos.unrealized_pnl || 0), 0)
  )

  // Actions
  async function fetchOrders(symbol = null) {
    isLoading.value = true
    error.value = null
    try {
      const data = await opexTradingService.getOrders(symbol)
      orders.value = data || []
      return data || []
    } catch (err) {
      error.value = err.message
      // Don't throw - return empty array instead
      orders.value = []
      return []
    } finally {
      isLoading.value = false
    }
  }

  async function fetchPositions(symbol = null) {
    isLoading.value = true
    error.value = null
    try {
      const data = await opexTradingService.getPositions(symbol)
      positions.value = data || []
      return data || []
    } catch (err) {
      error.value = err.message
      // Don't throw - return empty array instead
      positions.value = []
      return []
    } finally {
      isLoading.value = false
    }
  }

  async function placeOrder(orderData) {
    isLoading.value = true
    error.value = null
    try {
      const order = await opexTradingService.placeOrder(orderData)
      orders.value.unshift(order)
      return order
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function cancelOrder(orderId) {
    isLoading.value = true
    error.value = null
    try {
      await opexTradingService.cancelOrder(orderId)
      const index = orders.value.findIndex(o => o.id === orderId)
      if (index !== -1) {
        orders.value[index].status = 'cancelled'
      }
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function closePosition(positionId) {
    isLoading.value = true
    error.value = null
    try {
      await opexTradingService.closePosition(positionId)
      const index = positions.value.findIndex(p => p.id === positionId)
      if (index !== -1) {
        positions.value[index].status = 'closed'
      }
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      isLoading.value = false
    }
  }

  function updateOrder(orderUpdate) {
    const index = orders.value.findIndex(o => o.id === orderUpdate.id)
    if (index !== -1) {
      orders.value[index] = { ...orders.value[index], ...orderUpdate }
    }
  }

  function updatePosition(positionUpdate) {
    const index = positions.value.findIndex(p => p.id === positionUpdate.id)
    if (index !== -1) {
      positions.value[index] = { ...positions.value[index], ...positionUpdate }
    }
  }

  function setSelectedSymbol(symbol) {
    selectedSymbol.value = symbol
  }

  function setWsConnected(connected) {
    wsConnected.value = connected
  }

  function clearError() {
    error.value = null
  }

  return {
    // State
    orders,
    positions,
    marketData,
    selectedSymbol,
    isLoading,
    error,
    wsConnected,
    // Getters
    openOrders,
    filledOrders,
    openPositions,
    totalUnrealizedPnl,
    // Actions
    fetchOrders,
    fetchPositions,
    placeOrder,
    cancelOrder,
    closePosition,
    updateOrder,
    updatePosition,
    setSelectedSymbol,
    setWsConnected,
    clearError
  }
})

