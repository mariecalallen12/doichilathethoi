<script setup>
import { ref } from 'vue';
import Button from '../ui/Button.vue';

const props = defineProps({
  modelValue: {
    type: String,
    default: '7d',
  },
});

const emit = defineEmits(['update:modelValue']);

const ranges = [
  { value: '7d', label: '7 ngày' },
  { value: '30d', label: '30 ngày' },
  { value: '90d', label: '90 ngày' },
  { value: '1y', label: '1 năm' },
];

const selectedRange = ref(props.modelValue);

const selectRange = (range) => {
  selectedRange.value = range;
  emit('update:modelValue', range);
};
</script>

<template>
  <div class="flex items-center gap-2">
    <Button
      v-for="range in ranges"
      :key="range.value"
      :variant="selectedRange === range.value ? 'primary' : 'outline'"
      size="sm"
      @click="selectRange(range.value)"
    >
      {{ range.label }}
    </Button>
  </div>
</template>

