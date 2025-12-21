<template>
  <div class="p-4 h-full">
    <h1 class="text-2xl font-bold mb-4 text-white">Customer Support Chat</h1>
    <div class="flex h-[calc(100vh-100px)] bg-gray-800 rounded-lg shadow-lg">
      <!-- Conversation List -->
      <div class="w-1/3 border-r border-gray-700">
        <ConversationList />
      </div>

      <!-- Chat Window -->
      <div class="w-2/3 flex flex-col">
        <ChatWindow />
      </div>
    </div>
  </div>
</template>

<script setup>
import ConversationList from '../components/chat/ConversationList.vue';
import ChatWindow from '../components/chat/ChatWindow.vue';
</script>

<style scoped>
/* Scoped styles for ChatView */
</style>
