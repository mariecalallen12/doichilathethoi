<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-900">
    <!-- Header -->
    <SupportHeader />
    
    <!-- Main Content -->
    <div class="container mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="mb-8">
        <h1 class="text-4xl font-bold text-transparent bg-gradient-to-r from-purple-300 via-violet-300 to-indigo-300 bg-clip-text mb-4">
          Câu Hỏi Thường Gặp
        </h1>
        <p class="text-purple-200/80 text-lg">
          Tìm câu trả lời nhanh cho các câu hỏi phổ biến
        </p>
      </div>

      <!-- Search -->
      <FAQSearch @search="handleSearch" />

      <!-- Categories -->
      <FAQCategories @category-selected="handleCategorySelected" />

      <!-- FAQ List -->
      <FAQList :faq-items="supportStore.filteredFaqItems" />
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useSupportStore } from '../stores/support';
import SupportHeader from '../components/support/SupportHeader.vue';
import FAQSearch from '../components/support/FAQSearch.vue';
import FAQCategories from '../components/support/FAQCategories.vue';
import FAQList from '../components/support/FAQList.vue';

const supportStore = useSupportStore();

const handleSearch = (query) => {
  supportStore.setSearchQuery(query);
  if (query) {
    supportStore.searchFaq(query);
  } else {
    supportStore.fetchFaq();
  }
};

const handleCategorySelected = (category) => {
  supportStore.setFaqCategory(category);
  supportStore.fetchFaq(category === 'all' ? null : category);
};

onMounted(() => {
  supportStore.fetchFaq();
  supportStore.fetchCategories();
});
</script>

<style scoped>
/* FAQ page styles */
</style>

