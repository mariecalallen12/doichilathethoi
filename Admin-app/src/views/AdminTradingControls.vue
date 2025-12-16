<script setup>
import { ref, onMounted } from 'vue';
import api from '../services/api';
import toastService from '../services/toast';
import Card from '../components/ui/Card.vue';
import Input from '../components/ui/Input.vue';
import Button from '../components/ui/Button.vue';
import Table from '../components/ui/Table.vue';

const platformStats = ref({
  totalUsers: 0,
  totalPositions: 0,
  averageWinRate: 0,
  platformVolume: 0,
});

const riskMetrics = ref({
  highRiskUsers: 0,
  averageLeverage: 0,
  marginCallRisk: 0,
});

const topPerformers = ref([]);
const loading = ref(false);

const winRateControl = ref({
  userId: '',
  targetWinRate: 50,
});

const positionOverride = ref({
  positionId: '',
  outcome: 'profit',
  amount: 0,
});

const userPerformanceSearch = ref('');
const userPerformance = ref(null);
const loadingPerformance = ref(false);

const fetchData = async () => {
  loading.value = true;
  try {
    // Fetch platform stats
    const statsResponse = await api.get('/api/admin/platform/stats');
    const statsData = statsResponse.data?.data || statsResponse.data || {};
    
    if (statsData) {
      platformStats.value = {
        totalUsers: statsData.total_users || 0,
        totalPositions: statsData.total_positions || 0,
        averageWinRate: statsData.average_win_rate || 0,
        platformVolume: statsData.platform_volume || 0,
      };
      
      if (statsData.risk_metrics) {
        riskMetrics.value = {
          highRiskUsers: statsData.risk_metrics.high_risk_users || 0,
          averageLeverage: statsData.risk_metrics.average_leverage || 0,
          marginCallRisk: statsData.risk_metrics.margin_call_risk || 0,
        };
      }
      
      if (statsData.top_performers) {
        topPerformers.value = statsData.top_performers.map((p, index) => ({
          rank: index + 1,
          userId: p.user_id || p.userId,
          winRate: p.win_rate || p.winRate,
          trades: p.trades || 0,
        }));
      }
    }
  } catch (error) {
    console.error('Fetch data error:', error);
    toastService.error('Không thể tải dữ liệu');
  } finally {
    loading.value = false;
  }
};

const handleSetWinRate = async () => {
  if (!winRateControl.value.userId || !winRateControl.value.targetWinRate) {
    toastService.warning('Vui lòng nhập đầy đủ thông tin');
    return;
  }
  
  try {
    await api.post('/api/admin/trading-adjustments/win-rate', {
      user_id: winRateControl.value.userId,
      target_win_rate: winRateControl.value.targetWinRate,
    });
    toastService.success('Đã thiết lập win rate');
    winRateControl.value = { userId: '', targetWinRate: 50 };
    await fetchData();
  } catch (error) {
    console.error('Set win rate error:', error);
    toastService.error(error.message || 'Không thể thiết lập win rate');
  }
};

const handlePositionOverride = async () => {
  if (!positionOverride.value.positionId || !positionOverride.value.amount) {
    toastService.warning('Vui lòng nhập đầy đủ thông tin');
    return;
  }
  
  try {
    await api.post('/api/admin/trading-adjustments/position-override', {
      position_id: positionOverride.value.positionId,
      outcome: positionOverride.value.outcome,
      amount: positionOverride.value.amount,
    });
    toastService.success('Đã ghi đè vị thế');
    positionOverride.value = { positionId: '', outcome: 'profit', amount: 0 };
    await fetchData();
  } catch (error) {
    console.error('Position override error:', error);
    toastService.error(error.message || 'Không thể ghi đè vị thế');
  }
};

const handleSearchUserPerformance = async () => {
  if (!userPerformanceSearch.value.trim()) {
    toastService.warning('Vui lòng nhập User ID');
    return;
  }
  
  loadingPerformance.value = true;
  try {
    const response = await api.get(`/api/admin/users/${userPerformanceSearch.value.trim()}/performance`);
    const data = response.data?.data || response.data || {};
    userPerformance.value = {
      user_id: userPerformanceSearch.value.trim(),
      win_rate: data.win_rate || 0,
      total_trades: data.total_trades || 0,
      total_volume: data.total_volume || 0,
      profit_loss: data.profit_loss || 0,
      current_win_rate: data.current_win_rate || data.win_rate || 0,
    };
  } catch (error) {
    console.error('Fetch user performance error:', error);
    toastService.error('Không thể tải thông tin hiệu suất người dùng');
    userPerformance.value = null;
  } finally {
    loadingPerformance.value = false;
  }
};

const handleResetUserSettings = async () => {
  if (!userPerformance.value?.user_id) {
    return;
  }
  
  if (!confirm('Bạn có chắc chắn muốn reset cài đặt win rate về mặc định cho user này?')) {
    return;
  }
  
  loadingPerformance.value = true;
  try {
    await api.post('/api/admin/trading-adjustments/reset-win-rate', {
      user_id: userPerformance.value.user_id,
    });
    toastService.success('Đã reset cài đặt win rate');
    await handleSearchUserPerformance();
    await fetchData();
  } catch (error) {
    console.error('Reset user settings error:', error);
    toastService.error('Không thể reset cài đặt');
  } finally {
    loadingPerformance.value = false;
  }
};

onMounted(() => {
  fetchData();
});
</script>

<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div>
      <h1 class="text-3xl font-bold text-white mb-2">Điều khiển giao dịch</h1>
      <p class="text-white/60">Quản lý và điều chỉnh giao dịch hệ thống</p>
    </div>

    <!-- Platform Overview -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <Card>
        <p class="text-white/60 text-sm mb-1">Tổng số user</p>
        <p class="text-3xl font-bold text-white">{{ platformStats.totalUsers.toLocaleString() }}</p>
      </Card>
      <Card>
        <p class="text-white/60 text-sm mb-1">Tổng số vị thế</p>
        <p class="text-3xl font-bold text-white">{{ platformStats.totalPositions.toLocaleString() }}</p>
      </Card>
      <Card>
        <p class="text-white/60 text-sm mb-1">Tỷ lệ thắng trung bình</p>
        <p class="text-3xl font-bold text-white">{{ platformStats.averageWinRate }}%</p>
      </Card>
      <Card>
        <p class="text-white/60 text-sm mb-1">Khối lượng platform</p>
        <p class="text-3xl font-bold text-white">${{ platformStats.platformVolume.toLocaleString() }}</p>
      </Card>
    </div>

    <!-- Risk Management -->
    <Card title="Quản lý rủi ro">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <p class="text-white/60 text-sm mb-1">User rủi ro cao</p>
          <p class="text-2xl font-bold text-white">{{ riskMetrics.highRiskUsers }}</p>
        </div>
        <div>
          <p class="text-white/60 text-sm mb-1">Đòn bẩy trung bình</p>
          <p class="text-2xl font-bold text-white">{{ riskMetrics.averageLeverage }}x</p>
        </div>
        <div>
          <p class="text-white/60 text-sm mb-1">Rủi ro call margin</p>
          <p class="text-2xl font-bold text-white">{{ riskMetrics.marginCallRisk }}%</p>
        </div>
      </div>
    </Card>

    <!-- User Performance Lookup -->
    <Card title="Tra cứu hiệu suất người dùng">
      <div class="space-y-4">
        <div class="flex items-center gap-2">
          <Input
            v-model="userPerformanceSearch"
            placeholder="Nhập User ID để tra cứu"
            class="flex-1"
            @keyup.enter="handleSearchUserPerformance"
          />
          <Button variant="primary" @click="handleSearchUserPerformance" :loading="loadingPerformance">
            <i class="fas fa-search mr-2"></i>
            Tìm kiếm
          </Button>
        </div>
        
        <div v-if="userPerformance" class="space-y-4">
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card padding="p-4">
              <p class="text-white/60 text-sm mb-1">Win Rate</p>
              <p class="text-white text-2xl font-bold">{{ userPerformance.win_rate.toFixed(1) }}%</p>
            </Card>
            <Card padding="p-4">
              <p class="text-white/60 text-sm mb-1">Tổng giao dịch</p>
              <p class="text-white text-2xl font-bold">{{ userPerformance.total_trades.toLocaleString() }}</p>
            </Card>
            <Card padding="p-4">
              <p class="text-white/60 text-sm mb-1">Tổng khối lượng</p>
              <p class="text-white text-2xl font-bold">${{ userPerformance.total_volume.toLocaleString() }}</p>
            </Card>
            <Card padding="p-4">
              <p class="text-white/60 text-sm mb-1">Profit/Loss</p>
              <p :class="['text-white text-2xl font-bold', userPerformance.profit_loss >= 0 ? 'text-green-400' : 'text-red-400']">
                ${{ userPerformance.profit_loss.toLocaleString() }}
              </p>
            </Card>
          </div>
          
          <div v-if="userPerformance.current_win_rate !== userPerformance.win_rate" class="p-3 bg-yellow-500/10 border border-yellow-500/30 rounded-lg">
            <p class="text-yellow-400 text-sm">
              <i class="fas fa-info-circle mr-2"></i>
              Win rate hiện tại: {{ userPerformance.current_win_rate.toFixed(1) }}% 
              (Win rate gốc: {{ userPerformance.win_rate.toFixed(1) }}%)
            </p>
          </div>
          
          <div class="flex items-center justify-end">
            <Button variant="warning" @click="handleResetUserSettings" :loading="loadingPerformance">
              <i class="fas fa-undo mr-2"></i>
              Reset về mặc định
            </Button>
          </div>
        </div>
      </div>
    </Card>

    <!-- Win Rate Control -->
    <Card title="Điều khiển Win Rate">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Input
          v-model="winRateControl.userId"
          label="User ID"
          placeholder="Nhập User ID"
        />
        <Input
          v-model="winRateControl.targetWinRate"
          label="Target Win Rate (%)"
          type="number"
        />
        <div class="flex items-end">
          <Button variant="primary" @click="handleSetWinRate" full-width>
            Thiết lập Win Rate
          </Button>
        </div>
      </div>
    </Card>

    <!-- Position Override -->
    <Card title="Ghi đè vị thế">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Input
          v-model="positionOverride.positionId"
          label="Position ID"
          placeholder="Nhập Position ID"
        />
        <div>
          <label class="block text-sm font-medium text-white/80 mb-2">Kết quả</label>
          <select
            v-model="positionOverride.outcome"
            class="w-full px-4 py-3 rounded-lg bg-white/10 border border-white/20 text-white"
          >
            <option value="profit">Profit</option>
            <option value="loss">Loss</option>
          </select>
        </div>
        <Input
          v-model="positionOverride.amount"
          label="Số tiền"
          type="number"
        />
        <div class="flex items-end">
          <Button variant="primary" @click="handlePositionOverride" full-width>
            Ghi đè
          </Button>
        </div>
      </div>
    </Card>

    <!-- Trading Adjustments History -->
    <TradingAdjustmentsHistory />

    <!-- Top Performers -->
    <Card title="Top Performers">
      <Table
        :headers="[
          { key: 'rank', label: 'Rank' },
          { key: 'userId', label: 'User ID' },
          { key: 'winRate', label: 'Win Rate' },
          { key: 'trades', label: 'Trades' },
        ]"
        :data="topPerformers"
      >
        <template #default="{ data }">
          <tr
            v-for="performer in data"
            :key="performer.rank"
            class="border-b border-white/5 hover:bg-white/5"
          >
            <td class="px-4 py-3 text-white font-semibold">#{{ performer.rank }}</td>
            <td class="px-4 py-3 text-white/80">{{ performer.userId }}</td>
            <td class="px-4 py-3 text-green-400 font-semibold">{{ performer.winRate }}%</td>
            <td class="px-4 py-3 text-white/80">{{ performer.trades }}</td>
          </tr>
        </template>
      </Table>
    </Card>
  </div>
</template>

