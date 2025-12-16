<script setup>
import Card from '../ui/Card.vue';

const props = defineProps({
  uptime: {
    type: Number,
    default: 99.9,
  },
  systemLoad: {
    type: Number,
    default: 45,
  },
});
</script>

<template>
  <Card title="Trạng thái hệ thống">
    <div class="space-y-4">
      <!-- System Uptime -->
      <div>
        <div class="flex items-center justify-between mb-2">
          <span class="text-white/80 text-sm">System Uptime</span>
          <span class="text-white font-semibold">{{ uptime }}%</span>
        </div>
        <div class="w-full bg-white/10 rounded-full h-2">
          <div
            :class="[
              'h-2 rounded-full transition-all',
              uptime >= 99 ? 'bg-green-500' : uptime >= 95 ? 'bg-yellow-500' : 'bg-red-500',
            ]"
            :style="{ width: `${uptime}%` }"
          ></div>
        </div>
      </div>

      <!-- System Load -->
      <div>
        <div class="flex items-center justify-between mb-2">
          <span class="text-white/80 text-sm">System Load</span>
          <span class="text-white font-semibold">{{ systemLoad }}%</span>
        </div>
        <div class="w-full bg-white/10 rounded-full h-2">
          <div
            :class="[
              'h-2 rounded-full transition-all',
              systemLoad < 50 ? 'bg-green-500' : systemLoad < 80 ? 'bg-yellow-500' : 'bg-red-500',
            ]"
            :style="{ width: `${systemLoad}%` }"
          ></div>
        </div>
      </div>
    </div>
  </Card>
</template>

