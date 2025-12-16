import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { analysisApi } from '../services/api/analysis';

export const useAnalysisStore = defineStore('analysis', () => {
  // State
  const technicalData = ref({});
  const fundamentalData = ref({});
  const sentiment = ref({});
  const signals = ref([]);
  const indicators = ref([]);
  const isLoading = ref(false);
  const error = ref(null);

  // Selected symbol
  const selectedSymbol = ref('EUR/USD');

  // Filters
  const signalType = ref('all');
  const timeFrame = ref('1h');

  // Computed
  const filteredSignals = computed(() => {
    let result = signals.value;

    if (signalType.value !== 'all') {
      result = result.filter(s => s.type === signalType.value);
    }

    return result.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
  });

  // Actions
  async function fetchTechnicalAnalysis(symbol) {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await analysisApi.getTechnicalAnalysis(symbol || selectedSymbol.value);
      technicalData.value = response.data || response;
      return technicalData.value;
    } catch (err) {
      error.value = err.message || 'Failed to fetch technical analysis';
      console.error('Error fetching technical analysis:', err);
      // Fallback data
      technicalData.value = getFallbackTechnicalData();
      return technicalData.value;
    } finally {
      isLoading.value = false;
    }
  }

  async function fetchFundamentalAnalysis(symbol) {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await analysisApi.getFundamentalAnalysis(symbol || selectedSymbol.value);
      fundamentalData.value = response.data || response;
      return fundamentalData.value;
    } catch (err) {
      error.value = err.message || 'Failed to fetch fundamental analysis';
      console.error('Error fetching fundamental analysis:', err);
      // Fallback data
      fundamentalData.value = getFallbackFundamentalData();
      return fundamentalData.value;
    } finally {
      isLoading.value = false;
    }
  }

  async function fetchSentiment() {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await analysisApi.getSentiment();
      sentiment.value = response.data || response;
      return sentiment.value;
    } catch (err) {
      error.value = err.message || 'Failed to fetch sentiment';
      console.error('Error fetching sentiment:', err);
      // Fallback data
      sentiment.value = getFallbackSentiment();
      return sentiment.value;
    } finally {
      isLoading.value = false;
    }
  }

  async function fetchSignals() {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await analysisApi.getSignals();
      signals.value = response.data || response;
      return signals.value;
    } catch (err) {
      error.value = err.message || 'Failed to fetch signals';
      console.error('Error fetching signals:', err);
      // Fallback data
      signals.value = getFallbackSignals();
      return signals.value;
    } finally {
      isLoading.value = false;
    }
  }

  async function runBacktest(backtestData) {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await analysisApi.runBacktest(backtestData);
      return response.data || response;
    } catch (err) {
      error.value = err.message || 'Failed to run backtest';
      console.error('Error running backtest:', err);
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  function setSelectedSymbol(symbol) {
    selectedSymbol.value = symbol;
  }

  function setSignalType(type) {
    signalType.value = type;
  }

  function setTimeFrame(tf) {
    timeFrame.value = tf;
  }

  // Fallback data
  function getFallbackTechnicalData() {
    return {
      symbol: selectedSymbol.value,
      indicators: {
        rsi: 55.5,
        macd: { value: 0.12, signal: 0.08 },
        bollinger: { upper: 1.09, middle: 1.085, lower: 1.08 },
        moving_averages: {
          sma_20: 1.084,
          sma_50: 1.082,
          ema_12: 1.085
        }
      },
      support: 1.08,
      resistance: 1.09,
      trend: 'bullish'
    };
  }

  function getFallbackFundamentalData() {
    return {
      symbol: selectedSymbol.value,
      economic_indicators: {
        gdp: { value: 2.5, change: 0.3 },
        inflation: { value: 2.1, change: -0.1 },
        interest_rate: { value: 4.5, change: 0.25 }
      },
      news_sentiment: 'positive',
      analyst_ratings: {
        buy: 12,
        hold: 5,
        sell: 3
      }
    };
  }

  function getFallbackSentiment() {
    return {
      fear_greed_index: 65,
      social_sentiment: {
        twitter: 0.72,
        reddit: 0.68,
        overall: 0.70
      },
      market_sentiment: 'bullish'
    };
  }

  function getFallbackSignals() {
    return [
      {
        id: '1',
        symbol: 'EUR/USD',
        type: 'buy',
        strength: 'strong',
        price: 1.0850,
        target: 1.0900,
        stop_loss: 1.0800,
        created_at: new Date().toISOString(),
        source: 'ai'
      }
    ];
  }

  return {
    // State
    technicalData,
    fundamentalData,
    sentiment,
    signals,
    indicators,
    isLoading,
    error,
    selectedSymbol,
    signalType,
    timeFrame,
    // Computed
    filteredSignals,
    // Actions
    fetchTechnicalAnalysis,
    fetchFundamentalAnalysis,
    fetchSentiment,
    fetchSignals,
    runBacktest,
    setSelectedSymbol,
    setSignalType,
    setTimeFrame
  };
});

