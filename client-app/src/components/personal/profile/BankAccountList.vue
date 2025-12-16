<template>
  <div class="glass-panel rounded-lg p-6">
    <div class="flex items-center justify-between mb-6">
      <h3 class="text-lg font-bold text-white flex items-center">
        <i class="fas fa-university mr-2 text-purple-400"></i>
        Tài Khoản Ngân Hàng
      </h3>
      <button
        @click="$emit('add-account')"
        class="px-4 py-2 bg-gradient-to-r from-purple-500 to-indigo-500 text-white rounded-lg text-sm font-medium hover:from-purple-600 hover:to-indigo-600 transition-all"
      >
        <i class="fas fa-plus mr-2"></i>Thêm tài khoản
      </button>
    </div>

    <div v-if="loading" class="space-y-3">
      <div v-for="i in 3" :key="i" class="h-20 bg-slate-800/50 rounded-lg animate-pulse"></div>
    </div>

    <div v-else-if="bankAccounts.length === 0" class="text-center py-8 text-purple-300">
      <i class="fas fa-inbox text-4xl mb-2"></i>
      <p>Chưa có tài khoản ngân hàng nào</p>
    </div>

    <div v-else class="space-y-3">
      <div
        v-for="account in bankAccounts"
        :key="account.id"
        class="p-4 bg-slate-800/50 rounded-lg hover:bg-slate-800/70 transition-all"
      >
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-4 flex-1">
            <div class="w-12 h-12 bg-purple-500/20 rounded-lg flex items-center justify-center">
              <i class="fas fa-university text-purple-300 text-xl"></i>
            </div>
            <div class="flex-1">
              <div class="flex items-center space-x-2 mb-1">
                <span class="text-white font-medium">{{ account.bankName }}</span>
                <span
                  v-if="account.isPrimary"
                  class="px-2 py-1 bg-purple-500/20 text-purple-300 text-xs rounded"
                >
                  Mặc định
                </span>
                <StatusBadge :status="account.status === 'verified' ? 'completed' : 'pending'" />
              </div>
              <div class="text-purple-300 text-xs">
                Số tài khoản: ****{{ account.accountNumber.slice(-4) }}
              </div>
              <div class="text-purple-300 text-xs">
                Chủ tài khoản: {{ account.accountHolder }}
              </div>
            </div>
          </div>
          <div class="flex items-center space-x-2">
            <button
              v-if="!account.isPrimary"
              @click="$emit('set-primary', account.id)"
              class="px-3 py-1 text-xs bg-purple-500/20 text-purple-300 rounded hover:bg-purple-500/30 transition-colors"
            >
              Đặt mặc định
            </button>
            <button
              @click="$emit('edit', account)"
              class="px-3 py-1 text-xs bg-blue-500/20 text-blue-300 rounded hover:bg-blue-500/30 transition-colors"
            >
              Sửa
            </button>
            <button
              v-if="!account.isPrimary"
              @click="$emit('remove', account.id)"
              class="px-3 py-1 text-xs bg-red-500/20 text-red-300 rounded hover:bg-red-500/30 transition-colors"
            >
              Xóa
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useProfileStore } from '../../../stores/profile';
import StatusBadge from '../shared/StatusBadge.vue';

const profileStore = useProfileStore();
const bankAccounts = ref([]);
const loading = ref(true);

defineEmits(['add-account', 'set-primary', 'edit', 'remove']);

onMounted(async () => {
  try {
    loading.value = true;
    await profileStore.fetchBankAccounts();
    bankAccounts.value = profileStore.bankAccounts;
  } catch (error) {
    console.error('Failed to fetch bank accounts:', error);
    bankAccounts.value = [];
  } finally {
    loading.value = false;
  }
});
</script>

