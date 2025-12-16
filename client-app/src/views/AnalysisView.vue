<template>
  <AnalysisLayout>
    <!-- Technical Analysis Tools -->
    <TechnicalAnalysisTools />
    
    <!-- Fundamental Analysis Section -->
    <FundamentalAnalysisSection />
    
    <!-- Sentiment Indicators Section -->
    <SentimentIndicatorsSection />
    
    <!-- Trading Signals Section -->
    <TradingSignalsSection />
    
    <!-- Chart Analysis Tools -->
    <ChartAnalysisTools />
  </AnalysisLayout>
</template>

<script setup>
import { onMounted } from 'vue';
import AnalysisLayout from '../components/analysis/AnalysisLayout.vue';
import TechnicalAnalysisTools from '../components/analysis/TechnicalAnalysisTools.vue';
import FundamentalAnalysisSection from '../components/analysis/FundamentalAnalysisSection.vue';
import SentimentIndicatorsSection from '../components/analysis/SentimentIndicatorsSection.vue';
import TradingSignalsSection from '../components/analysis/TradingSignalsSection.vue';
import ChartAnalysisTools from '../components/analysis/ChartAnalysisTools.vue';
import { useAnalysisStore } from '../stores/analysis';

const analysisStore = useAnalysisStore();

onMounted(() => {
  // Initialize stores - fetch initial data
  analysisStore.fetchTechnicalAnalysis();
  analysisStore.fetchFundamentalAnalysis();
  analysisStore.fetchSentiment();
  analysisStore.fetchSignals();
});
</script>

<style scoped>
/* Analysis page specific styles */
</style>

