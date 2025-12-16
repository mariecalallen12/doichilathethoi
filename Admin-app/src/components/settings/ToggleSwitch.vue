<script setup>
const props = defineProps({
  modelValue: Boolean,
  label: String,
  description: String,
});

const emit = defineEmits(['update:modelValue']);
</script>

<template>
  <div class="flex items-center justify-between py-3">
    <div class="flex-1">
      <label class="text-white font-medium">{{ label }}</label>
      <p v-if="description" class="text-white/60 text-sm mt-1">{{ description }}</p>
    </div>
    <button
      :class="[
        'relative inline-flex h-6 w-11 items-center rounded-full transition-colors',
        modelValue ? 'bg-primary' : 'bg-white/20',
      ]"
      @click="emit('update:modelValue', !modelValue)"
    >
      <span
        :class="[
          'inline-block h-4 w-4 transform rounded-full bg-white transition-transform',
          modelValue ? 'translate-x-6' : 'translate-x-1',
        ]"
      ></span>
    </button>
  </div>
</template>

