<template>
  <div
    class="flex"
    :class="{
      'justify-end': message.sender_type === 'user',
      'justify-start': message.sender_type === 'admin'
    }"
  >
    <div
      class="max-w-[80%] rounded-lg px-4 py-2"
      :class="{
        'bg-gradient-to-r from-purple-600 to-indigo-600 text-white': message.sender_type === 'user',
        'bg-slate-700 text-gray-100': message.sender_type === 'admin'
      }"
    >
      <!-- Message Header -->
      <div v-if="message.sender_type === 'admin'" class="flex items-center space-x-2 mb-1">
        <span class="text-xs font-semibold text-purple-300">Hỗ trợ</span>
        <span class="text-xs text-gray-400">{{ formatTime(message.created_at) }}</span>
      </div>
      <div v-else class="flex items-center space-x-2 mb-1">
        <span class="text-xs font-semibold text-blue-300">Bạn</span>
        <span class="text-xs text-gray-400">{{ formatTime(message.created_at) }}</span>
      </div>

      <!-- Message Content -->
      <div class="text-sm whitespace-pre-wrap break-words">
        {{ message.content }}
      </div>

      <!-- Timestamp -->
      <div
        class="text-xs mt-1"
        :class="{
          'text-white/70': message.sender_type === 'user',
          'text-gray-400': message.sender_type === 'admin'
        }"
      >
        {{ formatTime(message.created_at) }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { format } from 'date-fns';
import { vi } from 'date-fns/locale';

const props = defineProps({
  message: {
    type: Object,
    required: true
  }
});

const formatTime = (timestamp) => {
  if (!timestamp) return '';
  const date = new Date(timestamp);
  const now = new Date();
  const diff = now - date;
  
  // If less than 1 minute ago
  if (diff < 60000) {
    return 'Vừa xong';
  }
  
  // If today
  if (date.toDateString() === now.toDateString()) {
    return format(date, 'HH:mm', { locale: vi });
  }
  
  // If yesterday
  const yesterday = new Date(now);
  yesterday.setDate(yesterday.getDate() - 1);
  if (date.toDateString() === yesterday.toDateString()) {
    return `Hôm qua ${format(date, 'HH:mm', { locale: vi })}`;
  }
  
  // Otherwise show date and time
  return format(date, 'dd/MM/yyyy HH:mm', { locale: vi });
};

// Removed getFileIcon and formatFileSize as file attachments are not yet supported
</script>

<style scoped>
/* Chat message styles */
</style>

