<script setup>
import { onMounted } from 'vue';
import { useAuthStore } from '../../store/auth';
import Sidebar from './Sidebar.vue';
import Header from './Header.vue';
import Breadcrumb from './Breadcrumb.vue';
import ToastContainer from '../notifications/ToastContainer.vue';

const authStore = useAuthStore();

onMounted(async () => {
  await authStore.checkAuth();
});
</script>

<template>
  <div class="min-h-screen bg-gradient-admin">
    <Sidebar />
    <div class="lg:ml-[260px] transition-all">
      <Header>
        <template #breadcrumb>
          <Breadcrumb />
        </template>
      </Header>
      <main class="p-4 lg:p-6 max-w-7xl mx-auto">
        <router-view />
      </main>
    </div>
    <ToastContainer />
  </div>
</template>

<style scoped>
.bg-gradient-admin {
  background: linear-gradient(135deg, #0F172A 0%, #1E293B 50%, #0F172A 100%);
}
</style>

