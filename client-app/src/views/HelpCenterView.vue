<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-900">
    <!-- Header -->
    <SupportHeader />
    
    <!-- Main Content -->
    <div class="container mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="mb-8">
        <h1 class="text-4xl font-bold text-transparent bg-gradient-to-r from-purple-300 via-violet-300 to-indigo-300 bg-clip-text mb-4">
          Trung Tâm Trợ Giúp
        </h1>
        <p class="text-purple-200/80 text-lg">
          Tìm câu trả lời cho các câu hỏi của bạn
        </p>
      </div>

      <!-- Search Bar -->
      <SearchBar @search="handleSearch" />

      <!-- Category Filter -->
      <CategoryFilter @category-selected="handleCategorySelected" />

      <!-- Articles List -->
      <ArticleList :articles="supportStore.filteredArticles" @article-click="openArticle" />

      <!-- Article Detail Modal -->
      <ArticleDetail
        v-if="selectedArticle"
        :article="selectedArticle"
        @close="closeArticle"
      />
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue';
import { useSupportStore } from '../stores/support';
import SupportHeader from '../components/support/SupportHeader.vue';
import SearchBar from '../components/support/SearchBar.vue';
import CategoryFilter from '../components/support/CategoryFilter.vue';
import ArticleList from '../components/support/ArticleList.vue';
import ArticleDetail from '../components/support/ArticleDetail.vue';

const supportStore = useSupportStore();
const selectedArticle = ref(null);

const handleSearch = (query) => {
  supportStore.setSearchQuery(query);
  if (query) {
    supportStore.searchArticles(query);
  } else {
    supportStore.fetchArticles();
  }
};

const handleCategorySelected = (category) => {
  supportStore.setArticleCategory(category);
};

const openArticle = async (article) => {
  selectedArticle.value = await supportStore.fetchArticleById(article.id);
};

const closeArticle = () => {
  selectedArticle.value = null;
};

onMounted(() => {
  supportStore.fetchArticles();
  supportStore.fetchCategories();
});
</script>

<style scoped>
/* Help center styles */
</style>

