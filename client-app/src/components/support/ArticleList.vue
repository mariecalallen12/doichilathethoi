<template>
  <div class="space-y-4">
    <div
      v-for="article in articles"
      :key="article.id"
      class="bg-gradient-to-br from-slate-800/50 to-slate-900/50 rounded-xl p-6 border border-purple-500/20 hover:border-purple-400/40 transition-all cursor-pointer"
      @click="$emit('article-click', article)"
    >
      <div class="flex items-start justify-between">
        <div class="flex-1">
          <div class="flex items-center space-x-3 mb-2">
            <span class="px-2 py-1 bg-purple-500/20 text-purple-400 rounded text-xs">
              {{ getCategoryName(article.category) }}
            </span>
            <span v-if="article.views" class="text-gray-400 text-sm">
              <i class="fas fa-eye mr-1"></i>{{ formatNumber(article.views) }}
            </span>
          </div>
          <h3 class="text-xl font-bold text-white mb-2">{{ article.title }}</h3>
          <p class="text-gray-400 line-clamp-2">{{ article.excerpt || article.content }}</p>
        </div>
        <i class="fas fa-chevron-right text-purple-400 ml-4"></i>
      </div>
    </div>

    <div v-if="articles.length === 0" class="text-center py-12 text-gray-400">
      Không tìm thấy bài viết nào
    </div>
  </div>
</template>

<script setup>
defineProps({
  articles: {
    type: Array,
    default: () => []
  }
});

defineEmits(['article-click']);

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
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>

