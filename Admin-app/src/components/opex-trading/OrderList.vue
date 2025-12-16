<template>
  <div class="space-y-2">
    <div v-if="orders.length === 0" class="text-gray-400 text-center py-8">
      No active orders
    </div>
    
    <div
      v-for="order in orders"
      :key="order.id"
      class="bg-slate-700/50 rounded-lg p-4 hover:bg-slate-700/70 transition-all"
    >
      <div class="flex justify-between items-start mb-2">
        <div>
          <div class="text-white font-semibold">{{ order.symbol }}</div>
          <div class="text-gray-400 text-sm">
            {{ order.side.toUpperCase() }} • {{ order.type.toUpperCase() }} • Qty: {{ order.quantity }}
          </div>
        </div>
        <div :class="[
          'px-2 py-1 rounded text-xs font-semibold',
          order.status === 'filled' ? 'bg-green-500/20 text-green-400' :
          order.status === 'pending' ? 'bg-yellow-500/20 text-yellow-400' :
          'bg-gray-500/20 text-gray-400'
        ]">
          {{ order.status.toUpperCase() }}
        </div>
      </div>
      
      <div class="flex gap-2 mt-3">
        <button
          @click="$emit('edit-order', order)"
          class="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold rounded transition-all"
        >
          Edit
        </button>
        <button
          @click="$emit('cancel-order', order.id)"
          class="px-3 py-1.5 bg-red-600 hover:bg-red-700 text-white text-sm font-semibold rounded transition-all"
        >
          Cancel
        </button>
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

defineEmits(['edit-order', 'cancel-order'])
</script>

