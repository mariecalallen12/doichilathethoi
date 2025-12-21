<template>
  <div class="p-4 bg-slate-800/50 border-t border-purple-500/20">
    <div class="flex items-end space-x-2">
      <!-- Text Input -->
      <div class="flex-1 relative">
        <textarea
          v-model="message"
          ref="textareaRef"
          @input="handleInput"
          @keydown.enter.prevent="handleSend"
          rows="1"
          class="w-full px-4 py-2 bg-slate-700 border border-purple-500/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-purple-400 resize-none max-h-32 overflow-y-auto"
          placeholder="Nhập tin nhắn..."
        ></textarea>
      </div>

      <!-- Send Button -->
      <button
        @click="handleSend"
        :disabled="!canSend"
        class="w-10 h-10 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg flex items-center justify-center text-white transition-all"
        aria-label="Gửi tin nhắn"
      >
        <i class="fas fa-paper-plane"></i>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';

const emit = defineEmits(['send']);

const message = ref('');
const textareaRef = ref(null);

const canSend = computed(() => {
  return message.value.trim().length > 0;
});

const handleInput = () => {
  // Auto-resize textarea
  if (textareaRef.value) {
    textareaRef.value.style.height = 'auto';
    textareaRef.value.style.height = `${Math.min(textareaRef.value.scrollHeight, 128)}px`;
  }
};

const handleSend = async () => {
  if (!canSend.value) return;

  const content = message.value.trim();

  // Emit send event
  emit('send', content);

  // Clear input
  message.value = '';
  if (textareaRef.value) {
    textareaRef.value.style.height = 'auto';
  }
};
</script>

<style scoped>
/* Chat input styles */
</style>
