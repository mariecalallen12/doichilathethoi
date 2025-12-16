import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { supportApi } from '../services/api/support';

export const useSupportStore = defineStore('support', () => {
  // State
  const articles = ref([]);
  const faqItems = ref([]);
  const categories = ref([]);
  const isLoading = ref(false);
  const error = ref(null);

  // Selected items
  const selectedArticle = ref(null);
  const selectedFaq = ref(null);

  // Filters
  const articleCategory = ref('all');
  const faqCategory = ref('all');
  const searchQuery = ref('');

  // Computed
  const filteredArticles = computed(() => {
    let result = articles.value;

    if (articleCategory.value !== 'all') {
      result = result.filter(a => a.category === articleCategory.value);
    }

    if (searchQuery.value) {
      const query = searchQuery.value.toLowerCase();
      result = result.filter(a => 
        a.title.toLowerCase().includes(query) ||
        a.content.toLowerCase().includes(query)
      );
    }

    return result;
  });

  const filteredFaqItems = computed(() => {
    let result = faqItems.value;

    if (faqCategory.value !== 'all') {
      result = result.filter(f => f.category === faqCategory.value);
    }

    if (searchQuery.value) {
      const query = searchQuery.value.toLowerCase();
      result = result.filter(f => 
        f.question.toLowerCase().includes(query) ||
        f.answer.toLowerCase().includes(query)
      );
    }

    return result;
  });

  // Actions
  async function fetchArticles() {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await supportApi.getArticles();
      articles.value = response.data || response;
    } catch (err) {
      error.value = err.message || 'Failed to fetch articles';
      console.error('Error fetching articles:', err);
      articles.value = getFallbackArticles();
    } finally {
      isLoading.value = false;
    }
  }

  async function fetchArticleById(id) {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await supportApi.getArticleById(id);
      selectedArticle.value = response.data || response;
      return selectedArticle.value;
    } catch (err) {
      error.value = err.message || 'Failed to fetch article';
      console.error('Error fetching article:', err);
      return null;
    } finally {
      isLoading.value = false;
    }
  }

  async function fetchCategories() {
    try {
      const response = await supportApi.getCategories();
      categories.value = response.data || response;
    } catch (err) {
      console.error('Error fetching categories:', err);
      categories.value = getFallbackCategories();
    }
  }

  async function searchArticles(query) {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await supportApi.searchArticles(query);
      articles.value = response.data || response;
    } catch (err) {
      error.value = err.message || 'Failed to search articles';
      console.error('Error searching articles:', err);
    } finally {
      isLoading.value = false;
    }
  }

  async function fetchFaq(category = null) {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await supportApi.getFaq(category);
      faqItems.value = response.data || response;
    } catch (err) {
      error.value = err.message || 'Failed to fetch FAQ';
      console.error('Error fetching FAQ:', err);
      faqItems.value = getFallbackFaq();
    } finally {
      isLoading.value = false;
    }
  }

  async function searchFaq(query) {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await supportApi.searchFaq(query);
      faqItems.value = response.data || response;
    } catch (err) {
      error.value = err.message || 'Failed to search FAQ';
      console.error('Error searching FAQ:', err);
    } finally {
      isLoading.value = false;
    }
  }

  async function submitContact(formData) {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await supportApi.submitContact(formData);
      return response;
    } catch (err) {
      error.value = err.message || 'Failed to submit contact form';
      console.error('Error submitting contact:', err);
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  function setArticleCategory(category) {
    articleCategory.value = category;
  }

  function setFaqCategory(category) {
    faqCategory.value = category;
  }

  function setSearchQuery(query) {
    searchQuery.value = query;
  }

  // Fallback data
  function getFallbackArticles() {
    return [
      {
        id: '1',
        title: 'Cách bắt đầu giao dịch',
        content: 'Hướng dẫn chi tiết về cách bắt đầu giao dịch...',
        category: 'getting-started',
        views: 1250
      }
    ];
  }

  function getFallbackCategories() {
    return [
      { id: 'getting-started', name: 'Bắt Đầu' },
      { id: 'trading', name: 'Giao Dịch' },
      { id: 'account', name: 'Tài Khoản' },
      { id: 'deposit-withdraw', name: 'Nạp/Rút Tiền' }
    ];
  }

  function getFallbackFaq() {
    return [
      {
        id: '1',
        question: 'Làm thế nào để đăng ký tài khoản?',
        answer: 'Bạn có thể đăng ký tài khoản bằng cách...',
        category: 'account'
      }
    ];
  }

  return {
    // State
    articles,
    faqItems,
    categories,
    isLoading,
    error,
    selectedArticle,
    selectedFaq,
    articleCategory,
    faqCategory,
    searchQuery,
    // Computed
    filteredArticles,
    filteredFaqItems,
    // Actions
    fetchArticles,
    fetchArticleById,
    fetchCategories,
    searchArticles,
    fetchFaq,
    searchFaq,
    submitContact,
    setArticleCategory,
    setFaqCategory,
    setSearchQuery
  };
});

