<template>
  <div class="fixed bottom-6 right-6 z-50">
    <!-- Chat Window -->
    <Transition
      enter-active-class="transition-all duration-300 ease-out"
      enter-from-class="opacity-0 translate-y-4 scale-95"
      enter-to-class="opacity-100 translate-y-0 scale-100"
      leave-active-class="transition-all duration-200 ease-in"
      leave-from-class="opacity-100 translate-y-0 scale-100"
      leave-to-class="opacity-0 translate-y-4 scale-95"
    >
      <ChatWindow
        v-if="isOpen"
        @close="closeChat"
      />
    </Transition>

    <!-- Floating Button -->
    <button
      @click="toggleChat"
      class="w-16 h-16 bg-gradient-to-r from-purple-600 to-indigo-600 rounded-full shadow-lg hover:shadow-xl transition-all transform hover:scale-110 flex items-center justify-center text-white relative"
      :class="{ 'rotate-180': isOpen }"
      aria-label="Mở chat hỗ trợ"
    >
      <i v-if="!isOpen" class="fas fa-comments text-2xl"></i>
      <i v-else class="fas fa-times text-2xl"></i>
      
      <!-- Unread Badge -->
      <span
        v-if="unreadCount > 0 && !isOpen"
        class="absolute -top-1 -right-1 bg-red-500 text-white text-xs font-bold rounded-full w-6 h-6 flex items-center justify-center animate-pulse"
      >
        {{ unreadCount > 9 ? '9+' : unreadCount }}
      </span>
    </button>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useChatStore } from '../../stores/chat';
import ChatWindow from './ChatWindow.vue';

const chatStore = useChatStore();
const isOpen = ref(false);

const unreadCount = computed(() => chatStore.unreadCount);

const toggleChat = () => {
  isOpen.value = !isOpen.value;
  if (isOpen.value) {
    chatStore.markAsRead();
    chatStore.connect();
  } else {
    // Keep connection but mark as read
    chatStore.markAsRead();
  }
};

const closeChat = () => {
  isOpen.value = false;
  chatStore.markAsRead();
};

// Handle keyboard shortcut (Ctrl/Cmd + /)
const handleKeyDown = (event) => {
  if ((event.ctrlKey || event.metaKey) && event.key === '/') {
    event.preventDefault();
    toggleChat();
  }
};

onMounted(() => {
  document.addEventListener('keydown', handleKeyDown);
  // Connect to chat on mount
  chatStore.connect();
});

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeyDown);
});
</script>

<style scoped>
/* Chat widget styles */
</style>

