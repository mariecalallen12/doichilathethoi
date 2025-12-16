<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue';
import { createChart, ColorType } from 'lightweight-charts';
import Card from '../ui/Card.vue';
import api from '../../services/api';

const chartContainer = ref(null);
const logContainer = ref(null);
let chart = null;
let candlestickSeries = null;
let priceData = ref([]);
const logs = ref([]);
const selectedSymbol = ref('BTCUSDT');
const symbols = ref(['BTCUSDT', 'ETHUSDT', 'BNBUSDT']);
const logFilter = ref('all'); // all, rule-change, event-inject, auto-adjust
let wsConnection = null;

const logTypes = {
  'all': 'Tất cả',
  'rule-change': 'Rule Change',
  'event-inject': 'Event Inject',
  'auto-adjust': 'Auto Adjust',
};

const initChart = () => {
  if (!chartContainer.value) return;

  chart = createChart(chartContainer.value, {
    layout: {
      background: { type: ColorType.Solid, color: '#1a1a1a' },
      textColor: '#d1d5db',
    },
    grid: {
      vertLines: { color: '#2a2a2a' },
      horzLines: { color: '#2a2a2a' },
    },
    width: chartContainer.value.clientWidth,
    height: 400,
    timeScale: {
      timeVisible: true,
      secondsVisible: false,
    },
  });

  candlestickSeries = chart.addCandlestickSeries({
    upColor: '#26a69a',
    downColor: '#ef5350',
    borderVisible: false,
    wickUpColor: '#26a69a',
    wickDownColor: '#ef5350',
  });

  // Load initial data
  loadInitialData();
};

const loadInitialData = async () => {
  try {
    const res = await api.get(`/api/sim/candles?symbol=${selectedSymbol.value}&limit=100`);
    const candles = res.data || [];
    
    const formattedData = candles.map((candle) => ({
      time: new Date(candle.start_ts || candle.close_ts).getTime() / 1000,
      open: parseFloat(candle.open),
      high: parseFloat(candle.high),
      low: parseFloat(candle.low),
      close: parseFloat(candle.close),
    })).reverse(); // Reverse để hiển thị từ cũ đến mới
    
    priceData.value = formattedData;
    if (candlestickSeries) {
      candlestickSeries.setData(formattedData);
    }
  } catch (error) {
    console.error('Load initial data error:', error);
    addLog('error', 'Không thể tải dữ liệu ban đầu');
  }
};

const connectWebSocket = () => {
  try {
    const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws';
    wsConnection = new WebSocket(wsUrl);

    wsConnection.onopen = () => {
      addLog('info', 'Đã kết nối WebSocket');
      // Subscribe to candles channel
      wsConnection.send(JSON.stringify({
        type: 'subscribe',
        channel: 'candles',
        symbol: selectedSymbol.value,
      }));
    };

    wsConnection.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        
        if (data.type === 'candle_update' && data.symbol === selectedSymbol.value) {
          const candle = data.candle;
          const newCandle = {
            time: new Date(candle.start_ts || candle.close_ts).getTime() / 1000,
            open: parseFloat(candle.open),
            high: parseFloat(candle.high),
            low: parseFloat(candle.low),
            close: parseFloat(candle.close),
          };
          
          if (candlestickSeries) {
            candlestickSeries.update(newCandle);
          }
          
          addLog('candle', `Candle mới: ${candle.close}`, 'auto-adjust');
        } else if (data.type === 'price_update' && data.symbol === selectedSymbol.value) {
          addLog('price', `Giá cập nhật: ${data.price}`, 'auto-adjust');
        } else if (data.type === 'log_event') {
          addLog(data.level || 'info', data.message, data.event_type);
        }
      } catch (error) {
        console.error('Parse WebSocket message error:', error);
      }
    };

    wsConnection.onerror = (error) => {
      console.error('WebSocket error:', error);
      addLog('error', 'Lỗi kết nối WebSocket');
    };

    wsConnection.onclose = () => {
      addLog('info', 'Đã ngắt kết nối WebSocket');
      // Reconnect after 3 seconds
      setTimeout(connectWebSocket, 3000);
    };
  } catch (error) {
    console.error('WebSocket connection error:', error);
    addLog('error', 'Không thể kết nối WebSocket');
  }
};

const addLog = (level, message, eventType = null) => {
  const log = {
    id: Date.now(),
    timestamp: new Date().toISOString(),
    level,
    message,
    eventType: eventType || 'all',
  };
  
  logs.value.unshift(log);
  
  // Keep only last 100 logs
  if (logs.value.length > 100) {
    logs.value = logs.value.slice(0, 100);
  }
  
  // Auto scroll to top
  if (logContainer.value) {
    logContainer.value.scrollTop = 0;
  }
};

const filteredLogs = () => {
  if (logFilter.value === 'all') {
    return logs.value;
  }
  return logs.value.filter(log => log.eventType === logFilter.value);
};

const getLogColor = (level) => {
  const colors = {
    info: 'text-blue-400',
    success: 'text-green-400',
    warning: 'text-yellow-400',
    error: 'text-red-400',
    candle: 'text-purple-400',
    price: 'text-cyan-400',
  };
  return colors[level] || 'text-white/60';
};

const getLogIcon = (level) => {
  const icons = {
    info: 'fa-info-circle',
    success: 'fa-check-circle',
    warning: 'fa-exclamation-triangle',
    error: 'fa-times-circle',
    candle: 'fa-chart-line',
    price: 'fa-dollar-sign',
  };
  return icons[level] || 'fa-circle';
};

const formatTime = (isoString) => {
  const date = new Date(isoString);
  return date.toLocaleTimeString('vi-VN');
};

const changeSymbol = () => {
  if (wsConnection && wsConnection.readyState === WebSocket.OPEN) {
    // Unsubscribe old symbol
    wsConnection.send(JSON.stringify({
      type: 'unsubscribe',
      channel: 'candles',
      symbol: selectedSymbol.value,
    }));
    
    // Subscribe new symbol
    wsConnection.send(JSON.stringify({
      type: 'subscribe',
      channel: 'candles',
      symbol: selectedSymbol.value,
    }));
  }
  
  loadInitialData();
  addLog('info', `Đã chuyển sang symbol: ${selectedSymbol.value}`, 'rule-change');
};

onMounted(() => {
  initChart();
  connectWebSocket();
  
  // Handle window resize
  window.addEventListener('resize', () => {
    if (chart && chartContainer.value) {
      chart.applyOptions({ width: chartContainer.value.clientWidth });
    }
  });
});

onBeforeUnmount(() => {
  if (wsConnection) {
    wsConnection.close();
  }
  if (chart) {
    chart.remove();
  }
});
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-white mb-2">Educational Hub</h1>
        <p class="text-white/60">
          Real-time chart và log panel để training đội vận hành
        </p>
      </div>
      <div class="flex gap-3">
        <select
          v-model="selectedSymbol"
          @change="changeSymbol"
          class="px-4 py-2 rounded-lg bg-white/10 border border-white/20 text-white focus:outline-none focus:ring-2 focus:ring-primary/50"
        >
          <option v-for="sym in symbols" :key="sym" :value="sym">{{ sym }}</option>
        </select>
      </div>
    </div>

    <!-- Real-time Chart -->
    <Card title="Real-time Price Chart">
      <div ref="chartContainer" class="w-full" style="height: 400px;"></div>
      <div class="mt-4 text-white/60 text-sm">
        Chart hiển thị giá real-time với TradingView Lightweight Charts. 
        Dữ liệu được cập nhật qua WebSocket mỗi khi có candle mới.
      </div>
    </Card>

    <!-- Log Panel -->
    <Card title="Log Panel">
      <div class="mb-4 flex gap-2">
        <button
          v-for="(label, value) in logTypes"
          :key="value"
          @click="logFilter = value"
          :class="[
            'px-4 py-2 rounded-lg text-sm font-semibold transition-colors',
            logFilter === value
              ? 'bg-primary text-white'
              : 'bg-white/10 text-white/60 hover:bg-white/20',
          ]"
        >
          {{ label }}
        </button>
      </div>

      <div
        ref="logContainer"
        class="bg-black/20 rounded-lg p-4 h-96 overflow-y-auto space-y-2"
      >
        <div
          v-for="log in filteredLogs()"
          :key="log.id"
          class="flex items-start gap-3 p-2 rounded bg-white/5 hover:bg-white/10 transition-colors"
        >
          <div class="flex-shrink-0 mt-1">
            <i :class="['fas', getLogIcon(log.level), getLogColor(log.level)]"></i>
          </div>
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2 mb-1">
              <span class="text-xs text-white/40">{{ formatTime(log.timestamp) }}</span>
              <span
                v-if="log.eventType !== 'all'"
                class="px-2 py-0.5 rounded text-xs bg-white/10 text-white/60"
              >
                {{ logTypes[log.eventType] || log.eventType }}
              </span>
            </div>
            <p :class="['text-sm', getLogColor(log.level)]">
              {{ log.message }}
            </p>
          </div>
        </div>
        <div v-if="filteredLogs().length === 0" class="text-center text-white/40 py-8">
          <i class="fas fa-inbox text-4xl mb-2"></i>
          <p>Chưa có log nào</p>
        </div>
      </div>

      <div class="mt-4 text-white/60 text-sm">
        <p class="font-semibold mb-2">Giải thích các loại log:</p>
        <ul class="list-disc list-inside space-y-1">
          <li><strong>Rule Change:</strong> Thay đổi rule/kịch bản (scenario, drift, volatility, etc.)</li>
          <li><strong>Event Inject:</strong> Event được inject (target price, house edge, etc.)</li>
          <li><strong>Auto Adjust:</strong> Tự động điều chỉnh giá (candle update, price update)</li>
        </ul>
        <p class="mt-2">Mỗi log hiển thị "why" - lý do giá thay đổi để training đội vận hành.</p>
      </div>
    </Card>

    <!-- Educational Content -->
    <Card title="Hướng dẫn vận hành">
      <div class="space-y-4 text-white/80 text-sm">
        <div>
          <p class="text-white font-semibold mb-2">1. Real-time Chart</p>
          <ul class="list-disc list-inside space-y-1 ml-4">
            <li>Chart hiển thị giá real-time với candles (OHLC)</li>
            <li>Chọn symbol để xem chart của symbol đó</li>
            <li>Dữ liệu được cập nhật tự động qua WebSocket</li>
            <li>Có thể zoom và pan để xem chi tiết</li>
          </ul>
        </div>
        <div>
          <p class="text-white font-semibold mb-2">2. Log Panel</p>
          <ul class="list-disc list-inside space-y-1 ml-4">
            <li>Filter logs theo type: Rule Change, Event Inject, Auto Adjust</li>
            <li>Mỗi log có timestamp và level (info, success, warning, error)</li>
            <li>Logs được cập nhật real-time khi có events</li>
            <li>Giữ tối đa 100 logs gần nhất</li>
          </ul>
        </div>
        <div>
          <p class="text-white font-semibold mb-2">3. Training Use Cases</p>
          <ul class="list-disc list-inside space-y-1 ml-4">
            <li>Xem cách giá thay đổi khi thay đổi scenario</li>
            <li>Hiểu "why" - lý do giá thay đổi (drift, volatility, target, etc.)</li>
            <li>Quan sát pattern khi bật Anti-TA</li>
            <li>Test formula và xem kết quả real-time</li>
          </ul>
        </div>
      </div>
    </Card>
  </div>
</template>

<style scoped>
/* Custom scrollbar for log container */
.log-container::-webkit-scrollbar {
  width: 8px;
}

.log-container::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 4px;
}

.log-container::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 4px;
}

.log-container::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}
</style>

