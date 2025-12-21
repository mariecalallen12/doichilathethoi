<template>
  <div class="trading-view">
    <!-- Trading Header -->
    <TradingHeader :connectionStatus="connectionStatus" />
    
    <!-- TradingView Chart Widget - REAL-TIME CHART -->
    <div class="chart-container">
      <TradingViewChart :symbol="selectedSymbol" />
    </div>
    
    <!-- Binary Sentiment Display -->
    <BinarySentimentBoard 
      :binaryArray="binaryArray"
      :marketSentiment="marketSentiment"
    />
    
    <!-- Trading Signals Grid -->
    <TradingSignalsGrid 
      :signals="tradingSignals"
      :loading="isLoadingSignals"
      @symbolSelect="onSymbolSelect"
    />
    
    <!-- Asset Class Performance -->
    <AssetClassPerformance 
      :analysis="assetAnalysis"
    />
    
    <!-- Top Gainers & Losers -->
    <TopMovers 
      :gainers="topGainers"
      :losers="topLosers"
      @symbolSelect="onSymbolSelect"
    />
    
    <!-- Trading Recommendations -->
    <TradingRecommendations 
      :recommendations="recommendations"
    />
    
    <!-- Market Analysis Dashboard -->
    <MarketAnalysisDashboard 
      :analysis="marketAnalysis"
    />
    
    <!-- Live Signal Stream -->
    <LiveSignalStream 
      :stream="signalStream"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue';
import TradingHeader from '../components/trading/TradingHeader.vue';
import TradingViewChart from '../components/trading/TradingViewChart.vue';
import BinarySentimentBoard from '../components/trading/BinarySentimentBoard.vue';
import TradingSignalsGrid from '../components/trading/TradingSignalsGrid.vue';
import AssetClassPerformance from '../components/trading/AssetClassPerformance.vue';
import TopMovers from '../components/trading/TopMovers.vue';
import TradingRecommendations from '../components/trading/TradingRecommendations.vue';
import MarketAnalysisDashboard from '../components/trading/MarketAnalysisDashboard.vue';
import LiveSignalStream from '../components/trading/LiveSignalStream.vue';
import { useTradingStore } from '../stores/trading';

const tradingStore = useTradingStore();

// Reactive states
const connectionStatus = ref({
  signals: false,
  binary: false
});

const selectedSymbol = ref('BTCUSDT'); // Default symbol

const binaryArray = computed(() => tradingStore.binaryArray);
const marketSentiment = computed(() => tradingStore.marketSentiment);
const tradingSignals = computed(() => tradingStore.signals);
const isLoadingSignals = computed(() => tradingStore.isLoading);
const assetAnalysis = computed(() => tradingStore.assetClassAnalysis);
const topGainers = computed(() => tradingStore.topGainers);
const topLosers = computed(() => tradingStore.topLosers);
const recommendations = computed(() => tradingStore.recommendations);
const marketAnalysis = computed(() => tradingStore.analysis);
const signalStream = computed(() => tradingStore.signalStream);

// Handle symbol selection from components
function onSymbolSelect(symbol) {
  selectedSymbol.value = symbol;
  console.log('[TradingView] Symbol selected:', symbol);
}

onMounted(async () => {
  console.log('[TradingView] Initializing...');
  
  // Fetch initial data
  await tradingStore.fetchAllSignals();
  await tradingStore.fetchBinaryArray();
  await tradingStore.fetchMarketAnalysis();
  await tradingStore.fetchRecommendations();
  
  // Setup WebSocket real-time streams
  tradingStore.setupWebSocketListeners((stream, status) => {
    connectionStatus.value[stream] = status;
  });
  
  // Start real-time updates
  tradingStore.startRealTimeUpdates();
  
  console.log('[TradingView] Initialized ✅');
});

onUnmounted(() => {
  console.log('[TradingView] Cleaning up...');
  tradingStore.stopRealTimeUpdates();
});
</script>

<style scoped>
.trading-view {
  min-height: 100vh;
  background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
  padding: 20px;
}

.chart-container {
  margin: 20px 0;
  background: #1e293b;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
}
</style>
