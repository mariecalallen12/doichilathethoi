<template>
  <div class="bg-gradient-to-br from-slate-800/50 to-slate-900/50 rounded-xl p-6 border border-purple-500/20">
    <h3 class="text-xl font-bold text-white mb-4">Văn Phòng</h3>
    <div class="space-y-4">
      <div
        v-for="office in offices"
        :key="office.id"
        class="p-4 bg-slate-700/50 rounded-lg"
      >
        <h4 class="text-white font-semibold mb-2">{{ office.name }}</h4>
        <div class="space-y-1 text-sm text-gray-400">
          <p><i class="fas fa-map-marker-alt mr-2 text-purple-400"></i>{{ office.address }}</p>
          <p><i class="fas fa-phone mr-2 text-purple-400"></i>{{ office.phone }}</p>
          <p><i class="fas fa-envelope mr-2 text-purple-400"></i>{{ office.email }}</p>
          <p v-if="office.hours"><i class="fas fa-clock mr-2 text-purple-400"></i>{{ office.hours }}</p>
        </div>
      </div>
      
      <!-- Fallback -->
      <div v-if="offices.length === 0" class="p-4 bg-slate-700/50 rounded-lg">
        <h4 class="text-white font-semibold mb-2">Văn phòng chính</h4>
        <div class="space-y-1 text-sm text-gray-400">
          <p><i class="fas fa-map-marker-alt mr-2 text-purple-400"></i>123 Nguyễn Huệ, Quận 1, TP.HCM</p>
          <p><i class="fas fa-phone mr-2 text-purple-400"></i>+84 1900 1234</p>
          <p><i class="fas fa-envelope mr-2 text-purple-400"></i>support@cmeetrading.com</p>
          <p><i class="fas fa-clock mr-2 text-purple-400"></i>Thứ 2 - Thứ 6: 9:00 - 18:00</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { supportApi } from '../../services/api/support';

const supportStore = useSupportStore();
const offices = ref([]);

onMounted(async () => {
  try {
    const response = await supportStore.getOffices();
    offices.value = response.data || response || [];
  } catch (error) {
    console.error('Error fetching offices:', error);
    offices.value = [];
  }
});
</script>

<style scoped>
/* Office locations styles */
</style>

