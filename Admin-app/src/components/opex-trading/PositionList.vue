<template>
  <div class="space-y-2">
    <div v-if="positions.length === 0" class="text-gray-400 text-center py-8">
      No open positions
    </div>
    
    <div
      v-for="position in positions"
      :key="position.id"
      class="bg-slate-700/50 rounded-lg p-4 hover:bg-slate-700/70 transition-all"
    >
      <div class="flex justify-between items-start mb-2">
        <div>
          <div class="text-white font-semibold">{{ position.symbol }}</div>
          <div class="text-gray-400 text-sm">
            {{ position.side.toUpperCase() }} • Qty: {{ position.quantity }} • Entry: ${{ position.entry_price }}
          </div>
        </div>
        <div :class="[
          'text-sm font-semibold',
          position.unrealized_pnl >= 0 ? 'text-green-400' : 'text-red-400'
        ]">
          {{ position.unrealized_pnl >= 0 ? '+' : '' }}{{ position.unrealized_pnl.toFixed(2) }}
        </div>
      </div>
      
      <div class="flex gap-2 mt-3">
        <button
          @click="$emit('edit-position', position)"
          class="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold rounded transition-all"
        >
          Edit
        </button>
        <button
          @click="$emit('close-position', position.id)"
          class="px-3 py-1.5 bg-red-600 hover:bg-red-700 text-white text-sm font-semibold rounded transition-all"
        >
          Force Close
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  positions: {
    type: Array,
    default: () => []
  }
})

defineEmits(['edit-position', 'close-position'])
</script>

