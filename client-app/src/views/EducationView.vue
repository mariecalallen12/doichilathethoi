<template>
  <EducationLayout>
    <!-- Video Tutorials Section -->
    <VideoTutorialsSection />
    
    <!-- Ebook Section -->
    <EbookSection />
    
    <!-- Economic Calendar Section -->
    <EconomicCalendarSection />
    
    <!-- Market Reports Section -->
    <MarketReportsSection />
  </EducationLayout>
</template>

<script setup>
import { onMounted } from 'vue';
import EducationLayout from '../components/education/EducationLayout.vue';
import VideoTutorialsSection from '../components/education/VideoTutorialsSection.vue';
import EbookSection from '../components/education/EbookSection.vue';
import EconomicCalendarSection from '../components/education/EconomicCalendarSection.vue';
import MarketReportsSection from '../components/education/MarketReportsSection.vue';
import { useEducationStore } from '../stores/education';

const educationStore = useEducationStore();

onMounted(() => {
  // Initialize stores - fetch initial data
  educationStore.fetchVideos();
  educationStore.fetchEbooks();
  educationStore.fetchReports();
  
  // Fetch calendar for current month
  const now = new Date();
  const startDate = new Date(now.getFullYear(), now.getMonth(), 1).toISOString();
  const endDate = new Date(now.getFullYear(), now.getMonth() + 1, 0).toISOString();
  educationStore.fetchCalendar(startDate, endDate);
});
</script>

<style scoped>
/* Education page specific styles */
</style>

