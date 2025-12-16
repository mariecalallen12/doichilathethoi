<template>
  <section id="ebooks" class="mb-12">
    <div class="mb-6">
      <h2 class="text-3xl font-bold text-white mb-2">Ebook Strategies</h2>
      <p class="text-purple-200/80">Chiến lược giao dịch từ chuyên gia</p>
    </div>

    <!-- Search and Filter -->
    <div class="mb-6 flex flex-col md:flex-row gap-4">
      <div class="flex-1">
        <div class="relative">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Tìm kiếm ebook..."
            class="w-full px-4 py-3 bg-slate-800/50 border border-purple-500/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-purple-400"
            @input="handleSearch"
          />
          <i class="fas fa-search absolute right-4 top-1/2 transform -translate-y-1/2 text-purple-400"></i>
        </div>
      </div>
      <select
        v-model="selectedCategory"
        @change="handleCategoryChange"
        class="px-4 py-3 bg-slate-800/50 border border-purple-500/20 rounded-lg text-white focus:outline-none focus:border-purple-400"
      >
        <option value="all">Tất cả danh mục</option>
        <option value="trading">Trading</option>
        <option value="forex">Forex</option>
        <option value="crypto">Cryptocurrency</option>
        <option value="strategy">Chiến lược</option>
        <option value="analysis">Phân tích</option>
      </select>
    </div>

    <!-- Loading State with Skeleton -->
    <div v-if="educationStore.isLoading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <SkeletonCard v-for="n in 6" :key="n" />
    </div>

    <!-- Empty State -->
    <div v-else-if="educationStore.filteredEbooks.length === 0" class="text-center py-12">
      <div class="max-w-md mx-auto">
        <i class="fas fa-book text-6xl text-purple-400/50 mb-4"></i>
        <h3 class="text-xl font-bold text-white mb-2">Không tìm thấy ebook</h3>
        <p class="text-gray-400 mb-4">
          {{ searchQuery ? 'Thử tìm kiếm với từ khóa khác' : 'Chưa có ebook nào trong danh mục này' }}
        </p>
        <button
          v-if="searchQuery"
          @click="clearSearch"
          class="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-all"
        >
          Xóa bộ lọc
        </button>
      </div>
    </div>

    <!-- Ebook Grid -->
    <TransitionGroup
      v-else
      name="ebook-grid"
      tag="div"
      class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
    >
      <CourseCard
        v-for="ebook in educationStore.filteredEbooks"
        :key="ebook.id"
        :course="ebook"
        type="ebook"
        @click="openEbook(ebook)"
      />
    </TransitionGroup>

    <!-- Ebook Viewer Modal -->
    <EbookViewer
      v-if="selectedEbook"
      :ebook="selectedEbook"
      @close="closeEbook"
    />
  </section>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useEducationStore } from '../../stores/education';
import CourseCard from './CourseCard.vue';
import EbookViewer from './EbookViewer.vue';
import SkeletonCard from './SkeletonCard.vue';
import { debounce } from 'lodash-es';

const educationStore = useEducationStore();
const searchQuery = ref('');
const selectedCategory = ref('all');
const selectedEbook = ref(null);

// Debounced search to improve performance
const debouncedSearch = debounce(() => {
  educationStore.setSearchQuery(searchQuery.value);
}, 300);

const handleSearch = () => {
  debouncedSearch();
};

const handleCategoryChange = () => {
  educationStore.setEbookCategory(selectedCategory.value);
};

const clearSearch = () => {
  searchQuery.value = '';
  educationStore.setSearchQuery('');
  educationStore.setEbookCategory('all');
  selectedCategory.value = 'all';
};

const openEbook = async (ebook) => {
  selectedEbook.value = ebook;
  // Update progress when ebook is opened
  if (ebook.id) {
    try {
      await educationStore.updateProgress(ebook.id, 'ebook', {
        last_opened: new Date().toISOString(),
        status: 'in_progress'
      });
    } catch (error) {
      console.error('Error updating progress:', error);
    }
  }
};

const closeEbook = () => {
  selectedEbook.value = null;
};

watch(() => educationStore.ebookCategory, (newCategory) => {
  selectedCategory.value = newCategory;
});

onMounted(() => {
  educationStore.fetchEbooks();
});
</script>

<style scoped>
/* Ebook section specific styles */
.ebook-grid-enter-active,
.ebook-grid-leave-active {
  transition: all 0.3s ease;
}

.ebook-grid-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.ebook-grid-leave-to {
  opacity: 0;
  transform: scale(0.9);
}

.ebook-grid-move {
  transition: transform 0.3s ease;
}
</style>

