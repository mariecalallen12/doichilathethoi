<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-900">
    <!-- Header -->
    <SupportHeader />
    
    <!-- Main Content -->
    <div class="container mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="mb-8">
        <h1 class="text-4xl font-bold text-transparent bg-gradient-to-r from-purple-300 via-violet-300 to-indigo-300 bg-clip-text mb-4">
          Khiếu Nại
        </h1>
        <p class="text-purple-200/80 text-lg">
          Gửi khiếu nại và theo dõi trạng thái
        </p>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Complaint Form -->
        <div class="lg:col-span-2">
          <ComplaintForm @submit="handleSubmit" />
        </div>

        <!-- Complaint History -->
        <div>
          <ComplaintHistory :complaints="legalStore.complaints" @view-detail="viewComplaintDetail" />
        </div>
      </div>

      <!-- Complaint Detail Modal -->
      <ComplaintStatus
        v-if="selectedComplaint"
        :complaint="selectedComplaint"
        @close="closeComplaintDetail"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useLegalStore } from '../stores/legal';
import SupportHeader from '../components/support/SupportHeader.vue';
import ComplaintForm from '../components/legal/ComplaintForm.vue';
import ComplaintHistory from '../components/legal/ComplaintHistory.vue';
import ComplaintStatus from '../components/legal/ComplaintStatus.vue';
import { success, error as showError } from '../services/utils/toast';

const legalStore = useLegalStore();
const selectedComplaint = ref(null);

const handleSubmit = async (formData) => {
  try {
    await legalStore.submitComplaint(formData);
    success('Khiếu nại đã được gửi thành công!');
  } catch (err) {
    const errorMessage = err?.message || 'Có lỗi xảy ra. Vui lòng thử lại.';
    showError(errorMessage);
  }
};

const viewComplaintDetail = async (complaintId) => {
  selectedComplaint.value = await legalStore.getComplaintById(complaintId);
};

const closeComplaintDetail = () => {
  selectedComplaint.value = null;
};

onMounted(() => {
  legalStore.fetchComplaints();
});
</script>

<style scoped>
/* Complaints page styles */
</style>

