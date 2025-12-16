<template>
  <div class="market-container min-h-screen">
    <MarketHeader />
    <main class="container mx-auto px-4 py-8">
      <slot />
    </main>
  </div>
</template>

<script setup>
import MarketHeader from './MarketHeader.vue';
</script>

<style scoped>
/* Market styles are imported globally */
</style>

