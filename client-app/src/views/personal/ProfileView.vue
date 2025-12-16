<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div>
      <h1 class="text-3xl font-bold text-white mb-2">Thông Tin Cá Nhân</h1>
      <p class="text-purple-300">Quản lý thông tin cá nhân và cài đặt bảo mật</p>
    </div>

    <!-- Tabs -->
    <div class="glass-panel rounded-lg p-1">
      <div class="flex space-x-1 overflow-x-auto">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="[
            'px-4 py-3 rounded-lg font-medium transition-all whitespace-nowrap',
            activeTab === tab.id
              ? 'bg-gradient-to-r from-purple-500 to-indigo-500 text-white'
              : 'text-purple-300 hover:text-white hover:bg-purple-500/10'
          ]"
        >
          <i :class="[tab.icon, 'mr-2']"></i>
          {{ tab.label }}
        </button>
      </div>
    </div>

    <!-- Tab Content -->
    <div>
      <div v-if="activeTab === 'info'">
        <PersonalInfoForm />
        <VerificationStatus class="mt-6" />
      </div>
      <div v-if="activeTab === 'bank'">
        <BankAccountList @add-account="showBankForm = true" />
      </div>
      <div v-if="activeTab === 'security'">
        <SecuritySettings />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import PersonalInfoForm from '../../components/personal/profile/PersonalInfoForm.vue';
import VerificationStatus from '../../components/personal/profile/VerificationStatus.vue';
import BankAccountList from '../../components/personal/profile/BankAccountList.vue';
import SecuritySettings from '../../components/personal/profile/SecuritySettings.vue';
import { useProfileStore } from '../../stores/profile';

const profileStore = useProfileStore();
const activeTab = ref('info');
const showBankForm = ref(false);

onMounted(async () => {
  try {
    await Promise.all([
      profileStore.fetchProfile(),
      profileStore.fetchBankAccounts()
    ]);
  } catch (error) {
    console.error('Error fetching profile data:', error);
  }
});

const tabs = [
  {
    id: 'info',
    label: 'Thông Tin Cá Nhân',
    icon: 'fas fa-user',
  },
  {
    id: 'bank',
    label: 'Tài Khoản Ngân Hàng',
    icon: 'fas fa-university',
  },
  {
    id: 'security',
    label: 'Bảo Mật',
    icon: 'fas fa-shield-alt',
  },
];
</script>

