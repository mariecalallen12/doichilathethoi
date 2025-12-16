<template>
  <section id="reports" class="mb-12">
    <div class="mb-6">
      <h2 class="text-3xl font-bold text-white mb-2">Phân Tích Thị Trường</h2>
      <p class="text-purple-200/80">Báo cáo chuyên sâu hàng ngày</p>
    </div>

    <!-- Search and Filter -->
    <div class="mb-6 flex flex-col md:flex-row gap-4">
      <div class="flex-1">
        <div class="relative">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Tìm kiếm báo cáo..."
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
        <option value="daily">Hàng ngày</option>
        <option value="weekly">Hàng tuần</option>
        <option value="monthly">Hàng tháng</option>
        <option value="forex">Forex</option>
        <option value="crypto">Cryptocurrency</option>
        <option value="commodities">Hàng hóa</option>
      </select>
    </div>

    <!-- Loading State with Skeleton -->
    <div v-if="educationStore.isLoading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <SkeletonCard v-for="n in 6" :key="n" />
    </div>

    <!-- Empty State -->
    <div v-else-if="educationStore.filteredReports.length === 0" class="text-center py-12">
      <div class="max-w-md mx-auto">
        <i class="fas fa-chart-line text-6xl text-purple-400/50 mb-4"></i>
        <h3 class="text-xl font-bold text-white mb-2">Không tìm thấy báo cáo</h3>
        <p class="text-gray-400 mb-4">
          {{ searchQuery ? 'Thử tìm kiếm với từ khóa khác' : 'Chưa có báo cáo nào trong danh mục này' }}
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

    <!-- Reports Grid -->
    <TransitionGroup
      v-else
      name="report-grid"
      tag="div"
      class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
    >
      <div
        v-for="report in educationStore.filteredReports"
        :key="report.id"
        class="bg-gradient-to-br from-slate-800/50 to-slate-900/50 rounded-xl overflow-hidden border border-purple-500/20 hover:border-purple-400/40 transition-all cursor-pointer transform hover:scale-105"
        @click="openReport(report)"
      >
        <!-- Thumbnail -->
        <div class="relative h-48 bg-gradient-to-br from-purple-600/20 to-indigo-600/20">
          <img
            v-if="report.thumbnail"
            :src="report.thumbnail"
            :alt="report.title"
            class="w-full h-full object-cover"
          />
          <div v-else class="w-full h-full flex items-center justify-center">
            <i class="fas fa-chart-line text-4xl text-purple-400/50"></i>
          </div>
          <div class="absolute top-2 left-2 px-2 py-1 bg-purple-600/80 rounded text-xs text-white font-semibold">
            {{ getCategoryLabel(report.category) }}
          </div>
        </div>

        <!-- Content -->
        <div class="p-4">
          <h3 class="text-white font-bold text-lg mb-2 line-clamp-2">{{ report.title }}</h3>
          <p class="text-gray-400 text-sm mb-4 line-clamp-2">{{ report.description }}</p>
          
          <!-- Meta Info -->
          <div class="flex items-center justify-between text-sm text-gray-500">
            <span>{{ formatDate(report.date) }}</span>
            <button
              @click.stop="downloadReport(report)"
              class="text-purple-400 hover:text-purple-300 transition-colors"
            >
              <i class="fas fa-download mr-1"></i>Tải xuống
            </button>
          </div>
        </div>
      </div>
    </TransitionGroup>

    <!-- Report Detail Modal -->
    <ReportDetailModal
      v-if="selectedReport"
      :report="selectedReport"
      @close="closeReport"
    />
  </section>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useEducationStore } from '../../stores/education';
import ReportDetailModal from './ReportDetailModal.vue';
import SkeletonCard from './SkeletonCard.vue';
import { debounce } from 'lodash-es';

const educationStore = useEducationStore();
const searchQuery = ref('');
const selectedCategory = ref('all');
const selectedReport = ref(null);

// Debounced search to improve performance
const debouncedSearch = debounce(() => {
  educationStore.setSearchQuery(searchQuery.value);
}, 300);

const handleSearch = () => {
  debouncedSearch();
};

const handleCategoryChange = () => {
  educationStore.setReportCategory(selectedCategory.value);
};

const clearSearch = () => {
  searchQuery.value = '';
  educationStore.setSearchQuery('');
  educationStore.setReportCategory('all');
  selectedCategory.value = 'all';
};

const openReport = async (report) => {
  selectedReport.value = report;
  // Update progress when report is opened
  if (report.id) {
    try {
      await educationStore.updateProgress(report.id, 'report', {
        last_opened: new Date().toISOString(),
        status: 'viewed'
      });
    } catch (error) {
      console.error('Error updating progress:', error);
    }
  }
};

const closeReport = () => {
  selectedReport.value = null;
};

const downloadReport = (report) => {
  if (report.fileUrl) {
    const link = document.createElement('a');
    link.href = report.fileUrl;
    link.download = `${report.title}.pdf`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }
};

const formatDate = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleDateString('vi-VN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });
};

const getCategoryLabel = (category) => {
  const labels = {
    daily: 'Hàng ngày',
    weekly: 'Hàng tuần',
    monthly: 'Hàng tháng',
    forex: 'Forex',
    crypto: 'Cryptocurrency',
    commodities: 'Hàng hóa'
  };
  return labels[category] || category;
};

watch(() => educationStore.reportCategory, (newCategory) => {
  selectedCategory.value = newCategory;
});

onMounted(() => {
  educationStore.fetchReports();
});
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.report-grid-enter-active,
.report-grid-leave-active {
  transition: all 0.3s ease;
}

.report-grid-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.report-grid-leave-to {
  opacity: 0;
  transform: scale(0.9);
}

.report-grid-move {
  transition: transform 0.3s ease;
}
</style>

