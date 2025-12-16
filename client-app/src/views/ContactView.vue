<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-900">
    <!-- Header -->
    <SupportHeader />
    
    <!-- Main Content -->
    <div class="container mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="mb-8">
        <h1 class="text-4xl font-bold text-transparent bg-gradient-to-r from-purple-300 via-violet-300 to-indigo-300 bg-clip-text mb-4">
          Liên Hệ
        </h1>
        <p class="text-purple-200/80 text-lg">
          Chúng tôi luôn sẵn sàng hỗ trợ bạn
        </p>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <!-- Contact Form -->
        <ContactForm @submit="handleSubmit" />

        <!-- Office Locations & Support Channels -->
        <div class="space-y-6">
          <OfficeLocations />
          <SupportChannels />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useSupportStore } from '../stores/support';
import SupportHeader from '../components/support/SupportHeader.vue';
import ContactForm from '../components/support/ContactForm.vue';
import OfficeLocations from '../components/support/OfficeLocations.vue';
import SupportChannels from '../components/support/SupportChannels.vue';
import { success, error as showError } from '../services/utils/toast';

const supportStore = useSupportStore();

const handleSubmit = async (formData) => {
  try {
    await supportStore.submitContact(formData);
    // Show success message
    success('Gửi thành công! Chúng tôi sẽ liên hệ với bạn sớm nhất.');
  } catch (err) {
    // Show error message
    const errorMessage = err?.message || 'Có lỗi xảy ra. Vui lòng thử lại.';
    showError(errorMessage);
  }
};

onMounted(() => {
  supportStore.getOffices();
  supportStore.getChannels();
});
</script>

<style scoped>
/* Contact page styles */
</style>

