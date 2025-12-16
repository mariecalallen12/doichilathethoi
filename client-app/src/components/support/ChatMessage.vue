<template>
  <div
    class="flex"
    :class="{
      'justify-end': message.sender === 'user',
      'justify-start': message.sender === 'support'
    }"
  >
    <div
      class="max-w-[80%] rounded-lg px-4 py-2"
      :class="{
        'bg-gradient-to-r from-purple-600 to-indigo-600 text-white': message.sender === 'user',
        'bg-slate-700 text-gray-100': message.sender === 'support'
      }"
    >
      <!-- Message Header -->
      <div v-if="message.sender === 'support'" class="flex items-center space-x-2 mb-1">
        <span class="text-xs font-semibold text-purple-300">Hỗ trợ</span>
        <span class="text-xs text-gray-400">{{ formatTime(message.timestamp) }}</span>
      </div>

      <!-- Message Content -->
      <div class="text-sm whitespace-pre-wrap break-words">
        {{ message.content }}
      </div>

      <!-- Files -->
      <div v-if="message.files && message.files.length > 0" class="mt-2 space-y-2">
        <div
          v-for="file in message.files"
          :key="file.id || file.name"
          class="flex items-center space-x-2 p-2 bg-white/10 rounded"
        >
          <i :class="getFileIcon(file.type)" class="text-lg"></i>
          <a
            :href="file.url"
            target="_blank"
            class="text-sm hover:underline flex-1 truncate"
          >
            {{ file.name }}
          </a>
          <span class="text-xs text-gray-400">{{ formatFileSize(file.size) }}</span>
        </div>
      </div>

      <!-- Timestamp -->
      <div
        class="text-xs mt-1"
        :class="{
          'text-white/70': message.sender === 'user',
          'text-gray-400': message.sender === 'support'
        }"
      >
        {{ formatTime(message.timestamp) }}
      </div>

      <!-- Read Status (for user messages) -->
      <div v-if="message.sender === 'user'" class="flex justify-end mt-1">
        <i
          v-if="message.read"
          class="fas fa-check-double text-blue-300 text-xs"
          title="Đã đọc"
        ></i>
        <i
          v-else-if="message.delivered"
          class="fas fa-check text-gray-400 text-xs"
          title="Đã gửi"
        ></i>
        <i
          v-else
          class="fas fa-clock text-gray-500 text-xs"
          title="Đang gửi"
        ></i>
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

const getFileIcon = (fileType) => {
  if (!fileType) return 'fas fa-file';
  
  if (fileType.startsWith('image/')) return 'fas fa-image';
  if (fileType.startsWith('video/')) return 'fas fa-video';
  if (fileType.startsWith('audio/')) return 'fas fa-music';
  if (fileType.includes('pdf')) return 'fas fa-file-pdf';
  if (fileType.includes('word') || fileType.includes('document')) return 'fas fa-file-word';
  if (fileType.includes('excel') || fileType.includes('spreadsheet')) return 'fas fa-file-excel';
  
  return 'fas fa-file';
};

const formatFileSize = (bytes) => {
  if (!bytes) return '';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
};
</script>

<style scoped>
/* Chat message styles */
</style>

