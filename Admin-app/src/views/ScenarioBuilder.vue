<script setup>
import { ref, onMounted, onUnmounted, computed, watch } from 'vue';
import api from '../services/api';
import toastService from '../services/toast';
import Card from '../components/ui/Card.vue';
import Input from '../components/ui/Input.vue';
import Select from '../components/ui/Select.vue';
import ToggleSwitch from '../components/settings/ToggleSwitch.vue';
import Button from '../components/ui/Button.vue';
import MonacoEditor from '../components/ui/MonacoEditor.vue';
import DateTimeInput from '../components/ui/DateTimeInput.vue';
import MarketChartPreview from '../components/market/MarketChartPreview.vue';
import MarketDataCards from '../components/market/MarketDataCards.vue';
import { useMarketPreviewStore } from '../store/marketPreview';
import ExcelJS from 'exceljs';

const scenarios = ref([]);
const sessions = ref([]);
const stopNotes = ref({});
const monitoring = ref(null);
const loading = ref(false);
const loadingSessions = ref(false);
const loadingMonitoring = ref(false);

// Preview functionality
const selectedPreviewSymbol = ref('');
const marketStore = useMarketPreviewStore();

const scenarioTemplate = {
  symbol: 'BTCUSDT',
  name: '',
  trend: 'SIDEWAY',
  drift: 0.0005,
  volatility: 0.002,
  volatilityLevel: 0.001,  // Default to LOW
  spread_bps: 8,
  depth: 10,
  target_price: null,
  house_edge: 0,
  anti_ta: false,
  formula: '',
  notes: '',
  start_ts: null,  // Thời gian bắt đầu áp dụng kịch bản
  end_ts: null,    // Thời gian kết thúc áp dụng kịch bản
};

const sessionForm = ref({
  name: 'Demo Session',
  note: '',
});

const trendOptions = [
  { label: 'UPTREND', value: 'UPTREND' },
  { label: 'DOWNTREND', value: 'DOWNTREND' },
  { label: 'SIDEWAY', value: 'SIDEWAY' },
];

const volatilityOptions = [
  { label: 'LOW (0.1%)', value: 0.001 },
  { label: 'MEDIUM (0.5%)', value: 0.005 },
  { label: 'HIGH (1.5%)', value: 0.015 },
  { label: 'CUSTOM', value: 'custom' },
];

// Helper function to get volatility level label
const getVolatilityLevel = (value) => {
  if (value <= 0.002) return 'LOW';
  if (value <= 0.008) return 'MEDIUM';
  return 'HIGH';
};

// Computed properties for preview
const symbolOptions = computed(() => {
  const uniqueSymbols = [...new Set(scenarios.value.map(sc => sc.symbol).filter(Boolean))];
  return uniqueSymbols.map(symbol => ({
    label: symbol,
    value: symbol
  }));
});

// Preview methods
const handlePreviewSymbolChange = (symbol) => {
  if (symbol) {
    // Unsubscribe from previous symbol
    if (selectedPreviewSymbol.value) {
      marketStore.unsubscribeFromSymbol(selectedPreviewSymbol.value);
    }
    
    // Subscribe to new symbol
    marketStore.subscribeToSymbol(symbol);
    
    // Fetch initial data
    marketStore.fetchMarketData(symbol);
  }
};

const fetchScenarios = async () => {
  loading.value = true;
  try {
    const res = await api.get('/api/admin/settings/market-scenarios');
    scenarios.value = res.data?.data || [];
    if (!scenarios.value.length) {
      scenarios.value = [{ ...scenarioTemplate }];
    }
  } catch (error) {
    console.error('Fetch scenarios error:', error);
    toastService.error('Không thể tải Scenario Builder');
  } finally {
    loading.value = false;
  }
};

const saveScenarios = async () => {
  loading.value = true;
  try {
    await api.put('/api/admin/settings/market-scenarios', {
      scenarios: scenarios.value.map((sc) => ({
        ...sc,
        drift: Number(sc.drift || 0),
        volatility: Number(sc.volatility || 0),
        spread_bps: Number(sc.spread_bps || 0),
        depth: Number(sc.depth || 1),
        target_price:
          sc.target_price === '' || sc.target_price === null || typeof sc.target_price === 'undefined'
            ? null
            : Number(sc.target_price),
        house_edge: Number(sc.house_edge || 0),
        start_ts: sc.start_ts || null,  // Thời gian bắt đầu
        end_ts: sc.end_ts || null,      // Thời gian kết thúc
      })),
    });
    toastService.success('Đã lưu kịch bản và áp dụng cho simulator');
    await fetchMonitoring();
    
    // Refresh preview if symbol is selected
    if (selectedPreviewSymbol.value) {
      await marketStore.refreshSymbol(selectedPreviewSymbol.value);
    }
  } catch (error) {
    console.error('Save scenarios error:', error);
    toastService.error(error?.response?.data?.detail || 'Không thể lưu kịch bản');
  } finally {
    loading.value = false;
  }
};

const addScenarioRow = () => {
  scenarios.value.push({ ...scenarioTemplate });
};

const removeScenarioRow = (index) => {
  scenarios.value.splice(index, 1);
};

const fetchSessions = async () => {
  loadingSessions.value = true;
  try {
    const res = await api.get('/api/admin/simulator/sessions');
    sessions.value = res.data?.data || [];
  } catch (error) {
    console.error('Fetch sessions error:', error);
    toastService.error('Không thể tải Session Manager');
  } finally {
    loadingSessions.value = false;
  }
};

const startSession = async () => {
  loadingSessions.value = true;
  try {
    await api.post('/api/admin/simulator/sessions/start', {
      name: sessionForm.value.name,
      note: sessionForm.value.note,
    });
    toastService.success('Đã bắt đầu session mới và reset simulator');
    sessionForm.value = { ...sessionForm.value, note: '' };
    await Promise.all([fetchSessions(), fetchMonitoring()]);
  } catch (error) {
    console.error('Start session error:', error);
    toastService.error('Không thể bắt đầu session');
  } finally {
    loadingSessions.value = false;
  }
};

const stopSession = async (sessionId) => {
  loadingSessions.value = true;
  try {
    await api.post('/api/admin/simulator/sessions/stop', {
      session_id: sessionId,
      result: stopNotes.value[sessionId] ? { note: stopNotes.value[sessionId] } : undefined,
    });
    toastService.success('Đã dừng session');
    await fetchSessions();
  } catch (error) {
    console.error('Stop session error:', error);
    toastService.error('Không thể dừng session');
  } finally {
    loadingSessions.value = false;
  }
};

const replaySession = async (sessionId) => {
  loadingSessions.value = true;
  try {
    await api.post('/api/admin/simulator/sessions/replay', {
      session_id: sessionId,
    });
    toastService.success('Đã replay session và áp dụng kịch bản');
    await Promise.all([fetchSessions(), fetchMonitoring()]);
  } catch (error) {
    console.error('Replay session error:', error);
    toastService.error(error?.response?.data?.detail || 'Không thể replay session');
  } finally {
    loadingSessions.value = false;
  }
};

const resetSimulator = async () => {
  loadingSessions.value = true;
  try {
    await api.post('/api/admin/simulator/sessions/reset');
    toastService.success('Đã reset simulator và xóa lịch sử session');
    await Promise.all([fetchSessions(), fetchMonitoring(), fetchScenarios()]);
  } catch (error) {
    console.error('Reset simulator error:', error);
    toastService.error('Không thể reset simulator');
  } finally {
    loadingSessions.value = false;
  }
};

const fetchMonitoring = async () => {
  loadingMonitoring.value = true;
  try {
    const res = await api.get('/api/admin/simulator/monitoring');
    monitoring.value = res.data?.data || null;
  } catch (error) {
    console.error('Fetch monitoring error:', error);
    toastService.error('Không thể tải Monitoring Hub');
  } finally {
    loadingMonitoring.value = false;
  }
};

const exportSessionToCSV = (session) => {
  const rows = [
    ['Session Export', ''],
    ['ID', session.id],
    ['Tên', session.name],
    ['Trạng thái', session.status],
    ['Bắt đầu', session.started_at || '—'],
    ['Kết thúc', session.ended_at || '—'],
    ['Ghi chú', session.note || '—'],
    ['Result Note', session.result?.note || '—'],
    [''],
    ['Scenarios', ''],
  ];

  // Add scenarios
  if (session.scenarios_snapshot && session.scenarios_snapshot.length > 0) {
    rows.push(['Symbol', 'Name', 'Trend', 'Drift', 'Volatility', 'Spread (bps)', 'Depth', 'Target Price', 'House Edge', 'Anti-TA', 'Formula', 'Notes']);
    session.scenarios_snapshot.forEach((sc) => {
      rows.push([
        sc.symbol || '',
        sc.name || '',
        sc.trend || '',
        sc.drift || '',
        sc.volatility || '',
        sc.spread_bps || '',
        sc.depth || '',
        sc.target_price || '',
        sc.house_edge || '',
        sc.anti_ta ? 'Yes' : 'No',
        sc.formula || '',
        sc.notes || '',
      ]);
    });
  } else {
    rows.push(['Không có scenarios']);
  }

  // Convert to CSV
  const csvContent = rows.map(row => row.map(cell => `"${String(cell).replace(/"/g, '""')}"`).join(',')).join('\n');
  
  // Download
  const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = `session_${session.id}_${new Date().toISOString().split('T')[0]}.csv`;
  link.click();
  URL.revokeObjectURL(link.href);
  
  toastService.success('Đã export session ra CSV');
};

const exportSessionToExcel = async (session) => {
  try {
    const workbook = new ExcelJS.Workbook();
    const worksheet = workbook.addWorksheet('Session Details');

    // Header
    worksheet.mergeCells('A1:B1');
    worksheet.getCell('A1').value = 'Session Export';
    worksheet.getCell('A1').font = { bold: true, size: 14 };
    worksheet.getCell('A1').alignment = { horizontal: 'center' };

    // Session Info
    worksheet.getCell('A3').value = 'ID';
    worksheet.getCell('B3').value = session.id;
    worksheet.getCell('A4').value = 'Tên';
    worksheet.getCell('B4').value = session.name;
    worksheet.getCell('A5').value = 'Trạng thái';
    worksheet.getCell('B5').value = session.status;
    worksheet.getCell('A6').value = 'Bắt đầu';
    worksheet.getCell('B6').value = session.started_at || '—';
    worksheet.getCell('A7').value = 'Kết thúc';
    worksheet.getCell('B7').value = session.ended_at || '—';
    worksheet.getCell('A8').value = 'Ghi chú';
    worksheet.getCell('B8').value = session.note || '—';
    worksheet.getCell('A9').value = 'Result Note';
    worksheet.getCell('B9').value = session.result?.note || '—';

    // Scenarios
    if (session.scenarios_snapshot && session.scenarios_snapshot.length > 0) {
      worksheet.getCell('A11').value = 'Scenarios';
      worksheet.getCell('A11').font = { bold: true };

      const scenarioHeaders = ['Symbol', 'Name', 'Trend', 'Drift', 'Volatility', 'Spread (bps)', 'Depth', 'Target Price', 'House Edge', 'Anti-TA', 'Formula', 'Notes'];
      worksheet.addRow(scenarioHeaders);
      const headerRow = worksheet.getRow(12);
      headerRow.font = { bold: true };
      headerRow.fill = {
        type: 'pattern',
        pattern: 'solid',
        fgColor: { argb: 'FFE0E0E0' },
      };

      session.scenarios_snapshot.forEach((sc) => {
        worksheet.addRow([
          sc.symbol || '',
          sc.name || '',
          sc.trend || '',
          sc.drift || '',
          sc.volatility || '',
          sc.spread_bps || '',
          sc.depth || '',
          sc.target_price || '',
          sc.house_edge || '',
          sc.anti_ta ? 'Yes' : 'No',
          sc.formula || '',
          sc.notes || '',
        ]);
      });

      // Auto-fit columns
      worksheet.columns.forEach((column) => {
        column.width = 15;
      });
    }

    // Download
    const buffer = await workbook.xlsx.writeBuffer();
    const blob = new Blob([buffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `session_${session.id}_${new Date().toISOString().split('T')[0]}.xlsx`;
    link.click();
    URL.revokeObjectURL(link.href);

    toastService.success('Đã export session ra Excel');
  } catch (error) {
    console.error('Export Excel error:', error);
    toastService.error('Không thể export Excel');
  }
};

const exportAllSessions = async (format) => {
  if (sessions.value.length === 0) {
    toastService.error('Không có session nào để export');
    return;
  }

  if (format === 'csv') {
    // Export all sessions to single CSV
    const rows = [['All Sessions Export', ''], ['']];
    
    sessions.value.forEach((session, index) => {
      rows.push([`Session ${index + 1}`, '']);
      rows.push(['ID', session.id]);
      rows.push(['Tên', session.name]);
      rows.push(['Trạng thái', session.status]);
      rows.push(['Bắt đầu', session.started_at || '—']);
      rows.push(['Kết thúc', session.ended_at || '—']);
      rows.push(['Ghi chú', session.note || '—']);
      rows.push(['Result Note', session.result?.note || '—']);
      rows.push(['']);
    });

    const csvContent = rows.map(row => row.map(cell => `"${String(cell).replace(/"/g, '""')}"`).join(',')).join('\n');
    const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `all_sessions_${new Date().toISOString().split('T')[0]}.csv`;
    link.click();
    URL.revokeObjectURL(link.href);
    
    toastService.success('Đã export tất cả sessions ra CSV');
  } else {
    // Export all sessions to Excel
    try {
      const workbook = new ExcelJS.Workbook();
      
      sessions.value.forEach((session, index) => {
        const worksheet = workbook.addWorksheet(`Session ${index + 1}`);
        
        worksheet.getCell('A1').value = 'Session Export';
        worksheet.getCell('A1').font = { bold: true, size: 14 };
        
        worksheet.getCell('A3').value = 'ID';
        worksheet.getCell('B3').value = session.id;
        worksheet.getCell('A4').value = 'Tên';
        worksheet.getCell('B4').value = session.name;
        worksheet.getCell('A5').value = 'Trạng thái';
        worksheet.getCell('B5').value = session.status;
        worksheet.getCell('A6').value = 'Bắt đầu';
        worksheet.getCell('B6').value = session.started_at || '—';
        worksheet.getCell('A7').value = 'Kết thúc';
        worksheet.getCell('B7').value = session.ended_at || '—';
        worksheet.getCell('A8').value = 'Ghi chú';
        worksheet.getCell('B8').value = session.note || '—';
        worksheet.getCell('A9').value = 'Result Note';
        worksheet.getCell('B9').value = session.result?.note || '—';
      });

      const buffer = await workbook.xlsx.writeBuffer();
      const blob = new Blob([buffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = `all_sessions_${new Date().toISOString().split('T')[0]}.xlsx`;
      link.click();
      URL.revokeObjectURL(link.href);

      toastService.success('Đã export tất cả sessions ra Excel');
    } catch (error) {
      console.error('Export Excel error:', error);
      toastService.error('Không thể export Excel');
    }
  }
};

onMounted(async () => {
  await Promise.all([fetchScenarios(), fetchSessions(), fetchMonitoring()]);
  
  // Set initial preview symbol if available
  if (scenarios.value.length > 0 && scenarios.value[0].symbol) {
    selectedPreviewSymbol.value = scenarios.value[0].symbol;
    handlePreviewSymbolChange(selectedPreviewSymbol.value);
  }
});

onUnmounted(() => {
  // Cleanup WebSocket subscriptions
  if (selectedPreviewSymbol.value) {
    marketStore.unsubscribeFromSymbol(selectedPreviewSymbol.value);
  }
});
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-white mb-2">Scenario Builder & Session Manager</h1>
        <p class="text-white/60">
          God Mode: cấu hình kịch bản giá, khởi động session và theo dõi simulator realtime
        </p>
      </div>
      <div class="flex gap-3">
        <Button variant="secondary" @click="resetSimulator" :loading="loadingSessions">
          <i class="fas fa-undo mr-2"></i>
          Reset / Replay
        </Button>
        <Button variant="primary" @click="saveScenarios" :loading="loading">
          <i class="fas fa-save mr-2"></i>
          Lưu Scenario
        </Button>
      </div>
    </div>

    <!-- Scenario Builder -->
    <Card title="Scenario Builder (God Mode)">
      <div class="space-y-4">
        <div
          v-for="(scenario, index) in scenarios"
          :key="index"
          class="border border-white/10 rounded-lg p-4 space-y-3 bg-white/5"
        >
          <div class="flex items-start justify-between gap-4">
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 flex-1">
              <Input v-model="scenario.symbol" label="Symbol" placeholder="BTCUSDT" />
              <Input v-model="scenario.name" label="Tên kịch bản" placeholder="Kill Long / Sideway..." />
              <Select
                v-model="scenario.trend"
                :options="trendOptions"
                label="Xu hướng"
                placeholder="Chọn xu hướng"
              />
              <Input v-model="scenario.drift" type="number" step="0.0001" label="Drift" />
              <div class="space-y-1">
                <Select
                  v-model="scenario.volatilityLevel"
                  :options="volatilityOptions"
                  label="Volatility Level"
                  placeholder="Chọn mức biến động"
                  @update:modelValue="(val) => {
                    if (val !== 'custom') {
                      scenario.volatility = val;
                    }
                  }"
                />
                <Input 
                  v-if="scenario.volatilityLevel === 'custom'" 
                  v-model="scenario.volatility" 
                  type="number" 
                  step="0.0001" 
                  label="" 
                  placeholder="Nhập giá trị tùy chỉnh"
                />
                <span class="text-xs text-white/50">Giá trị hiện tại: {{ (scenario.volatility * 100).toFixed(2) }}%</span>
              </div>
              <Input v-model="scenario.spread_bps" type="number" label="Spread (bps)" />
              <Input v-model="scenario.depth" type="number" label="Depth" />
              <Input v-model="scenario.target_price" type="number" label="Target Price" />
              <Input v-model="scenario.house_edge" type="number" step="0.0001" label="House Edge" />
            </div>
            <button
              v-if="scenarios.length > 1"
              class="text-red-400 hover:text-red-200"
              @click="removeScenarioRow(index)"
            >
              <i class="fas fa-trash"></i>
            </button>
          </div>
          
          <!-- Time Range for Scenario Application -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 p-3 bg-purple-500/10 rounded-lg border border-purple-500/20">
            <DateTimeInput 
              v-model="scenario.start_ts" 
              label="Thời gian bắt đầu" 
              placeholder="Chọn thời gian bắt đầu áp dụng"
            />
            <DateTimeInput 
              v-model="scenario.end_ts" 
              label="Thời gian kết thúc" 
              placeholder="Chọn thời gian kết thúc"
            />
            <p class="col-span-2 text-xs text-white/50">
              <i class="fas fa-info-circle mr-1"></i>
              Để trống = áp dụng ngay lập tức và không giới hạn thời gian. Có thể đặt kịch bản theo lịch cố định (ví dụ: 08:00-12:00, cả ngày, v.v.)
            </p>
          </div>
          
          <ToggleSwitch v-model="scenario.anti_ta" label="Anti-TA (làm nhiễu mô hình TA)" />
          <div class="space-y-2">
            <label class="text-sm text-white/80">Formula (sandbox) - biến sẵn có: price, dt, trend, target, drift, volatility</label>
            <MonacoEditor
              v-model="scenario.formula"
              language="javascript"
              theme="vs-dark"
              height="200px"
              placeholder="Ví dụ: price * (1 + drift * dt) + (random.random() - 0.5)"
            />
            <p class="text-xs text-white/60">
              Hỗ trợ autocomplete: gõ "price", "dt", "trend", "target", "drift", "volatility", "math.*", "random.random()"
            </p>
          </div>
          <Input v-model="scenario.notes" label="Ghi chú" placeholder="Giải thích nhanh về kịch bản" />
        </div>

        <div class="flex justify-between items-center">
          <Button variant="secondary" @click="addScenarioRow">
            <i class="fas fa-plus mr-2"></i>
            Thêm kịch bản
          </Button>
          <div class="text-white/60 text-sm">
            Save = lưu DB + áp dụng simulator (không cần restart server)
          </div>
        </div>
      </div>
    </Card>

    <!-- Live Preview -->
    <Card title="Live Preview">
      <div v-if="scenarios.length > 0" class="space-y-6">
        <!-- Symbol Selector -->
        <div class="flex items-center gap-4">
          <label class="text-sm text-white/80">Preview Symbol:</label>
          <Select
            v-model="selectedPreviewSymbol"
            :options="symbolOptions"
            placeholder="Chọn symbol để preview"
            @update:modelValue="handlePreviewSymbolChange"
          />
        </div>

        <!-- Market Data Cards (Compact) -->
        <MarketDataCards
          v-if="selectedPreviewSymbol"
          :symbol="selectedPreviewSymbol"
          :compact="true"
        />

        <!-- Chart Preview (Compact) -->
        <div v-if="selectedPreviewSymbol" class="chart-section">
          <h3 class="text-lg font-semibold text-white mb-3">Real-time Chart</h3>
          <MarketChartPreview
            :symbol="selectedPreviewSymbol"
            :compact="true"
            :height="300"
          />
        </div>

        <!-- Preview Status -->
        <div class="preview-status">
          <div class="flex items-center gap-2 text-sm text-white/60">
            <i :class="[
              'fas',
              marketStore.isConnected ? 'fa-circle text-green-400' : 'fa-circle text-red-400'
            ]"></i>
            <span>
              {{ marketStore.isConnected ? 'Real-time updates active' : 'Connecting to real-time data...' }}
            </span>
          </div>
          <div v-if="marketStore.hasError" class="text-sm text-red-400 mt-1">
            <i class="fas fa-exclamation-triangle mr-1"></i>
            {{ marketStore.error }}
          </div>
        </div>
      </div>
      
      <div v-else class="text-center py-8 text-white/60">
        <i class="fas fa-chart-line text-4xl mb-3 opacity-50"></i>
        <p>Thêm ít nhất một kịch bản để xem preview</p>
      </div>
    </Card>

    <!-- Session Manager -->
    <Card title="Session Manager">
      <div class="flex justify-between items-center mb-4">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 flex-1">
        <Input v-model="sessionForm.name" label="Tên phiên" placeholder="Phiên sáng 08:00" />
        <Input v-model="sessionForm.note" label="Ghi chú" placeholder="Mục tiêu, chiến lược..." />
        <div class="flex items-end">
          <Button class="w-full" variant="primary" @click="startSession" :loading="loadingSessions">
            <i class="fas fa-play mr-2"></i>
            Bắt đầu session
          </Button>
        </div>
      </div>
      <div class="flex gap-2">
        <Button size="sm" variant="secondary" @click="exportAllSessions('csv')" :disabled="!sessions.length">
          <i class="fas fa-file-csv mr-2"></i>Export All CSV
        </Button>
        <Button size="sm" variant="secondary" @click="exportAllSessions('excel')" :disabled="!sessions.length">
          <i class="fas fa-file-excel mr-2"></i>Export All Excel
        </Button>
      </div>
      </div>

      <div class="overflow-x-auto">
        <table class="min-w-full text-left text-white/80">
          <thead class="text-white/60 border-b border-white/10">
            <tr>
              <th class="py-2 pr-4">Tên</th>
              <th class="py-2 pr-4">Trạng thái</th>
              <th class="py-2 pr-4">Bắt đầu</th>
              <th class="py-2 pr-4">Kết thúc</th>
          <th class="py-2 pr-4">Ghi chú</th>
          <th class="py-2 pr-4">Result note</th>
          <th class="py-2 pr-4"></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in sessions" :key="item.id" class="border-b border-white/5">
              <td class="py-2 pr-4 font-semibold text-white">{{ item.name }}</td>
              <td class="py-2 pr-4">
                <span
                  :class="[
                    'px-3 py-1 rounded-full text-xs font-semibold',
                    item.status === 'running' ? 'bg-green-500/20 text-green-300' : 'bg-white/10 text-white/70',
                  ]"
                >
                  {{ item.status }}
                </span>
              </td>
              <td class="py-2 pr-4 text-sm">{{ item.started_at || '—' }}</td>
              <td class="py-2 pr-4 text-sm">{{ item.ended_at || '—' }}</td>
              <td class="py-2 pr-4 text-sm">{{ item.note || '—' }}</td>
              <td class="py-2 pr-4">
                <Input
                  v-model="stopNotes[item.id]"
                  placeholder="Nhập ghi chú kết quả"
                  :disabled="item.status !== 'running'"
                />
              </td>
              <td class="py-2 pr-4 text-right space-x-2">
                <Button
                  v-if="item.status === 'running'"
                  size="sm"
                  variant="secondary"
                  @click="stopSession(item.id)"
                  :loading="loadingSessions"
                >
                  <i class="fas fa-stop mr-2"></i>Dừng
                </Button>
                <Button
                  size="sm"
                  variant="tertiary"
                  @click="replaySession(item.id)"
                  :loading="loadingSessions"
                >
                  <i class="fas fa-undo mr-2"></i>Replay
                </Button>
                <div class="inline-block relative group">
                  <Button
                    size="sm"
                    variant="secondary"
                    @click.stop
                  >
                    <i class="fas fa-download mr-2"></i>Export
                  </Button>
                  <div class="absolute right-0 mt-1 w-32 bg-white/10 backdrop-blur-sm rounded-lg shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-10">
                    <button
                      @click="exportSessionToCSV(item)"
                      class="w-full text-left px-4 py-2 text-sm text-white hover:bg-white/20 rounded-t-lg"
                    >
                      <i class="fas fa-file-csv mr-2"></i>Export CSV
                    </button>
                    <button
                      @click="exportSessionToExcel(item)"
                      class="w-full text-left px-4 py-2 text-sm text-white hover:bg-white/20 rounded-b-lg"
                    >
                      <i class="fas fa-file-excel mr-2"></i>Export Excel
                    </button>
                  </div>
                </div>
              </td>
            </tr>
            <tr v-if="!sessions.length">
              <td colspan="7" class="py-3 text-white/60">Chưa có session nào</td>
            </tr>
          </tbody>
        </table>
      </div>
    </Card>

    <!-- Monitoring -->
    <Card title="Monitoring">
      <div v-if="monitoring" class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div class="bg-white/5 border border-white/10 rounded-lg p-4">
          <p class="text-white/60 text-sm mb-1">Symbols</p>
          <p class="text-xl font-bold text-white">{{ (monitoring.metrics?.symbols || []).join(', ') }}</p>
        </div>
        <div class="bg-white/5 border border-white/10 rounded-lg p-4">
          <p class="text-white/60 text-sm mb-1">Latency (ms)</p>
          <p class="text-xl font-bold text-white">{{ monitoring.metrics?.latency_ms?.toFixed(1) }}</p>
        </div>
        <div class="bg-white/5 border border-white/10 rounded-lg p-4">
          <p class="text-white/60 text-sm mb-1">Scenarios</p>
          <p class="text-xl font-bold text-white">{{ monitoring.metrics?.scenario_count }}</p>
        </div>
        <div class="bg-white/5 border border-white/10 rounded-lg p-4">
          <p class="text-white/60 text-sm mb-1">Cập nhật</p>
          <p class="text-xl font-bold text-white">{{ monitoring.metrics?.last_updated }}</p>
        </div>
      </div>

      <div v-if="monitoring?.snapshot" class="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
        <div class="bg-white/5 border border-white/10 rounded-lg p-4">
          <p class="text-white font-semibold mb-2">Prices</p>
          <ul class="space-y-1 text-white/80 text-sm">
            <li v-for="(price, sym) in monitoring.snapshot.prices" :key="sym">
                  <span class="font-semibold text-white">{{ sym }}</span>:
                  {{ price !== undefined ? Number(price).toFixed(2) : '--' }}
            </li>
          </ul>
        </div>
        <div class="bg-white/5 border border-white/10 rounded-lg p-4">
          <p class="text-white font-semibold mb-2">Trades</p>
          <ul class="space-y-1 text-white/80 text-sm">
            <li v-for="(count, sym) in monitoring.snapshot.trades" :key="sym">
              {{ sym }}: {{ count }} giao dịch
            </li>
          </ul>
        </div>
        <div class="bg-white/5 border border-white/10 rounded-lg p-4">
          <p class="text-white font-semibold mb-2">Positions</p>
          <ul class="space-y-1 text-white/80 text-sm">
            <li v-for="(count, sym) in monitoring.snapshot.positions" :key="sym">
              {{ sym }}: {{ count }} vị thế
            </li>
          </ul>
        </div>
      </div>

      <div class="mt-4 text-white/60 text-sm">
        Monitoring Hub: xem latency, giá cuối, số trades/candles/positions để training đội vận hành.
      </div>
    </Card>

    <!-- Educational Hub - Moved to separate view -->
    <Card title="Quick Reference / Checklist nhanh">
      <div class="space-y-2 text-white/80 text-sm">
        <p class="text-white font-semibold">Checklist nhanh</p>
        <ul class="list-disc list-inside space-y-1">
          <li>Scenario Builder: điều chỉnh drift/volatility/target/house_edge; bật Anti-TA để phá mô hình TA.</li>
          <li>Formula sandbox: dùng biến price, dt, trend, target, drift, volatility; chỉ hỗ trợ math/random/time.</li>
          <li>Session Manager: Start → simulator reset & áp kịch bản hiện tại; Stop kèm ghi chú kết quả; Replay để tải snapshot.</li>
          <li>Repair/Replay: dùng nút Reset/Replay để đưa simulator về trạng thái chuẩn hoặc theo session đã lưu.</li>
          <li>Monitoring: theo dõi latency, trade count, positions; nếu giá không đổi, thử Reset hoặc Replay session.</li>
        </ul>
        <p class="text-white/60 mt-4">
          <i class="fas fa-info-circle mr-2"></i>
          Để xem real-time chart và log panel chi tiết, truy cập <strong>Educational Hub</strong> từ menu.
        </p>
      </div>
    </Card>
  </div>
</template>


