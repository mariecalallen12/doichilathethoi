<template>
  <div class="bg-gradient-to-br from-slate-800/50 to-slate-900/50 rounded-xl p-6 border border-purple-500/20">
    <h3 class="text-xl font-bold text-white mb-4">Kênh Hỗ Trợ</h3>
    <div class="space-y-3">
      <div
        v-for="channel in channels"
        :key="channel.id"
        class="flex items-center justify-between p-4 bg-slate-700/50 rounded-lg hover:bg-slate-700 transition-all cursor-pointer"
      >
        <div class="flex items-center space-x-3">
          <i :class="channel.icon" class="text-2xl text-purple-400"></i>
          <div>
            <div class="text-white font-semibold">{{ channel.name }}</div>
            <div class="text-sm text-gray-400">{{ channel.description }}</div>
          </div>
        </div>
        <i class="fas fa-chevron-right text-purple-400"></i>
      </div>

      <!-- Fallback -->
      <div v-if="channels.length === 0" class="space-y-3">
        <div class="flex items-center justify-between p-4 bg-slate-700/50 rounded-lg">
          <div class="flex items-center space-x-3">
            <i class="fas fa-envelope text-2xl text-purple-400"></i>
            <div>
              <div class="text-white font-semibold">Email</div>
              <div class="text-sm text-gray-400">support@cmeetrading.com</div>
            </div>
          </div>
          <i class="fas fa-chevron-right text-purple-400"></i>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { supportApi } from '../../services/api/support';

const supportStore = useSupportStore();
const channels = ref([]);

onMounted(async () => {
  try {
    const response = await supportApi.getChannels();
    channels.value = response.data || response || [];
  } catch (error) {
    console.error('Error fetching channels:', error);
    channels.value = [];
  }
});
</script>

<style scoped>
/* Support channels styles */
</style>

