<template>
  <div class="p-4 bg-slate-800/50 border-t border-purple-500/20">
    <!-- File Preview -->
    <div v-if="selectedFiles.length > 0" class="mb-2 flex flex-wrap gap-2">
      <div
        v-for="(file, index) in selectedFiles"
        :key="index"
        class="relative inline-flex items-center space-x-2 bg-slate-700 rounded-lg p-2"
      >
        <i :class="getFileIcon(file.type)" class="text-purple-400"></i>
        <span class="text-sm text-white truncate max-w-[150px]">{{ file.name }}</span>
        <button
          @click="removeFile(index)"
          class="text-red-400 hover:text-red-300"
          aria-label="Xóa file"
        >
          <i class="fas fa-times text-xs"></i>
        </button>
      </div>
    </div>

    <div class="flex items-end space-x-2">
      <!-- Emoji Button -->
      <button
        @click="toggleEmojiPicker"
        class="w-10 h-10 flex items-center justify-center text-purple-400 hover:text-purple-300 hover:bg-slate-700 rounded-lg transition-all"
        aria-label="Chọn emoji"
      >
        <i class="fas fa-smile text-xl"></i>
      </button>

      <!-- Emoji Picker -->
      <div
        v-if="showEmojiPicker"
        class="absolute bottom-full left-4 mb-2 bg-slate-800 rounded-lg shadow-xl border border-purple-500/20 p-4 w-80 max-h-64 overflow-y-auto"
      >
        <div class="grid grid-cols-8 gap-2">
          <button
            v-for="emoji in commonEmojis"
            :key="emoji"
            @click="insertEmoji(emoji)"
            class="text-2xl hover:bg-slate-700 rounded p-1 transition-all"
            :title="emoji"
          >
            {{ emoji }}
          </button>
        </div>
      </div>

      <!-- Text Input -->
      <div class="flex-1 relative">
        <textarea
          v-model="message"
          ref="textareaRef"
          @input="handleInput"
          @keydown="handleKeyDown"
          @focus="handleFocus"
          @blur="handleBlur"
          rows="1"
          class="w-full px-4 py-2 bg-slate-700 border border-purple-500/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-purple-400 resize-none max-h-32 overflow-y-auto"
          placeholder="Nhập tin nhắn..."
        ></textarea>
      </div>

      <!-- File Upload Button -->
      <label class="w-10 h-10 flex items-center justify-center text-purple-400 hover:text-purple-300 hover:bg-slate-700 rounded-lg transition-all cursor-pointer">
        <input
          type="file"
          ref="fileInputRef"
          @change="handleFileSelect"
          multiple
          class="hidden"
          accept="image/*,video/*,audio/*,.pdf,.doc,.docx,.xls,.xlsx"
        />
        <i class="fas fa-paperclip text-xl"></i>
      </label>

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
import { ref, computed, watch, nextTick } from 'vue';

const emit = defineEmits(['send', 'typing']);

const message = ref('');
const selectedFiles = ref([]);
const showEmojiPicker = ref(false);
const textareaRef = ref(null);
const fileInputRef = ref(null);
const typingTimeout = ref(null);
const isTyping = ref(false);

const commonEmojis = [
  '😀', '😃', '😄', '😁', '😆', '😅', '😂', '🤣',
  '😊', '😇', '🙂', '🙃', '😉', '😌', '😍', '🥰',
  '😘', '😗', '😙', '😚', '😋', '😛', '😝', '😜',
  '🤪', '🤨', '🧐', '🤓', '😎', '🤩', '🥳', '😏',
  '😒', '😞', '😔', '😟', '😕', '🙁', '😣', '😖',
  '😫', '😩', '🥺', '😢', '😭', '😤', '😠', '😡',
  '👍', '👎', '👌', '✌️', '🤞', '🤟', '🤘', '👏',
  '🙌', '👐', '🤲', '🤝', '🙏', '💪', '❤️', '💯'
];

const canSend = computed(() => {
  return (message.value.trim().length > 0 || selectedFiles.value.length > 0);
});

const toggleEmojiPicker = () => {
  showEmojiPicker.value = !showEmojiPicker.value;
};

const insertEmoji = (emoji) => {
  const textarea = textareaRef.value;
  if (textarea) {
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    message.value = message.value.substring(0, start) + emoji + message.value.substring(end);
    nextTick(() => {
      textarea.focus();
      textarea.setSelectionRange(start + emoji.length, start + emoji.length);
    });
  }
  showEmojiPicker.value = false;
};

const handleFileSelect = (event) => {
  const files = Array.from(event.target.files);
  files.forEach(file => {
    if (file.size > 10 * 1024 * 1024) { // 10MB limit
      alert(`File ${file.name} quá lớn. Kích thước tối đa là 10MB.`);
      return;
    }
    selectedFiles.value.push(file);
  });
  // Reset input
  if (fileInputRef.value) {
    fileInputRef.value.value = '';
  }
};

const removeFile = (index) => {
  selectedFiles.value.splice(index, 1);
};

const getFileIcon = (fileType) => {
  if (!fileType) return 'fas fa-file';
  
  if (fileType.startsWith('image/')) return 'fas fa-image';
  if (fileType.startsWith('video/')) return 'fas fa-video';
  if (fileType.startsWith('audio/')) return 'fas fa-music';
  if (fileType.includes('pdf')) return 'fas fa-file-pdf';
  
  return 'fas fa-file';
};

const handleInput = () => {
  // Auto-resize textarea
  if (textareaRef.value) {
    textareaRef.value.style.height = 'auto';
    textareaRef.value.style.height = `${Math.min(textareaRef.value.scrollHeight, 128)}px`;
  }

  // Typing indicator
  if (!isTyping.value) {
    isTyping.value = true;
    emit('typing', true);
  }

  // Clear existing timeout
  if (typingTimeout.value) {
    clearTimeout(typingTimeout.value);
  }

  // Set new timeout to stop typing indicator
  typingTimeout.value = setTimeout(() => {
    isTyping.value = false;
    emit('typing', false);
    typingTimeout.value = null;
  }, 1000);
};

const handleKeyDown = (event) => {
  // Send on Enter (but allow Shift+Enter for new line)
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault();
    handleSend();
  }
  
  // Close emoji picker on Escape
  if (event.key === 'Escape' && showEmojiPicker.value) {
    showEmojiPicker.value = false;
  }
};

const handleFocus = () => {
  // Scroll to bottom when input is focused
  nextTick(() => {
    const container = textareaRef.value?.closest('.chat-window');
    if (container) {
      container.scrollTop = container.scrollHeight;
    }
  });
};

const handleBlur = () => {
  // Small delay to allow clicking emoji picker
  setTimeout(() => {
    showEmojiPicker.value = false;
  }, 200);
};

const handleSend = async () => {
  if (!canSend.value) return;

  const content = message.value.trim();
  const files = [...selectedFiles.value];

  // Emit send event
  emit('send', content, files);

  // Clear input
  message.value = '';
  selectedFiles.value = [];
  if (textareaRef.value) {
    textareaRef.value.style.height = 'auto';
  }

  // Stop typing indicator
  if (isTyping.value) {
    isTyping.value = false;
    emit('typing', false);
  }
  if (typingTimeout.value) {
    clearTimeout(typingTimeout.value);
    typingTimeout.value = null;
  }
};

// Close emoji picker when clicking outside
const handleClickOutside = (event) => {
  if (showEmojiPicker.value && !event.target.closest('.emoji-picker-container')) {
    showEmojiPicker.value = false;
  }
};

watch(showEmojiPicker, (isOpen) => {
  if (isOpen) {
    document.addEventListener('click', handleClickOutside);
  } else {
    document.removeEventListener('click', handleClickOutside);
  }
});
</script>

<style scoped>
/* Chat input styles */
</style>

