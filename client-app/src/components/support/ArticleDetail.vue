<template>
  <div
    v-if="article"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm overflow-y-auto"
    @click.self="close"
  >
    <div class="relative w-full max-w-4xl mx-4 my-8 bg-slate-900 rounded-xl overflow-hidden border border-purple-500/20">
      <!-- Close Button -->
      <button
        @click="close"
        class="absolute top-4 right-4 z-10 w-10 h-10 bg-black/70 hover:bg-black/90 rounded-full flex items-center justify-center text-white transition-all"
      >
        <i class="fas fa-times"></i>
      </button>

      <!-- Content -->
      <div class="p-8">
        <!-- Header -->
        <div class="mb-6">
          <div class="flex items-center space-x-3 mb-4">
            <span class="px-3 py-1 bg-purple-500/20 text-purple-400 rounded text-sm">
              {{ getCategoryName(article.category) }}
            </span>
            <span v-if="article.views" class="text-gray-400 text-sm">
              <i class="fas fa-eye mr-1"></i>{{ formatNumber(article.views) }} lượt xem
            </span>
          </div>
          <h1 class="text-3xl font-bold text-white mb-4">{{ article.title }}</h1>
        </div>

        <!-- Article Content -->
        <div class="prose prose-invert max-w-none text-gray-300" v-html="article.content"></div>

        <!-- Related Articles -->
        <RelatedArticles v-if="article.related" :articles="article.related" />
      </div>
    </div>
  </div>
</template>

<script setup>
import RelatedArticles from './RelatedArticles.vue';

const props = defineProps({
  article: {
    type: Object,
    required: true
  }
});

const emit = defineEmits(['close']);

const close = () => {
  emit('close');
};

const getCategoryName = (categoryId) => {
  const names = {
    'getting-started': 'Bắt Đầu',
    'trading': 'Giao Dịch',
    'account': 'Tài Khoản',
    'deposit-withdraw': 'Nạp/Rút Tiền'
  };
  return names[categoryId] || categoryId;
};

const formatNumber = (num) => {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M';
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K';
  }
  return num.toString();
};
</script>

<style scoped>
/* Article detail styles */
</style>

