<template>
  <section class="mb-6">
    <div class="market-card p-4">
      <div class="flex flex-col lg:flex-row gap-4 flex-wrap">
        <!-- Search Bar -->
        <div class="flex-1">
          <div class="relative">
            <i class="fas fa-search absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400"></i>
            <input
              v-model="searchQuery"
              @input="handleSearch"
              type="text"
              placeholder="Tìm kiếm tài sản..."
              class="market-search-input w-full pl-12 pr-4 py-3"
            />
          </div>
        </div>

        <!-- Timezone Filter -->
        <div class="lg:w-48">
          <select
            v-model="selectedTimezone"
            @change="handleFilterChange"
            class="market-search-input w-full px-4 py-3"
          >
            <option value="all">Tất cả múi giờ</option>
            <option value="UTC">UTC</option>
            <option value="EST">EST (New York)</option>
            <option value="GMT">GMT (London)</option>
            <option value="JST">JST (Tokyo)</option>
            <option value="CST">CST (Shanghai)</option>
          </select>
        </div>

        <!-- Volatility Filter -->
        <div class="lg:w-48">
          <select
            v-model="selectedVolatility"
            @change="handleFilterChange"
            class="market-search-input w-full px-4 py-3"
          >
            <option value="all">Tất cả volatility</option>
            <option value="low">Thấp (&lt; 1%)</option>
            <option value="medium">Trung bình (1-5%)</option>
            <option value="high">Cao (&gt; 5%)</option>
          </select>
        </div>

        <!-- Volume Filter -->
        <div class="lg:w-48">
          <select
            v-model="selectedVolume"
            @change="handleFilterChange"
            class="market-search-input w-full px-4 py-3"
          >
            <option value="all">Tất cả volume</option>
            <option value="low">Thấp</option>
            <option value="medium">Trung bình</option>
            <option value="high">Cao</option>
          </select>
        </div>

        <!-- Sort Options -->
        <div class="lg:w-48">
          <select
            v-model="sortBy"
            @change="handleSortChange"
            class="market-search-input w-full px-4 py-3"
          >
            <option value="price">Sắp xếp theo giá</option>
            <option value="change">Sắp xếp theo thay đổi</option>
            <option value="volume">Sắp xếp theo volume</option>
            <option value="symbol">Sắp xếp theo tên</option>
          </select>
        </div>

        <!-- Sort Order Toggle -->
        <button
          @click="toggleSortOrder"
          class="px-4 py-3 bg-purple-500/20 hover:bg-purple-500/30 rounded-lg text-purple-300 transition-colors"
          :title="sortOrder === 'asc' ? 'Tăng dần' : 'Giảm dần'"
        >
          <i :class="sortOrder === 'asc' ? 'fas fa-sort-amount-up' : 'fas fa-sort-amount-down'"></i>
        </button>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, watch } from 'vue';
import { useMarketStore } from '../../stores/market';

const marketStore = useMarketStore();
const searchQuery = ref('');
const selectedTimezone = ref('all');
const selectedVolatility = ref('all');
const selectedVolume = ref('all');
const sortBy = ref('price');
const sortOrder = ref('desc');

const handleSearch = () => {
  marketStore.setSearchQuery(searchQuery.value);
};

const handleFilterChange = () => {
  // Filter logic can be extended here
  console.log('Filters changed:', {
    timezone: selectedTimezone.value,
    volatility: selectedVolatility.value,
    volume: selectedVolume.value,
  });
};

const handleSortChange = () => {
  marketStore.setSort(sortBy.value, sortOrder.value);
};

const toggleSortOrder = () => {
  sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc';
  marketStore.setSort(sortBy.value, sortOrder.value);
};

watch(() => marketStore.searchQuery, (newQuery) => {
  searchQuery.value = newQuery;
});

watch(() => marketStore.sortBy, (newSort) => {
  sortBy.value = newSort;
});

watch(() => marketStore.sortOrder, (newOrder) => {
  sortOrder.value = newOrder;
});
</script>

