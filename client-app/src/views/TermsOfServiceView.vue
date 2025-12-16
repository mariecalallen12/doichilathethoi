<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-900">
    <!-- Header -->
    <SupportHeader />
    
    <!-- Main Content -->
    <div class="container mx-auto px-4 sm:px-6 lg:px-8 py-8 max-w-4xl">
      <div class="mb-8">
        <h1 class="text-4xl font-bold text-transparent bg-gradient-to-r from-purple-300 via-violet-300 to-indigo-300 bg-clip-text mb-4">
          Điều Khoản Sử Dụng
        </h1>
        <div class="flex items-center space-x-4 text-sm text-gray-400">
          <span>Phiên bản: {{ terms?.version || '1.0' }}</span>
          <span v-if="terms?.effective_date">
            Có hiệu lực từ: {{ formatDate(terms.effective_date) }}
          </span>
        </div>
      </div>

      <!-- Version Selector -->
      <div v-if="versions.length > 1" class="mb-6">
        <select
          v-model="selectedVersion"
          @change="handleVersionChange"
          class="px-4 py-3 bg-slate-800/50 border border-purple-500/20 rounded-lg text-white focus:outline-none focus:border-purple-400"
        >
          <option v-for="version in versions" :key="version" :value="version">
            Phiên bản {{ version }}
          </option>
        </select>
      </div>

      <!-- Loading State -->
      <div v-if="legalStore.isLoading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-400"></div>
        <p class="text-purple-200 mt-4">Đang tải...</p>
      </div>

      <!-- Terms Content -->
      <div v-else class="bg-gradient-to-br from-slate-800/50 to-slate-900/50 rounded-xl p-8 border border-purple-500/20">
        <TermsContent :content="terms?.content || ''" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useLegalStore } from '../stores/legal';
import SupportHeader from '../components/support/SupportHeader.vue';
import TermsContent from '../components/legal/TermsContent.vue';

const legalStore = useLegalStore();
const selectedVersion = ref(null);
const versions = ref(['1.0']);

const terms = ref(null);

const handleVersionChange = () => {
  legalStore.fetchTerms(selectedVersion.value);
};

const formatDate = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleDateString('vi-VN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
};

onMounted(async () => {
  terms.value = await legalStore.fetchTerms();
  selectedVersion.value = terms.value?.version || '1.0';
});
</script>

<style scoped>
/* Terms page styles */
</style>

