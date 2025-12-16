<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-900">
    <!-- Header -->
    <SupportHeader />
    
    <!-- Main Content -->
    <div class="container mx-auto px-4 sm:px-6 lg:px-8 py-8 max-w-4xl">
      <div class="mb-8">
        <h1 class="text-4xl font-bold text-transparent bg-gradient-to-r from-purple-300 via-violet-300 to-indigo-300 bg-clip-text mb-4">
          Cảnh Báo Rủi Ro
        </h1>
        <p class="text-purple-200/80 text-lg">
          Thông tin quan trọng về rủi ro khi giao dịch
        </p>
      </div>

      <!-- Warning Banner -->
      <div class="mb-8 bg-red-900/20 border border-red-500/30 rounded-lg p-6">
        <div class="flex items-start space-x-3">
          <i class="fas fa-exclamation-triangle text-red-400 text-2xl mt-1"></i>
          <div>
            <h3 class="text-red-400 font-bold text-xl mb-2">Cảnh Báo Quan Trọng</h3>
            <p class="text-gray-300">
              Giao dịch CFD và Forex có rủi ro cao và có thể không phù hợp với tất cả nhà đầu tư. 
              Bạn có thể mất một phần hoặc toàn bộ khoản đầu tư của mình.
            </p>
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="legalStore.isLoading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-400"></div>
        <p class="text-purple-200 mt-4">Đang tải...</p>
      </div>

      <!-- Risk Warning Content -->
      <div v-else class="bg-gradient-to-br from-slate-800/50 to-slate-900/50 rounded-xl p-8 border border-purple-500/20">
        <RiskWarningContent :content="riskWarning?.content || ''" />
      </div>

      <!-- Interactive Risk Assessment -->
      <div class="mt-8 bg-gradient-to-br from-slate-800/50 to-slate-900/50 rounded-xl p-6 border border-purple-500/20">
        <h3 class="text-xl font-bold text-white mb-4">Đánh Giá Rủi Ro Cá Nhân</h3>
        <p class="text-gray-400 mb-4">Trả lời các câu hỏi sau để đánh giá mức độ rủi ro phù hợp với bạn:</p>
        <!-- Risk assessment questions would go here -->
        <button class="px-6 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-lg hover:from-purple-700 hover:to-indigo-700 transition-all">
          Bắt Đầu Đánh Giá
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useLegalStore } from '../stores/legal';
import SupportHeader from '../components/support/SupportHeader.vue';
import RiskWarningContent from '../components/legal/RiskWarningContent.vue';

const legalStore = useLegalStore();
const riskWarning = ref(null);

onMounted(async () => {
  riskWarning.value = await legalStore.fetchRiskWarning();
});
</script>

<style scoped>
/* Risk warning page styles */
</style>

