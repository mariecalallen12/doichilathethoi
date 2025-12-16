<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import Toast from './Toast.vue';
import toastService from '../../services/toast';

const toasts = ref([]);

const updateToasts = (newToasts) => {
  toasts.value = newToasts;
};

onMounted(() => {
  toastService.subscribe(updateToasts);
  if (toastService.toasts) {
    toasts.value = [...toastService.toasts];
  }
});

onUnmounted(() => {
  // Cleanup handled by service
});
</script>

<template>
  <div
    class="fixed top-4 right-4 z-50 flex flex-col gap-3 pointer-events-none"
  >
    <TransitionGroup name="toast-list">
      <div
        v-for="toast in toasts"
        :key="toast.id"
        class="pointer-events-auto"
      >
        <Toast :toast="toast" @close="toastService.removeToast(toast.id)" />
      </div>
    </TransitionGroup>
  </div>
</template>

<style scoped>
.toast-list-enter-active,
.toast-list-leave-active {
  transition: all 0.3s ease;
}

.toast-list-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.toast-list-leave-to {
  opacity: 0;
  transform: translateX(100%);
}

.toast-list-move {
  transition: transform 0.3s ease;
}
</style>

