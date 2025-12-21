<template>
  <div class="flex flex-col h-full bg-gray-800 text-white">
    <template v-if="activeConversation">
      <!-- Header -->
      <div class="p-4 border-b border-gray-700">
        <h2 class="text-xl font-bold">Chat with {{ activeConversation.user?.name || 'User' }}</h2>
      </div>

      <!-- Message Display Area -->
      <div class="flex-1 p-4 overflow-y-auto bg-gray-900/50" ref="messageContainer">
        <div 
          v-for="message in activeConversation.messages" 
          :key="message.id" 
          class="flex mb-4"
          :class="message.sender_type === 'admin' ? 'justify-end' : 'justify-start'"
        >
          <div 
            class="rounded-lg p-3 max-w-lg"
            :class="message.sender_type === 'admin' ? 'bg-blue-600' : 'bg-gray-700'"
          >
            <p class="text-white">{{ message.content }}</p>
            <span 
              class="text-xs mt-1 block text-right"
              :class="message.sender_type === 'admin' ? 'text-blue-200' : 'text-gray-400'"
            >
              {{ new Date(message.created_at).toLocaleTimeString() }}
            </span>
          </div>
        </div>
      </div>

      <!-- Message Input Area -->
      <div class="p-4 bg-gray-800">
        <form @submit.prevent="handleSendMessage" class="flex">
          <input
            v-model="newMessage"
            type="text"
            placeholder="Type your message..."
            class="flex-1 p-2 rounded-l-lg bg-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button type="submit" class="bg-blue-600 text-white px-4 py-2 rounded-r-lg hover:bg-blue-700">
            Send
          </button>
        </form>
      </div>
    </template>
    <div v-else class="flex items-center justify-center h-full text-gray-500">
      <p>Select a conversation to start chatting.</p>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch, nextTick } from 'vue';
import { useChatStore } from '../../store/chat';

const chatStore = useChatStore();
const newMessage = ref('');
const messageContainer = ref(null);

const activeConversation = computed(() => chatStore.activeConversation);

const handleSendMessage = () => {
  if (newMessage.value.trim() === '') return;
  chatStore.sendMessage(newMessage.value);
  newMessage.value = '';
};

// Auto-scroll to the bottom when new messages are added
watch(() => activeConversation.value?.messages, async () => {
  await nextTick();
  if (messageContainer.value) {
    messageContainer.value.scrollTop = messageContainer.value.scrollHeight;
  }
}, { deep: true });
</script>

<style scoped>
/* Scoped styles for ChatWindow */
</style>
