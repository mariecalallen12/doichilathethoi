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
        v-if="clientChatStore.isChatOpen"
        @close="clientChatStore.setChatOpen(false)"
      />
    </Transition>

    <!-- Floating Button -->
    <button
      @click="clientChatStore.setChatOpen(!clientChatStore.isChatOpen)"
      class="w-16 h-16 bg-gradient-to-r from-purple-600 to-indigo-600 rounded-full shadow-lg hover:shadow-xl transition-all transform hover:scale-110 flex items-center justify-center text-white relative"
      :class="{ 'rotate-180': clientChatStore.isChatOpen }"
      aria-label="Mở chat hỗ trợ"
    >
      <i v-if="!clientChatStore.isChatOpen" class="fas fa-comments text-2xl"></i>
      <i v-else class="fas fa-times text-2xl"></i>
      
      <!-- Unread Badge -->
      <span
        v-if="clientChatStore.unreadCount > 0 && !clientChatStore.isChatOpen"
        class="absolute -top-1 -right-1 bg-red-500 text-white text-xs font-bold rounded-full w-6 h-6 flex items-center justify-center animate-pulse"
      >
        {{ clientChatStore.unreadCount > 9 ? '9+' : clientChatStore.unreadCount }}
      </span>
    </button>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue';
import { useClientChatStore } from '../../stores/chat'; // Use the specific client chat store
import ChatWindow from './ChatWindow.vue';

const clientChatStore = useClientChatStore();

// Handle keyboard shortcut (Ctrl/Cmd + /)
const handleKeyDown = (event) => {
  if ((event.ctrlKey || event.metaKey) && event.key === '/') {
    event.preventDefault();
    clientChatStore.setChatOpen(!clientChatStore.isChatOpen);
  }
};

onMounted(() => {
  document.addEventListener('keydown', handleKeyDown);
  // Fetch or create conversation and connect WebSocket on mount
  clientChatStore.fetchOrCreateConversation();
});

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeyDown);
  clientChatStore.disconnectWebSocket(); // Disconnect when component is unmounted
});
</script>

<style scoped>
/* Chat widget styles */
</style>
