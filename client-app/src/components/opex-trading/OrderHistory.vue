<template>
  <div class="bg-slate-800/50 backdrop-blur-sm rounded-lg border border-purple-500/20 p-4">
    <h2 class="text-lg font-semibold text-white mb-4">Order History</h2>
    
    <div v-if="orders.length === 0" class="text-purple-200/60 text-center py-8">
      No orders yet
    </div>
    
    <div v-else class="space-y-2 max-h-64 overflow-y-auto">
      <div
        v-for="order in orders.slice(0, 10)"
        :key="order.id"
        class="bg-slate-700/50 rounded-lg p-2 text-sm"
      >
        <div class="flex justify-between items-center">
          <div>
            <div class="text-white font-medium">{{ order.symbol }}</div>
            <div class="text-purple-200/60 text-xs">
              {{ order.side.toUpperCase() }} • {{ order.type.toUpperCase() }}
            </div>
          </div>
          <div :class="[
            'text-xs font-semibold',
            order.side === 'buy' ? 'text-green-400' : 'text-red-400'
          ]">
            {{ order.status.toUpperCase() }}
          </div>
        </div>
        <div class="text-purple-200/60 text-xs mt-1">
          Qty: {{ order.quantity }} • Price: {{ order.price || 'Market' }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  orders: {
    type: Array,
    default: () => []
  }
})
</script>

