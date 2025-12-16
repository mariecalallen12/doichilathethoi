<template>
  <div class="space-y-2">
    <div v-if="adjustments.length === 0" class="text-gray-400 text-center py-8">
      No adjustments yet
    </div>
    
    <div
      v-for="adjustment in adjustments"
      :key="adjustment.id"
      class="bg-slate-700/50 rounded-lg p-4"
    >
      <div class="flex justify-between items-start mb-2">
        <div>
          <div class="text-white font-semibold">{{ adjustment.adjustment_type }}</div>
          <div class="text-gray-400 text-sm">
            User ID: {{ adjustment.user_id }} • {{ new Date(adjustment.created_at).toLocaleString() }}
          </div>
        </div>
      </div>
      
      <div class="text-sm text-gray-300 mt-2">
        <div>Previous: {{ adjustment.previous_value }}</div>
        <div>Target: {{ adjustment.target_value }}</div>
        <div v-if="adjustment.result" class="mt-1 text-purple-300">
          Result: {{ adjustment.result }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  adjustments: {
    type: Array,
    default: () => []
  }
})
</script>

