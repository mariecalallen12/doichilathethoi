<template>
  <div class="absolute bottom-24 right-0 w-96 h-[600px] bg-gradient-to-br from-slate-900 to-slate-800 rounded-xl shadow-2xl border border-purple-500/20 flex flex-col overflow-hidden">
    <!-- Header -->
    <div class="bg-gradient-to-r from-purple-600 to-indigo-600 p-4 flex items-center justify-between">
      <div class="flex items-center space-x-3">
        <div class="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
          <i class="fas fa-headset text-white"></i>
        </div>
        <div>
          <h3 class="text-white font-bold">Hỗ Trợ Trực Tuyến</h3>
          <p class="text-white/80 text-xs">
            <span v-if="isOnline" class="flex items-center">
              <span class="w-2 h-2 bg-green-400 rounded-full mr-1 animate-pulse"></span>
              Đang trực tuyến
            </span>
            <span v-else class="flex items-center">
              <span class="w-2 h-2 bg-gray-400 rounded-full mr-1"></span>
              Ngoại tuyến
            </span>
          </p>
        </div>
      </div>
      <button
        @click="$emit('close')"
        class="w-8 h-8 bg-white/20 hover:bg-white/30 rounded-full flex items-center justify-center text-white transition-all"
        aria-label="Đóng chat"
      >
        <i class="fas fa-times"></i>
      </button>
    </div>

    <!-- Messages Container -->
    <div
      ref="messagesContainer"
      class="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-900/50"
      @scroll="handleScroll"
    >
      <!-- Loading State -->
      <div v-if="chatStore.isLoading && messages.length === 0" class="flex items-center justify-center h-full">
        <div class="text-center">
          <div class="inline-block animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-purple-400 mb-2"></div>
          <p class="text-purple-200 text-sm">Đang tải tin nhắn...</p>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else-if="messages.length === 0" class="flex items-center justify-center h-full">
        <div class="text-center">
          <i class="fas fa-comments text-4xl text-purple-400/50 mb-4"></i>
          <p class="text-gray-400">Chưa có tin nhắn nào</p>
          <p class="text-gray-500 text-sm mt-2">Bắt đầu cuộc trò chuyện với chúng tôi!</p>
        </div>
      </div>

      <!-- Messages -->
      <ChatMessage
        v-for="message in messages"
        :key="message.id"
        :message="message"
      />
    </div>

    <!-- Typing Indicator -->
    <div v-if="isTyping" class="px-4 py-2 bg-slate-800/50 border-t border-purple-500/20">
      <div class="flex items-center space-x-2 text-gray-400 text-sm">
        <div class="flex space-x-1">
          <span class="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style="animation-delay: 0s"></span>
          <span class="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></span>
          <span class="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style="animation-delay: 0.4s"></span>
        </div>
        <span>Đang soạn tin nhắn...</span>
      </div>
    </div>

    <!-- Input -->
    <ChatInput
      @send="handleSend"
      @typing="handleTyping"
    />
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted } from 'vue';
import { useChatStore } from '../../stores/chat';
import ChatMessage from './ChatMessage.vue';
import ChatInput from './ChatInput.vue';

const emit = defineEmits(['close']);

const chatStore = useChatStore();
const messagesContainer = ref(null);
const isTyping = ref(false);

const messages = computed(() => chatStore.messages);
const isOnline = computed(() => chatStore.isConnected);

// Auto-scroll to bottom when new messages arrive
watch(messages, async () => {
  await nextTick();
  scrollToBottom();
}, { deep: true });

const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
  }
};

const handleScroll = () => {
  // Load more messages when scrolling to top
  if (messagesContainer.value && messagesContainer.value.scrollTop === 0) {
    chatStore.loadMoreMessages();
  }
};

const handleSend = async (content, files) => {
  await chatStore.sendMessage(content, files);
  await nextTick();
  scrollToBottom();
};

const handleTyping = (typing) => {
  isTyping.value = typing;
  chatStore.sendTypingIndicator(typing);
};

onMounted(() => {
  chatStore.loadMessages();
  scrollToBottom();
});
</script>

<style scoped>
/* Custom scrollbar */
:deep(.overflow-y-auto) {
  scrollbar-width: thin;
  scrollbar-color: rgba(139, 92, 246, 0.5) transparent;
}

:deep(.overflow-y-auto)::-webkit-scrollbar {
  width: 6px;
}

:deep(.overflow-y-auto)::-webkit-scrollbar-track {
  background: transparent;
}

:deep(.overflow-y-auto)::-webkit-scrollbar-thumb {
  background-color: rgba(139, 92, 246, 0.5);
  border-radius: 3px;
}

:deep(.overflow-y-auto)::-webkit-scrollbar-thumb:hover {
  background-color: rgba(139, 92, 246, 0.7);
}
</style>

