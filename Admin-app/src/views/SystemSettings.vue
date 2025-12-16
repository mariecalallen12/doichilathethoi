<script setup>
import { ref, onMounted } from 'vue';
import { useAppStore } from '../store/app';
import api from '../services/api';
import toastService from '../services/toast';
import GeneralSettings from '../components/settings/GeneralSettings.vue';
import ToggleSwitch from '../components/settings/ToggleSwitch.vue';
import AllowedOriginsList from '../components/settings/AllowedOriginsList.vue';
import ChartDisplayConfig from '../components/settings/ChartDisplayConfig.vue';
import Input from '../components/ui/Input.vue';
import Card from '../components/ui/Card.vue';
import Button from '../components/ui/Button.vue';

const appStore = useAppStore();
const activeTab = ref('general');
const settings = ref({ ...appStore.settings });
const loading = ref(false);

const tabs = [
  { id: 'general', label: 'Chung', icon: 'fa-cog' },
  { id: 'security', label: 'Bảo mật', icon: 'fa-shield-alt' },
  { id: 'trading', label: 'Giao dịch', icon: 'fa-exchange-alt' },
  { id: 'chart', label: 'Chart Display', icon: 'fa-chart-line' },
  { id: 'notifications', label: 'Thông báo', icon: 'fa-bell' },
  { id: 'api', label: 'API', icon: 'fa-code' },
  { id: 'system', label: 'Hệ thống', icon: 'fa-info-circle' },
];

const fetchSettings = async () => {
  loading.value = true;
  try {
    const response = await api.get('/api/admin/settings');
    const data = response.data?.data || response.data || {};
    
    // Fetch auto approve registration setting separately
    let autoApproveRegistration = false;
    try {
      const autoApproveResponse = await api.get('/api/admin/settings/auto-approve-registration');
      autoApproveRegistration = autoApproveResponse.data?.data?.enabled || false;
    } catch (error) {
      console.warn('Could not fetch auto approve registration setting:', error);
    }

    // Fetch market display settings separately
    let marketDisplay = {};
    try {
      const marketDisplayResponse = await api.get('/api/admin/settings/market-display');
      marketDisplay = marketDisplayResponse.data?.data || {};
    } catch (error) {
      console.warn('Could not fetch market display settings:', error);
    }
    
    // Map backend settings to frontend format
    settings.value = {
      ...appStore.settings,
      ...data,
      // Map specific fields if needed
      platformName: data.platform_name || settings.value.platformName,
      platformURL: data.platform_url || settings.value.platformURL,
      supportEmail: data.support_email || settings.value.supportEmail,
      minDeposit: data.minDeposit || data.min_deposit || settings.value.minDeposit,
      maxDeposit: data.maxDeposit || data.max_deposit || settings.value.maxDeposit,
      minWithdrawal: data.minWithdraw || data.min_withdraw || settings.value.minWithdrawal,
      maxWithdrawal: data.maxWithdraw || data.max_withdraw || settings.value.maxWithdrawal,
      tradingFee: data.tradingFee || data.trading_fee || settings.value.tradingFee,
      withdrawalFee: data.withdrawalFee || data.withdrawal_fee || settings.value.withdrawalFee,
      maxLeverage: data.maxLeverage || data.max_leverage || settings.value.maxLeverage,
      maxOpenPositions: data.maxOpenPositions || data.max_open_positions || settings.value.maxOpenPositions,
      largeTradeAlertThreshold: data.largeTradeAlertThreshold || data.large_trade_alert_threshold || settings.value.largeTradeAlertThreshold || 10000,
      maintenanceMode: data.maintenanceMode || data.maintenance_mode || settings.value.maintenanceMode,
      autoApproveRegistration: autoApproveRegistration,
      // Market display config
      marketSpreadBps: marketDisplay.spread_bps ?? 8,
      marketVolatility: marketDisplay.volatility ?? 0.002,
      marketDepth: marketDisplay.depth ?? 10,
      marketVolumeMultiplier: marketDisplay.volume_24h_multiplier ?? 1,
      marketCapMultiplier: marketDisplay.market_cap_multiplier ?? 1,
      candleUpColor: marketDisplay.candle_style?.upColor ?? '#10b981',
      candleDownColor: marketDisplay.candle_style?.downColor ?? '#ef4444',
      candleWickUpColor: marketDisplay.candle_style?.wickUpColor ?? '#10b981',
      candleWickDownColor: marketDisplay.candle_style?.wickDownColor ?? '#ef4444',
    };
  } catch (error) {
    console.error('Fetch settings error:', error);
    toastService.error('Không thể tải cài đặt');
  } finally {
    loading.value = false;
  }
};

const handleChartConfigUpdated = (config) => {
  // Update local settings with new chart config
  settings.value.candleUpColor = config.upColor;
  settings.value.candleDownColor = config.downColor;
  settings.value.candleWickUpColor = config.wickUpColor;
  settings.value.candleWickDownColor = config.wickDownColor;
};

const saveSettings = async () => {
  loading.value = true;
  try {
    // Map frontend settings to backend format
    const settingsPayload = {
      platform_name: settings.value.platformName,
      platform_url: settings.value.platformURL,
      support_email: settings.value.supportEmail,
      timezone: settings.value.timezone,
      default_language: settings.value.defaultLanguage,
      maintenance_mode: settings.value.maintenanceMode,
      allow_registrations: settings.value.allowRegistrations,
      session_timeout: settings.value.sessionTimeout,
      password_min_length: settings.value.passwordMinLength,
      max_login_attempts: settings.value.maxLoginAttempts,
      lockout_duration: settings.value.lockoutDuration,
      two_factor_required: settings.value.twoFactorRequired,
      email_verification: settings.value.emailVerification,
      social_login: settings.value.socialLogin,
      min_deposit: settings.value.minDeposit,
      max_deposit: settings.value.maxDeposit,
      min_withdraw: settings.value.minWithdrawal,
      max_withdraw: settings.value.maxWithdrawal,
      trading_fee: settings.value.tradingFee,
      withdrawal_fee: settings.value.withdrawalFee,
      max_leverage: settings.value.maxLeverage,
      max_open_positions: settings.value.maxOpenPositions,
      large_trade_alert_threshold: settings.value.largeTradeAlertThreshold,
      auto_approval: settings.value.autoApproval,
      email_notifications: settings.value.emailNotifications,
      sms_notifications: settings.value.smsNotifications,
      push_notifications: settings.value.pushNotifications,
      daily_reports: settings.value.dailyReports,
      weekly_reports: settings.value.weeklyReports,
      monthly_reports: settings.value.monthlyReports,
      rate_limit: settings.value.rateLimit,
      enable_webhooks: settings.value.enableWebhooks,
      webhook_url: settings.value.webhookURL,
      api_version: settings.value.apiVersion,
      enable_cors: settings.value.enableCORS,
    };
    
    await api.put('/api/admin/settings', settingsPayload);
    
    // Save auto approve registration setting separately
    try {
      await api.put('/api/admin/settings/auto-approve-registration', {
        enabled: settings.value.autoApproveRegistration || false
      });
    } catch (error) {
      console.error('Save auto approve registration setting error:', error);
      toastService.error('Không thể lưu cài đặt tự động phê duyệt đăng ký');
    }

    // Save market display settings separately
    try {
      await api.put('/api/admin/settings/market-display', {
        spread_bps: Number(settings.value.marketSpreadBps || 8),
        volatility: Number(settings.value.marketVolatility || 0.002),
        depth: Number(settings.value.marketDepth || 10),
        volume_24h_multiplier: Number(settings.value.marketVolumeMultiplier || 1),
        market_cap_multiplier: Number(settings.value.marketCapMultiplier || 1),
        candle_style: {
          upColor: settings.value.candleUpColor,
          downColor: settings.value.candleDownColor,
          borderVisible: false,
          wickUpColor: settings.value.candleWickUpColor,
          wickDownColor: settings.value.candleWickDownColor,
        },
      });
    } catch (error) {
      console.error('Save market display settings error:', error);
      toastService.error('Không thể lưu cấu hình hiển thị Market');
    }
    await appStore.updateSettings(settings.value);
    toastService.success('Đã lưu cài đặt');
  } catch (error) {
    console.error('Save settings error:', error);
    toastService.error(error.message || 'Không thể lưu cài đặt');
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchSettings();
});
</script>

<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-white mb-2">Cài đặt hệ thống</h1>
        <p class="text-white/60">Cấu hình và quản lý hệ thống</p>
      </div>
      <Button variant="primary" @click="saveSettings" :loading="loading">
        <i class="fas fa-save mr-2"></i>
        Lưu cài đặt
      </Button>
    </div>

    <!-- Tabs -->
    <div class="flex items-center gap-2 border-b border-white/10">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        :class="[
          'px-4 py-2 font-medium transition-colors border-b-2 flex items-center gap-2',
          activeTab === tab.id
            ? 'text-primary border-primary'
            : 'text-white/60 border-transparent hover:text-white',
        ]"
        @click="activeTab = tab.id"
      >
        <i :class="['fas', tab.icon]"></i>
        {{ tab.label }}
      </button>
    </div>

    <!-- General Settings -->
    <GeneralSettings
      v-if="activeTab === 'general'"
      :settings="settings"
      @update:settings="settings = { ...settings, ...$event }"
    />

    <!-- Security Settings -->
    <Card v-if="activeTab === 'security'" title="Cài đặt bảo mật">
      <div class="space-y-4">
        <Input v-model="settings.sessionTimeout" label="Thời gian chờ phiên (phút)" type="number" />
        <Input v-model="settings.passwordMinLength" label="Độ dài mật khẩu tối thiểu" type="number" />
        <Input v-model="settings.maxLoginAttempts" label="Số lần đăng nhập tối đa" type="number" />
        <Input v-model="settings.lockoutDuration" label="Thời gian khóa (phút)" type="number" />
        <div class="border-t border-white/10 pt-4 space-y-2">
          <ToggleSwitch v-model="settings.twoFactorRequired" label="Yêu cầu 2FA" />
          <ToggleSwitch v-model="settings.emailVerification" label="Xác thực email" />
          <ToggleSwitch v-model="settings.socialLogin" label="Cho phép đăng nhập mạng xã hội" />
        </div>
      </div>
    </Card>

    <!-- Trading Settings -->
    <Card v-if="activeTab === 'trading'" title="Cài đặt giao dịch">
      <div class="space-y-4">
        <Input v-model="settings.minDeposit" label="Nạp tiền tối thiểu ($)" type="number" />
        <Input v-model="settings.maxDeposit" label="Nạp tiền tối đa ($)" type="number" />
        <Input v-model="settings.minWithdrawal" label="Rút tiền tối thiểu ($)" type="number" />
        <Input v-model="settings.maxWithdrawal" label="Rút tiền tối đa ($)" type="number" />
        <Input v-model="settings.tradingFee" label="Phí giao dịch (%)" type="number" />
        <Input v-model="settings.withdrawalFee" label="Phí rút tiền ($)" type="number" />
        <Input v-model="settings.maxLeverage" label="Đòn bẩy tối đa (x)" type="number" />
        <Input v-model="settings.maxOpenPositions" label="Vị thế mở tối đa" type="number" />
        <Input v-model="settings.largeTradeAlertThreshold" label="Ngưỡng cảnh báo giao dịch lớn ($)" type="number" />
        <ToggleSwitch v-model="settings.autoApproval" label="Tự động phê duyệt giao dịch nhỏ" />

        <div class="border-t border-white/10 pt-4 space-y-3">
          <h3 class="text-white font-semibold text-sm">Cấu hình hiển thị Market</h3>
          <p class="text-xs text-white/60">
            Điều chỉnh spread, độ biến động và độ sâu orderbook cho Market-Maker Engine.
          </p>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Input
              v-model="settings.marketSpreadBps"
              label="Spread (bps)"
              type="number"
              min="0"
              max="1000"
            />
            <Input
              v-model="settings.marketVolatility"
              label="Độ biến động"
              type="number"
              step="0.0001"
              min="0"
              max="0.1"
            />
            <Input
              v-model="settings.marketDepth"
              label="Độ sâu Orderbook"
              type="number"
              min="1"
              max="100"
            />
            <Input
              v-model="settings.marketVolumeMultiplier"
              label="Volume 24h multiplier"
              type="number"
              step="0.1"
            />
            <Input
              v-model="settings.marketCapMultiplier"
              label="Market Cap multiplier"
              type="number"
              step="0.1"
            />
            <Input
              v-model="settings.candleUpColor"
              label="Màu nến tăng"
              type="color"
            />
            <Input
              v-model="settings.candleDownColor"
              label="Màu nến giảm"
              type="color"
            />
            <Input
              v-model="settings.candleWickUpColor"
              label="Wick tăng"
              type="color"
            />
            <Input
              v-model="settings.candleWickDownColor"
              label="Wick giảm"
              type="color"
            />
          </div>
        </div>
      </div>
    </Card>

    <!-- Chart Display Settings -->
    <div v-if="activeTab === 'chart'">
      <ChartDisplayConfig @configUpdated="handleChartConfigUpdated" />
    </div>

    <!-- Notification Settings -->
    <Card v-if="activeTab === 'notifications'" title="Cài đặt thông báo">
      <div class="space-y-2">
        <ToggleSwitch v-model="settings.emailNotifications" label="Thông báo email" />
        <ToggleSwitch v-model="settings.smsNotifications" label="Thông báo SMS" />
        <ToggleSwitch v-model="settings.pushNotifications" label="Thông báo đẩy" />
        <ToggleSwitch v-model="settings.dailyReports" label="Báo cáo hàng ngày" />
        <ToggleSwitch v-model="settings.weeklyReports" label="Báo cáo hàng tuần" />
        <ToggleSwitch v-model="settings.monthlyReports" label="Báo cáo hàng tháng" />
      </div>
    </Card>

    <!-- API Settings -->
    <Card v-if="activeTab === 'api'" title="Cài đặt API">
      <div class="space-y-4">
        <Input v-model="settings.rateLimit" label="Giới hạn tốc độ (requests/hour)" type="number" />
        <Input v-model="settings.webhookURL" label="Webhook URL" />
        <Input v-model="settings.apiVersion" label="Phiên bản API" />
        <ToggleSwitch v-model="settings.enableWebhooks" label="Bật webhook" />
        <ToggleSwitch v-model="settings.enableCORS" label="Bật CORS" />
        
        <div v-if="settings.enableCORS" class="mt-6">
          <AllowedOriginsList />
        </div>
      </div>
    </Card>

    <!-- System Info -->
    <Card v-if="activeTab === 'system'" title="Thông tin hệ thống">
      <div class="space-y-3">
        <div class="flex items-center justify-between py-2 border-b border-white/10">
          <span class="text-white/60">Phiên bản</span>
          <span class="text-white font-semibold">v2.0.0</span>
        </div>
        <div class="flex items-center justify-between py-2 border-b border-white/10">
          <span class="text-white/60">Ngày build</span>
          <span class="text-white font-semibold">2024-12-05</span>
        </div>
        <div class="flex items-center justify-between py-2">
          <span class="text-white/60">Môi trường</span>
          <span class="text-white font-semibold">Production</span>
        </div>
      </div>
    </Card>
  </div>
</template>

