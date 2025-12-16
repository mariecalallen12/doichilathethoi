<script setup>
defineProps({
  title: String,
  subtitle: String,
  padding: {
    type: String,
    default: 'p-6',
  },
  hover: {
    type: Boolean,
    default: false,
  },
});
</script>

<template>
  <div
    :class="[
      'glass-effect rounded-xl shadow-glass',
      padding,
      hover && 'transition-transform hover:scale-[1.02] cursor-pointer',
    ]"
  >
    <div v-if="title || subtitle" class="mb-4">
      <h3 v-if="title" class="text-lg font-semibold text-white mb-1">
        {{ title }}
      </h3>
      <p v-if="subtitle" class="text-sm text-white/60">
        {{ subtitle }}
      </p>
    </div>
    <slot />
  </div>
</template>

<style scoped>
.glass-effect {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}
</style>

