<template>
  <div class="h-full overflow-y-auto bg-gray-800 text-white">
    <div class="p-4 font-bold text-lg border-b border-gray-700">Conversations</div>
    <div v-if="chatStore.isLoading && chatStore.conversations.length === 0" class="p-4 text-center">Loading...</div>
    <div v-else-if="chatStore.error" class="p-4 text-center text-red-400">Error loading conversations.</div>
    <ul v-else-if="chatStore.sortedConversations.length > 0">
      <li 
        v-for="convo in chatStore.sortedConversations" 
        :key="convo.id"
        class="p-4 border-b border-gray-700 hover:bg-gray-700 cursor-pointer"
        :class="{ 'bg-blue-900/50': chatStore.activeConversation?.id === convo.id }"
        @click="chatStore.selectConversation(convo.id)"
      >
        <div class="flex justify-between">
          <span class="font-bold">User #{{ convo.user_id }}</span>
          <span class="text-xs text-gray-400">{{ new Date(convo.updated_at).toLocaleTimeString() }}</span>
        </div>
        <p class="text-sm text-gray-300 truncate">
          {{ convo.messages.length > 0 ? convo.messages[convo.messages.length - 1].content : 'No messages yet' }}
        </p>
      </li>
    </ul>
    <div v-else class="p-4 text-center text-gray-500">No conversations found.</div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useChatStore } from '../../store/chat';

const chatStore = useChatStore();

onMounted(() => {
  chatStore.fetchConversations();
});
</script>

<style scoped>
/* Scoped styles for ConversationList */
</style>
