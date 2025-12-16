<template>
  <section id="signals" class="mb-12">
    <div class="mb-6">
      <h2 class="text-3xl font-bold text-white mb-2">Tín Hiệu Giao Dịch</h2>
      <p class="text-purple-200/80">Tín hiệu AI và chuyên gia</p>
    </div>

    <!-- Filters -->
    <div class="mb-6 flex flex-col md:flex-row gap-4">
      <select
        v-model="selectedSignalType"
        @change="handleSignalTypeChange"
        class="px-4 py-3 bg-slate-800/50 border border-purple-500/20 rounded-lg text-white focus:outline-none focus:border-purple-400"
      >
        <option value="all">Tất cả loại</option>
        <option value="buy">Mua</option>
        <option value="sell">Bán</option>
        <option value="hold">Giữ</option>
      </select>
      <select
        v-model="selectedSource"
        @change="handleSourceChange"
        class="px-4 py-3 bg-slate-800/50 border border-purple-500/20 rounded-lg text-white focus:outline-none focus:border-purple-400"
      >
        <option value="all">Tất cả nguồn</option>
        <option value="ai">AI</option>
        <option value="expert">Chuyên gia</option>
      </select>
    </div>

    <!-- Loading State -->
    <div v-if="analysisStore.isLoading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-400"></div>
      <p class="text-purple-200 mt-4">Đang tải tín hiệu...</p>
    </div>

    <!-- Signals List -->
    <div v-else class="space-y-4">
      <div
        v-for="signal in analysisStore.filteredSignals"
        :key="signal.id"
        class="bg-gradient-to-br from-slate-800/50 to-slate-900/50 rounded-xl p-6 border border-purple-500/20 hover:border-purple-400/40 transition-all"
      >
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <div class="flex items-center space-x-3 mb-3">
              <span
                class="px-3 py-1 rounded text-sm font-semibold"
                :class="getSignalTypeClass(signal.type)"
              >
                {{ getSignalTypeLabel(signal.type) }}
              </span>
              <span class="text-white font-bold text-lg">{{ signal.symbol }}</span>
              <span
                class="px-2 py-1 rounded text-xs"
                :class="getStrengthClass(signal.strength)"
              >
                {{ getStrengthLabel(signal.strength) }}
              </span>
              <span class="text-gray-400 text-sm">
                <i :class="signal.source === 'ai' ? 'fas fa-robot' : 'fas fa-user-tie'" class="mr-1"></i>
                {{ signal.source === 'ai' ? 'AI' : 'Chuyên gia' }}
              </span>
            </div>
            
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
              <div>
                <div class="text-xs text-gray-400 mb-1">Giá hiện tại</div>
                <div class="text-white font-semibold">{{ signal.price }}</div>
              </div>
              <div>
                <div class="text-xs text-gray-400 mb-1">Mục tiêu</div>
                <div class="text-green-400 font-semibold">{{ signal.target }}</div>
              </div>
              <div>
                <div class="text-xs text-gray-400 mb-1">Cắt lỗ</div>
                <div class="text-red-400 font-semibold">{{ signal.stop_loss }}</div>
              </div>
              <div>
                <div class="text-xs text-gray-400 mb-1">Thời gian</div>
                <div class="text-gray-300 text-sm">{{ formatDate(signal.created_at) }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="analysisStore.filteredSignals.length === 0" class="text-center py-12 text-gray-400">
        Không có tín hiệu nào
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useAnalysisStore } from '../../stores/analysis';

const analysisStore = useAnalysisStore();
const selectedSignalType = ref('all');
const selectedSource = ref('all');

const handleSignalTypeChange = () => {
  analysisStore.setSignalType(selectedSignalType.value);
};

const handleSourceChange = () => {
  // Filter by source
  // This would be implemented in the store
};

const getSignalTypeClass = (type) => {
  const classes = {
    buy: 'bg-green-500/20 text-green-400',
    sell: 'bg-red-500/20 text-red-400',
    hold: 'bg-yellow-500/20 text-yellow-400'
  };
  return classes[type] || 'bg-gray-500/20 text-gray-400';
};

const getSignalTypeLabel = (type) => {
  const labels = {
    buy: 'MUA',
    sell: 'BÁN',
    hold: 'GIỮ'
  };
  return labels[type] || type;
};

const getStrengthClass = (strength) => {
  const classes = {
    strong: 'bg-purple-500/20 text-purple-400',
    medium: 'bg-blue-500/20 text-blue-400',
    weak: 'bg-gray-500/20 text-gray-400'
  };
  return classes[strength] || 'bg-gray-500/20 text-gray-400';
};

const getStrengthLabel = (strength) => {
  const labels = {
    strong: 'Mạnh',
    medium: 'Trung bình',
    weak: 'Yếu'
  };
  return labels[strength] || strength;
};

const formatDate = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleDateString('vi-VN', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

watch(() => analysisStore.signalType, (newType) => {
  selectedSignalType.value = newType;
});

onMounted(() => {
  analysisStore.fetchSignals();
});
</script>

<style scoped>
/* Trading signals styles */
</style>

