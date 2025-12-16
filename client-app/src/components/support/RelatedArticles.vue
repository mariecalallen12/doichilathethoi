<template>
  <div v-if="articles && articles.length > 0" class="mt-8 pt-8 border-t border-purple-500/20">
    <h3 class="text-xl font-bold text-white mb-4">Bài viết liên quan</h3>
    <div class="space-y-3">
      <router-link
        v-for="article in articles"
        :key="article.id"
        :to="`/help/article/${article.id}`"
        class="block p-4 bg-slate-800/50 rounded-lg hover:bg-slate-800 transition-all"
      >
        <h4 class="text-white font-semibold mb-1">{{ article.title }}</h4>
        <p class="text-gray-400 text-sm line-clamp-1">{{ article.excerpt }}</p>
      </router-link>
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
</script>

<style scoped>
.line-clamp-1 {
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>

