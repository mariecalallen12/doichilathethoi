<script setup>
defineProps({
  modelValue: [String, Number],
  type: {
    type: String,
    default: 'text',
  },
  placeholder: String,
  label: String,
  error: String,
  disabled: Boolean,
  icon: String,
});

const emit = defineEmits(['update:modelValue']);
</script>

<template>
  <div class="w-full">
    <label v-if="label" class="block text-sm font-medium text-white/80 mb-2">
      {{ label }}
    </label>
    <div class="relative">
      <i v-if="icon" :class="[icon, 'absolute left-4 top-1/2 -translate-y-1/2 text-white/60 text-sm']"></i>
      <input
        :type="type"
        :value="modelValue"
        :placeholder="placeholder"
        :disabled="disabled"
        :class="[
          'w-full px-4 py-3 rounded-lg bg-white/10 border border-white/20',
          'text-white placeholder-white/50',
          'focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/50',
          'transition-all disabled:opacity-50 disabled:cursor-not-allowed',
          icon && 'pl-12',
        ]"
        @input="emit('update:modelValue', $event.target.value)"
      />
    </div>
    <p v-if="error" class="mt-1 text-sm text-red-300">{{ error }}</p>
  </div>
</template>

