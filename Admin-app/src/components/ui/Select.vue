<script setup>
const props = defineProps({
  modelValue: [String, Number],
  options: {
    type: Array,
    default: () => [],
  },
  placeholder: String,
  label: String,
  error: String,
  disabled: Boolean,
});

const emit = defineEmits(['update:modelValue']);
</script>

<template>
  <div class="w-full">
    <label v-if="label" class="block text-sm font-medium text-white/80 mb-2">
      {{ label }}
    </label>
    <select
      :value="modelValue"
      :disabled="disabled"
      :class="[
        'w-full px-4 py-3 rounded-lg bg-white/10 border border-white/20',
        'text-white',
        'focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/50',
        'transition-all disabled:opacity-50 disabled:cursor-not-allowed',
      ]"
      @change="emit('update:modelValue', $event.target.value)"
    >
      <option v-if="placeholder" value="" disabled class="bg-slate-800">
        {{ placeholder }}
      </option>
      <option
        v-for="option in options"
        :key="option.value"
        :value="option.value"
        class="bg-slate-800"
      >
        {{ option.label }}
      </option>
    </select>
    <p v-if="error" class="mt-1 text-sm text-red-300">{{ error }}</p>
  </div>
</template>

