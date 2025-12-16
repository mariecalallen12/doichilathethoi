<template>
  <div class="bg-gradient-to-br from-slate-800/50 to-slate-900/50 rounded-xl overflow-hidden border border-purple-500/20 animate-pulse">
    <!-- Thumbnail Skeleton -->
    <div class="h-48 bg-slate-700"></div>
    
    <!-- Content Skeleton -->
    <div class="p-4">
      <div class="h-5 bg-slate-700 rounded mb-2"></div>
      <div class="h-4 bg-slate-700 rounded mb-4 w-3/4"></div>
      
      <!-- Meta Skeleton -->
      <div class="flex items-center space-x-4">
        <div class="h-4 bg-slate-700 rounded w-20"></div>
        <div class="h-4 bg-slate-700 rounded w-16"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
// Skeleton card component for loading states
</script>

<style scoped>
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
</style>

