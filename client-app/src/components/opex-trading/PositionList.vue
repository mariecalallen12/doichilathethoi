<template>
  <div class="bg-slate-800/50 backdrop-blur-sm rounded-lg border border-purple-500/20 p-4">
    <h2 class="text-lg font-semibold text-white mb-4">Open Positions</h2>
    
    <div v-if="positions.length === 0" class="text-purple-200/60 text-center py-8">
      No open positions
    </div>
    
    <div v-else class="space-y-3">
      <div
        v-for="position in positions"
        :key="position.id"
        class="bg-slate-700/50 rounded-lg p-3 border border-purple-500/10"
      >
        <div class="flex justify-between items-start mb-2">
          <div>
            <div class="text-white font-semibold">{{ position.symbol }}</div>
            <div class="text-purple-200/80 text-sm">
              {{ position.side.toUpperCase() }} • {{ position.quantity }}
            </div>
          </div>
          <div :class="[
            'text-sm font-semibold',
            position.unrealized_pnl >= 0 ? 'text-green-400' : 'text-red-400'
          ]">
            {{ position.unrealized_pnl >= 0 ? '+' : '' }}{{ position.unrealized_pnl.toFixed(2) }}
          </div>
        </div>
        
        <div class="flex justify-between text-xs text-purple-200/60 mb-2">
          <span>Entry: ${{ position.entry_price.toFixed(2) }}</span>
          <span v-if="position.current_price">
            Current: ${{ position.current_price.toFixed(2) }}
          </span>
        </div>
        
        <button
          @click="$emit('close-position', position.id)"
          class="w-full mt-2 px-3 py-1.5 bg-red-600/20 hover:bg-red-600/30 text-red-400 text-sm font-semibold rounded transition-all"
        >
          Close Position
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

defineEmits(['close-position'])
</script>

