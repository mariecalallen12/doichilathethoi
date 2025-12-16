<script setup>
import { ref, computed, watch } from 'vue';

const props = defineProps({
  modelValue: {
    type: String,
    default: null,
  },
  label: {
    type: String,
    default: '',
  },
  placeholder: {
    type: String,
    default: 'Chọn ngày giờ',
  },
  disabled: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(['update:modelValue']);

// Convert ISO string to datetime-local format
const toDateTimeLocal = (isoString) => {
  if (!isoString) return '';
  try {
    const date = new Date(isoString);
    // Format: YYYY-MM-DDTHH:mm
    return date.toISOString().slice(0, 16);
  } catch {
    return '';
  }
};

// Convert datetime-local to ISO string
const toISOString = (dateTimeLocal) => {
  if (!dateTimeLocal) return null;
  try {
    return new Date(dateTimeLocal).toISOString();
  } catch {
    return null;
  }
};

const localValue = ref(toDateTimeLocal(props.modelValue));

watch(() => props.modelValue, (newVal) => {
  localValue.value = toDateTimeLocal(newVal);
});

const handleChange = (event) => {
  const value = event.target.value;
  localValue.value = value;
  emit('update:modelValue', toISOString(value));
};

const clearValue = () => {
  localValue.value = '';
  emit('update:modelValue', null);
};
</script>

<template>
  <div class="w-full">
    <label v-if="label" class="block text-sm text-white/80 mb-1.5">{{ label }}</label>
    <div class="relative">
      <input
        type="datetime-local"
        :value="localValue"
        :disabled="disabled"
        :placeholder="placeholder"
        @change="handleChange"
        class="w-full px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-white placeholder-white/40 
               focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-transparent
               disabled:opacity-50 disabled:cursor-not-allowed
               [&::-webkit-calendar-picker-indicator]:filter [&::-webkit-calendar-picker-indicator]:invert"
      />
      <button
        v-if="localValue && !disabled"
        type="button"
        @click="clearValue"
        class="absolute right-2 top-1/2 -translate-y-1/2 text-white/40 hover:text-white/80 transition-colors"
      >
        <i class="fas fa-times text-sm"></i>
      </button>
    </div>
  </div>
</template>
