<template>
  <div class="mb-6">
    <div class="relative">
      <input
        v-model="query"
        type="text"
        placeholder="Tìm kiếm câu hỏi..."
        class="w-full px-6 py-4 bg-slate-800/50 border border-purple-500/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-purple-400 text-lg"
        @input="handleInput"
        @keyup.enter="handleSearch"
      />
      <button
        @click="handleSearch"
        class="absolute right-4 top-1/2 transform -translate-y-1/2 text-purple-400 hover:text-purple-300 transition-colors"
      >
        <i class="fas fa-search text-xl"></i>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const emit = defineEmits(['search']);

const query = ref('');

const handleInput = () => {
  emit('search', query.value);
};

const handleSearch = () => {
  emit('search', query.value);
};
</script>

<style scoped>
/* FAQ search styles */
</style>

