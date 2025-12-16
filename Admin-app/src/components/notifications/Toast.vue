<script setup>
import { onMounted } from 'vue';

const props = defineProps({
  toast: {
    type: Object,
    required: true,
  },
});

const emit = defineEmits(['close']);

const typeIcons = {
  success: 'fa-check-circle',
  error: 'fa-exclamation-circle',
  warning: 'fa-exclamation-triangle',
  info: 'fa-info-circle',
};

const typeColors = {
  success: 'bg-green-500/20 border-green-500/30 text-green-300',
  error: 'bg-red-500/20 border-red-500/30 text-red-300',
  warning: 'bg-yellow-500/20 border-yellow-500/30 text-yellow-300',
  info: 'bg-blue-500/20 border-blue-500/30 text-blue-300',
};

onMounted(() => {
  if (props.toast.duration > 0) {
    setTimeout(() => {
      emit('close');
    }, props.toast.duration);
  }
});
</script>

<template>
  <div
    :class="[
      'glass-effect rounded-lg border p-4 shadow-lg min-w-[300px] max-w-md',
      'flex items-start gap-3 animate-slide-in',
      typeColors[toast.type] || typeColors.info,
    ]"
  >
    <i
      :class="[
        'fas text-xl flex-shrink-0 mt-0.5',
        typeIcons[toast.type] || typeIcons.info,
      ]"
    ></i>
    <div class="flex-1">
      <p class="text-sm font-medium">{{ toast.message }}</p>
    </div>
    <button
      @click="emit('close')"
      class="text-white/60 hover:text-white transition-colors flex-shrink-0"
    >
      <i class="fas fa-times text-sm"></i>
    </button>
  </div>
</template>

<style scoped>
.glass-effect {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

@keyframes slide-in {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.animate-slide-in {
  animation: slide-in 0.3s ease-out;
}
</style>

