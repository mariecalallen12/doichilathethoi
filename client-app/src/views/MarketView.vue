<template>
  <MarketLayout>
    <!-- Market Overview Section -->
    <MarketOverview />
    
    <!-- Asset Category Tabs -->
    <AssetCategoryTabs />
    
    <!-- Search and Filter Tools -->
    <MarketFilters />
    
    <!-- Real-time Price Table -->
    <PriceTable />
    
    <!-- TradingView Chart Integration -->
    <TradingViewWidget />
    
    <!-- Market Heatmap -->
    <MarketHeatmap />
    
    <!-- Financial News Feed -->
    <NewsFeed />
    
    <!-- Economic Indicators -->
    <EconomicIndicators />
    
    <!-- Market Analysis Section -->
    <MarketAnalysis />
    
    <!-- Quick Trade Widget (Fixed Position) -->
    <QuickTradeWidget />
    
    <!-- Footer -->
    <MarketFooter />
  </MarketLayout>
</template>

<script setup>
import { onMounted } from 'vue';
import MarketLayout from '../components/market/MarketLayout.vue';
import MarketOverview from '../components/market/MarketOverview.vue';
import AssetCategoryTabs from '../components/market/AssetCategoryTabs.vue';
import MarketFilters from '../components/market/MarketFilters.vue';
import PriceTable from '../components/market/PriceTable.vue';
import TradingViewWidget from '../components/market/TradingViewWidget.vue';
import MarketHeatmap from '../components/market/MarketHeatmap.vue';
import NewsFeed from '../components/market/NewsFeed.vue';
import EconomicIndicators from '../components/market/EconomicIndicators.vue';
import MarketAnalysis from '../components/market/MarketAnalysis.vue';
import QuickTradeWidget from '../components/market/QuickTradeWidget.vue';
import MarketFooter from '../components/market/MarketFooter.vue';
import { useMarketStore } from '../stores/market';
import { useNewsStore } from '../stores/news';
import { useIndicatorsStore } from '../stores/indicators';

const marketStore = useMarketStore();
const newsStore = useNewsStore();
const indicatorsStore = useIndicatorsStore();

onMounted(() => {
  // Initialize stores
  marketStore.setupWebSocketListeners();
  newsStore.fetchNews();
  indicatorsStore.fetchIndicators();
});
</script>

<style>
@import '../styles/market.css';
</style>

