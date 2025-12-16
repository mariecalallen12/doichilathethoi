<script setup>
import { onBeforeUnmount, onMounted, reactive, ref, nextTick, computed } from "vue";
import { useRouter } from "vue-router";
import { useI18n } from "vue-i18n";
import ParticleCanvas from "../components/ParticleCanvas.vue";
import AOS from "aos";
import { authApi } from "../services/api/auth";
import { getDefaultRegistrationConfig } from "../config/registrationFields";

const router = useRouter();
const { t } = useI18n();

const theme = ref("dark");
const mobileOpen = ref(false);
const currentLang = ref("vi");
const languages = [
  { value: "vi", label: "VI" },
  { value: "en", label: "EN" },
];

const toggleTheme = () => {
  theme.value = theme.value === "dark" ? "light" : "dark";
  document.documentElement.setAttribute("data-theme", theme.value);
};

const { locale } = useI18n();
const changeLang = (val) => {
  currentLang.value = val;
  locale.value = val;
};

// Form state
const formData = reactive({
  fullName: "",
  email: "",
  phone: "",
  dateOfBirth: "",
  password: "",
  confirmPassword: "",
  customId: "",
  country: "",
  tradingExperience: "",
  referralCode: "",
  agreeTerms: false,
  agreeMarketing: false,
});

const errors = reactive({
  fullName: "",
  email: "",
  phone: "",
  dateOfBirth: "",
  password: "",
  confirmPassword: "",
  customId: "",
  country: "",
  agreeTerms: "",
});

const showPassword = ref(false);
const showConfirmPassword = ref(false);
const isSubmitting = ref(false);
const countryDropdownOpen = ref(false);
const experienceDropdownOpen = ref(false);
const registrationConfig = ref(getDefaultRegistrationConfig());
const loadingConfig = ref(false);
const configLoaded = ref(true);
const currentConfigVersion = ref(null);
const pollingInterval = ref(null);

const countries = [
  "Việt Nam",
  "United States",
  "United Kingdom",
  "Australia",
  "Canada",
  "Germany",
  "France",
  "Japan",
  "Singapore",
  "Thailand",
];

const tradingExperiences = [
  "Chưa có kinh nghiệm",
  "Dưới 1 năm",
  "1-3 năm",
  "3-5 năm",
  "Trên 5 năm",
];

// Validation functions
const validateEmail = (email) => {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
};

const validatePhone = (phone) => {
  const re = /^\+?[0-9]{10,15}$/;
  return re.test(phone.replace(/\s/g, ""));
};

// Get field config by key
const getFieldConfig = (key) => {
  if (!registrationConfig.value || !registrationConfig.value.fields) {
    return null;
  }
  return registrationConfig.value.fields.find(f => f.key === key);
};

// Check if field is enabled
const isFieldEnabled = (key) => {
  const field = getFieldConfig(key);
  return field ? field.enabled : false;
};

// Check if field is required
const isFieldRequired = (key) => {
  const field = getFieldConfig(key);
  return field ? field.required : false;
};

// Get enabled fields for rendering
const enabledFields = computed(() => {
  if (!registrationConfig.value || !registrationConfig.value.fields) {
    return [];
  }
  return registrationConfig.value.fields.filter(f => f.enabled);
});

const validateForm = () => {
  let isValid = true;
  
  // Reset all errors
  Object.keys(errors).forEach(key => {
    errors[key] = "";
  });

  // Validate only enabled and required fields
  if (isFieldEnabled('fullName') && isFieldRequired('fullName')) {
    if (!formData.fullName.trim()) {
      errors.fullName = "Vui lòng nhập họ và tên";
      isValid = false;
    }
  }

  if (isFieldEnabled('email') && isFieldRequired('email')) {
    if (!formData.email.trim()) {
      errors.email = "Vui lòng nhập email";
      isValid = false;
    } else if (!validateEmail(formData.email)) {
      errors.email = "Email không hợp lệ";
      isValid = false;
    }
  }

  if (isFieldEnabled('phone') && isFieldRequired('phone')) {
    if (!formData.phone.trim()) {
      errors.phone = "Vui lòng nhập số điện thoại";
      isValid = false;
    } else if (!validatePhone(formData.phone)) {
      errors.phone = "Số điện thoại không hợp lệ";
      isValid = false;
    }
  }

  if (isFieldEnabled('password') && isFieldRequired('password')) {
    if (!formData.password) {
      errors.password = "Vui lòng nhập mật khẩu";
      isValid = false;
    } else if (formData.password.length < 8) {
      errors.password = "Mật khẩu phải có ít nhất 8 ký tự";
      isValid = false;
    }
  }

  if (isFieldEnabled('confirmPassword') && isFieldRequired('confirmPassword')) {
    if (!formData.confirmPassword) {
      errors.confirmPassword = "Vui lòng xác nhận mật khẩu";
      isValid = false;
    } else if (formData.password !== formData.confirmPassword) {
      errors.confirmPassword = "Mật khẩu không khớp";
      isValid = false;
    }
  }

  // Validate customId if provided (optional field)
  if (isFieldEnabled('customId') && formData.customId.trim()) {
    const customIdValue = formData.customId.trim();
    const customIdRegex = /^[a-zA-Z0-9_-]{3,50}$/;
    if (!customIdRegex.test(customIdValue)) {
      errors.customId = "ID tùy chỉnh chỉ được chứa chữ cái, số, dấu gạch dưới và dấu gạch ngang (3-50 ký tự)";
      isValid = false;
    }
  }

  if (isFieldEnabled('country') && isFieldRequired('country')) {
    if (!formData.country) {
      errors.country = "Vui lòng chọn quốc gia";
      isValid = false;
    }
  }

  if (isFieldEnabled('agreeTerms') && isFieldRequired('agreeTerms')) {
    if (!formData.agreeTerms) {
      errors.agreeTerms = "Vui lòng đồng ý với điều khoản sử dụng";
      isValid = false;
    }
  }

  return isValid;
};

const errorMessage = ref("");

const handleSubmit = async () => {
  errorMessage.value = "";
  
  if (!validateForm()) {
    return;
  }

  isSubmitting.value = true;

  try {
    // Don't send locked fields (country, tradingExperience, referralCode)
    // These are set automatically by backend with default values
    const response = await authApi.register({
      fullName: formData.fullName,
      displayName: formData.fullName || formData.phone,
      email: formData.email,
      phone: formData.phone,
      password: formData.password,
      customId: formData.customId.trim() || null,
      // referralCode is locked - backend will set default value
      agreeTerms: formData.agreeTerms
    });

    // Show success message
    if (response.needsApproval) {
      alert("Đăng ký thành công! Tài khoản của bạn đang chờ phê duyệt từ quản trị viên.");
    } else {
      alert("Đăng ký thành công!");
    }
    
    // Redirect to login
    router.push('/login');
  } catch (error) {
    if (error.response?.data?.detail) {
      errorMessage.value = error.response.data.detail;
    } else if (error.message) {
      errorMessage.value = error.message;
    } else {
      errorMessage.value = "Đăng ký thất bại. Vui lòng thử lại.";
    }
  } finally {
    isSubmitting.value = false;
  }
};

const observeElems = () => {
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) entry.target.classList.add("is-visible");
      });
    },
    { threshold: 0.2 }
  );
  document.querySelectorAll(".observe").forEach((el) => observer.observe(el));
};

const handleClickOutside = (event) => {
  const countryDropdown = event.target.closest('[data-dropdown="country"]');
  const experienceDropdown = event.target.closest('[data-dropdown="experience"]');
  
  if (!countryDropdown) {
    countryDropdownOpen.value = false;
  }
  if (!experienceDropdown) {
    experienceDropdownOpen.value = false;
  }
};

// Load registration fields configuration
const loadRegistrationConfig = async (silent = false) => {
  if (!silent) {
  loadingConfig.value = true;
  }
  try {
    const config = await authApi.getRegistrationFieldsConfig(currentConfigVersion.value);
    console.log('Loaded registration config:', config);
    
    // Check if version changed
    const newVersion = config?.version || config?.data?.version || null;
    if (currentConfigVersion.value !== null && newVersion !== null && newVersion === currentConfigVersion.value) {
      // Version unchanged, no need to update
      console.log('Config version unchanged, skipping update');
      return;
    }
    
    // Handle different response structures
    let configData = null;
    if (config && config.fields) {
      // Direct structure: { fields: [...] }
      configData = config;
      console.log('Using direct config structure, fields count:', config.fields.length);
    } else if (config && config.data && config.data.fields) {
      // Nested structure: { data: { fields: [...] } }
      configData = config.data;
      console.log('Using nested config structure, fields count:', config.data.fields.length);
    } else {
      // Use default config if API returns null or invalid data
      console.warn('Invalid config structure, using default config');
      configData = getDefaultRegistrationConfig();
    }
    
    // Update config and version
    registrationConfig.value = configData;
    currentConfigVersion.value = configData?.version || config?.version || null;
    
    // Log enabled/disabled fields for debugging
    if (registrationConfig.value && registrationConfig.value.fields) {
      const enabledFields = registrationConfig.value.fields.filter(f => f.enabled);
      const disabledFields = registrationConfig.value.fields.filter(f => !f.enabled);
      console.log('Enabled fields:', enabledFields.map(f => f.key));
      console.log('Disabled fields:', disabledFields.map(f => f.key));
      console.log('Config version:', currentConfigVersion.value);
      configLoaded.value = true;
    } else {
      configLoaded.value = true;
    }
  } catch (error) {
    console.error('Failed to load registration config:', error);
    // Use default config on error
    registrationConfig.value = getDefaultRegistrationConfig();
    configLoaded.value = true;
  } finally {
    if (!silent) {
    loadingConfig.value = false;
    }
  }
};

// Start polling for config updates
const startConfigPolling = () => {
  // Poll every 30 seconds
  pollingInterval.value = setInterval(() => {
    loadRegistrationConfig(true); // Silent reload
  }, 30000);
};

// Stop polling
const stopConfigPolling = () => {
  if (pollingInterval.value) {
    clearInterval(pollingInterval.value);
    pollingInterval.value = null;
  }
};

onMounted(async () => {
  AOS.init({ once: true, duration: 700, offset: 60 });
  document.documentElement.setAttribute("data-theme", theme.value);
  observeElems();
  document.addEventListener('click', handleClickOutside);
  
  // Load registration config
  await loadRegistrationConfig();
  
  // Start polling for config updates
  startConfigPolling();
});

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside);
  // Stop polling when component unmounts
  stopConfigPolling();
});
</script>

<template>
  <div
    class="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-900 text-white relative overflow-hidden"
    :class="theme === 'light' ? 'brightness-105' : ''"
  >
    <!-- Background blobs -->
    <div class="absolute inset-0 overflow-hidden pointer-events-none">
      <div class="absolute top-0 -left-10 w-72 h-72 bg-purple-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob"></div>
      <div class="absolute top-10 -right-10 w-80 h-80 bg-indigo-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob"></div>
      <div class="absolute -bottom-10 left-32 w-72 h-72 bg-blue-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob"></div>
    </div>

    <!-- Header -->
    <header class="bg-[var(--header-blur)] backdrop-blur-md shadow-2xl sticky top-0 z-50 border-b border-purple-500/20">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <router-link to="/" class="flex items-center space-x-4 cursor-pointer">
            <div class="relative w-12 h-12 bg-gradient-to-r from-purple-400 via-violet-500 to-indigo-500 rounded-xl flex items-center justify-center shadow-lg">
              <div class="absolute inset-0 bg-gradient-to-r from-purple-600 to-indigo-600 rounded-xl blur opacity-75"></div>
              <i class="fas fa-gem text-white text-xl relative z-10"></i>
              <div class="absolute -top-1 -right-1 w-3 h-3 bg-gradient-to-r from-yellow-400 to-orange-400 rounded-full animate-pulse"></div>
            </div>
            <div class="flex flex-col">
              <span class="text-transparent bg-gradient-to-r from-purple-300 via-violet-300 to-indigo-300 bg-clip-text font-bold text-2xl tracking-wide">CMEETRADING</span>
              <span class="text-purple-400/80 text-xs font-light tracking-widest">CMEETRADING</span>
            </div>
          </router-link>

          <nav class="hidden lg:flex space-x-8">
            <router-link to="/" class="relative text-purple-100 hover:text-transparent hover:bg-gradient-to-r hover:from-purple-300 hover:to-indigo-300 hover:bg-clip-text transition-all duration-300 cursor-pointer group">
              <span class="relative z-10">{{ t("nav.home") }}</span>
              <div class="absolute bottom-0 left-0 w-0 h-0.5 bg-gradient-to-r from-purple-400 to-indigo-400 group-hover:w-full transition-all duration-300"></div>
            </router-link>
          </nav>

          <div class="flex items-center space-x-3 md:space-x-4">
            <button class="hidden md:flex items-center relative text-purple-100 hover:text-white cursor-pointer group">
              <i class="fas fa-headset mr-2 text-purple-400 group-hover:text-white transition-colors"></i>
              <span class="relative">{{ t("cta.support") }}</span>
              <div class="absolute -top-1 -right-1 w-2 h-2 bg-gradient-to-r from-green-400 to-emerald-400 rounded-full animate-pulse"></div>
            </button>
            <select
              class="bg-slate-800/70 text-sm px-3 py-2 rounded-lg border border-purple-400/30 text-white focus:outline-none"
              :value="currentLang"
              @change="changeLang($event.target.value)"
            >
              <option v-for="lang in languages" :key="lang.value" :value="lang.value">{{ lang.label }}</option>
            </select>
            <button
              class="bg-slate-800/70 text-white px-3 py-2 rounded-lg border border-purple-400/30 hover:bg-slate-700 transition"
              @click="toggleTheme"
            >
              <i :class="theme === 'dark' ? 'ri-sun-line' : 'ri-moon-line'"></i>
            </button>
            <router-link to="/" class="relative bg-gradient-to-r from-purple-600/80 to-indigo-600/80 backdrop-blur-sm text-white px-4 py-2 rounded-button hover:from-purple-600 hover:to-indigo-600 transition-all transform hover:scale-105 border border-purple-400/30 cursor-pointer whitespace-nowrap hidden sm:block">
              <span class="relative z-10">{{ t("cta.login") }}</span>
            </router-link>
            <button class="lg:hidden text-white text-2xl" @click="mobileOpen = !mobileOpen">
              <i :class="mobileOpen ? 'ri-close-line' : 'ri-menu-line'"></i>
            </button>
          </div>
        </div>
      </div>
    </header>

    <!-- Hero Section -->
    <section class="relative min-h-[60vh] flex items-center justify-center overflow-hidden py-20">
      <div class="absolute inset-0 bg-gradient-to-br from-purple-950/80 via-slate-950/60 to-indigo-950/80"></div>
      <ParticleCanvas />
      <div class="absolute inset-0">
        <div class="absolute top-20 left-10 w-20 h-20 border border-purple-400/30 rounded-lg rotate-45 animate-spin-slow"></div>
        <div class="absolute top-40 right-20 w-16 h-16 bg-gradient-to-r from-purple-500/20 to-indigo-500/20 rounded-full animate-float"></div>
        <div class="absolute bottom-32 left-32 w-12 h-12 border border-violet-400/40 rotate-12 animate-pulse"></div>
      </div>
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 text-center">
        <h1 class="text-5xl sm:text-6xl lg:text-7xl font-bold mb-6 leading-tight observe">
          <span class="bg-gradient-to-r from-purple-300 via-violet-300 to-indigo-300 bg-clip-text text-transparent">Đăng Ký Tài Khoản</span>
        </h1>
        <p class="text-xl text-purple-200/90 mb-8 leading-relaxed max-w-3xl mx-auto observe">
          Trải nghiệm giao dịch đẳng cấp thượng lưu với ưu đãi độc quyền dành riêng cho thành viên premium
        </p>
        <div class="flex items-center justify-center flex-wrap gap-4 sm:gap-8 observe">
          <div class="flex items-center space-x-2">
            <div class="w-3 h-3 bg-gradient-to-r from-emerald-400 to-green-400 rounded-full animate-pulse"></div>
            <span class="text-purple-200 text-sm">Spread từ 0.0 pips</span>
          </div>
          <div class="flex items-center space-x-2">
            <div class="w-3 h-3 bg-gradient-to-r from-purple-400 to-violet-400 rounded-full animate-pulse"></div>
            <span class="text-purple-200 text-sm">Hỗ trợ 1-1</span>
          </div>
          <div class="flex items-center space-x-2">
            <div class="w-3 h-3 bg-gradient-to-r from-yellow-400 to-orange-400 rounded-full animate-pulse"></div>
            <span class="text-purple-200 text-sm">Đòn bẩy cao</span>
          </div>
        </div>
      </div>
    </section>

    <!-- Registration Form Section -->
    <section class="relative py-16 lg:py-24 -mt-20">
      <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="bg-slate-900/90 backdrop-blur-xl rounded-2xl border border-purple-500/30 shadow-2xl p-8 lg:p-12 observe">
          <div class="text-center mb-8">
            <h2 class="text-3xl lg:text-4xl font-bold text-white mb-3">Thông Tin Đăng Ký</h2>
            <p class="text-purple-200/80">Vui lòng điền đầy đủ thông tin để tạo tài khoản premium</p>
          </div>

          <div v-if="loadingConfig" class="text-center py-8">
            <i class="fas fa-spinner fa-spin text-purple-400 text-2xl"></i>
            <p class="text-white/60 mt-2">Đang tải form đăng ký...</p>
          </div>

          <form v-else @submit.prevent="handleSubmit" class="space-y-8">
            <!-- Two Column Layout -->
            <div class="grid md:grid-cols-2 gap-8">
              <!-- Left Column - Personal Information -->
              <div class="space-y-6">
                <div v-if="isFieldEnabled('fullName') || isFieldEnabled('email') || isFieldEnabled('phone') || isFieldEnabled('dateOfBirth')" class="flex items-center space-x-2 mb-4">
                  <i class="ri-user-line text-purple-400 text-xl"></i>
                  <h3 class="text-xl font-semibold text-white">Thông Tin Cá Nhân</h3>
                </div>

                <!-- Full Name -->
                <div v-if="isFieldEnabled('fullName')">
                  <label class="block text-sm font-medium text-purple-200 mb-2">
                    {{ getFieldConfig('fullName')?.label || 'Họ và Tên' }} <span v-if="isFieldRequired('fullName')" class="text-red-400">*</span>
                  </label>
                  <input
                    v-model="formData.fullName"
                    type="text"
                    :placeholder="getFieldConfig('fullName')?.placeholder || 'Nhập họ và tên đầy đủ'"
                    class="w-full px-4 py-3 bg-slate-800/70 border border-purple-500/30 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-500/50 transition-all"
                    :class="{ 'border-red-500': errors.fullName }"
                    :required="isFieldRequired('fullName')"
                  />
                  <p v-if="errors.fullName" class="mt-1 text-sm text-red-400">{{ errors.fullName }}</p>
                </div>

                <!-- Email -->
                <div v-if="isFieldEnabled('email')">
                  <label class="block text-sm font-medium text-purple-200 mb-2">
                    {{ getFieldConfig('email')?.label || 'Email' }} <span v-if="isFieldRequired('email')" class="text-red-400">*</span>
                  </label>
                  <input
                    v-model="formData.email"
                    type="email"
                    :placeholder="getFieldConfig('email')?.placeholder || 'example@gmail.com'"
                    class="w-full px-4 py-3 bg-slate-800/70 border border-purple-500/30 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-500/50 transition-all"
                    :class="{ 'border-red-500': errors.email }"
                    :required="isFieldRequired('email')"
                  />
                  <p v-if="errors.email" class="mt-1 text-sm text-red-400">{{ errors.email }}</p>
                </div>

                <!-- Phone -->
                <div v-if="isFieldEnabled('phone')">
                  <label class="block text-sm font-medium text-purple-200 mb-2">
                    {{ getFieldConfig('phone')?.label || 'Số Điện Thoại' }} <span v-if="isFieldRequired('phone')" class="text-red-400">*</span>
                  </label>
                  <input
                    v-model="formData.phone"
                    type="tel"
                    :placeholder="getFieldConfig('phone')?.placeholder || '+84 xxx xxx xxx'"
                    class="w-full px-4 py-3 bg-slate-800/70 border border-purple-500/30 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-500/50 transition-all"
                    :class="{ 'border-red-500': errors.phone }"
                    :required="isFieldRequired('phone')"
                  />
                  <p v-if="errors.phone" class="mt-1 text-sm text-red-400">{{ errors.phone }}</p>
                </div>

                <!-- Date of Birth -->
                <div v-if="isFieldEnabled('dateOfBirth')">
                  <label class="block text-sm font-medium text-purple-200 mb-2">
                    {{ getFieldConfig('dateOfBirth')?.label || 'Ngày Sinh' }} <span v-if="isFieldRequired('dateOfBirth')" class="text-red-400">*</span>
                  </label>
                  <input
                    v-model="formData.dateOfBirth"
                    type="date"
                    class="w-full px-4 py-3 bg-slate-800/70 border border-purple-500/30 rounded-lg text-white focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-500/50 transition-all"
                    :required="isFieldRequired('dateOfBirth')"
                  />
                </div>
              </div>

              <!-- Right Column - Account Information -->
              <div class="space-y-6">
                <div v-if="isFieldEnabled('password') || isFieldEnabled('confirmPassword') || isFieldEnabled('country') || isFieldEnabled('tradingExperience')" class="flex items-center space-x-2 mb-4">
                  <i class="ri-lock-line text-purple-400 text-xl"></i>
                  <h3 class="text-xl font-semibold text-white">Thông Tin Tài Khoản</h3>
                </div>

                <!-- Password -->
                <div v-if="isFieldEnabled('password')">
                  <label class="block text-sm font-medium text-purple-200 mb-2">
                    {{ getFieldConfig('password')?.label || 'Mật Khẩu' }} <span v-if="isFieldRequired('password')" class="text-red-400">*</span>
                  </label>
                  <div class="relative">
                    <input
                      v-model="formData.password"
                      :type="showPassword ? 'text' : 'password'"
                      :placeholder="getFieldConfig('password')?.placeholder || 'Tối thiểu 8 ký tự'"
                      class="w-full px-4 py-3 bg-slate-800/70 border border-purple-500/30 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-500/50 transition-all pr-12"
                      :class="{ 'border-red-500': errors.password }"
                      :required="isFieldRequired('password')"
                    />
                    <button
                      type="button"
                      @click="showPassword = !showPassword"
                      class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-white transition-colors"
                    >
                      <i :class="showPassword ? 'ri-eye-off-line' : 'ri-eye-line'"></i>
                    </button>
                  </div>
                  <p v-if="errors.password" class="mt-1 text-sm text-red-400">{{ errors.password }}</p>
                </div>

                <!-- Confirm Password -->
                <div v-if="isFieldEnabled('confirmPassword')">
                  <label class="block text-sm font-medium text-purple-200 mb-2">
                    {{ getFieldConfig('confirmPassword')?.label || 'Xác Nhận Mật Khẩu' }} <span v-if="isFieldRequired('confirmPassword')" class="text-red-400">*</span>
                  </label>
                  <div class="relative">
                    <input
                      v-model="formData.confirmPassword"
                      :type="showConfirmPassword ? 'text' : 'password'"
                      :placeholder="getFieldConfig('confirmPassword')?.placeholder || 'Nhập lại mật khẩu'"
                      class="w-full px-4 py-3 bg-slate-800/70 border border-purple-500/30 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-500/50 transition-all pr-12"
                      :class="{ 'border-red-500': errors.confirmPassword }"
                      :required="isFieldRequired('confirmPassword')"
                    />
                    <button
                      type="button"
                      @click="showConfirmPassword = !showConfirmPassword"
                      class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-white transition-colors"
                    >
                      <i :class="showConfirmPassword ? 'ri-eye-off-line' : 'ri-eye-line'"></i>
                    </button>
                  </div>
                  <p v-if="errors.confirmPassword" class="mt-1 text-sm text-red-400">{{ errors.confirmPassword }}</p>
                </div>

                <!-- Custom ID/Username -->
                <div v-if="isFieldEnabled('customId')">
                  <label class="block text-sm font-medium text-purple-200 mb-2">
                    {{ getFieldConfig('customId')?.label || 'ID/Username Tùy Chỉnh' }} <span v-if="isFieldRequired('customId')" class="text-red-400">*</span>
                  </label>
                  <div class="relative">
                    <i class="ri-user-3-line absolute left-3 top-1/2 -translate-y-1/2 text-purple-400"></i>
                    <input
                      v-model="formData.customId"
                      type="text"
                      :placeholder="getFieldConfig('customId')?.placeholder || 'Nhập ID/username của bạn (3-50 ký tự)'"
                      class="w-full pl-10 pr-4 py-3 bg-slate-800/70 border border-purple-500/30 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-500/50 transition-all"
                      :class="{ 'border-red-500': errors.customId }"
                      :required="isFieldRequired('customId')"
                      maxlength="50"
                    />
                  </div>
                  <p v-if="errors.customId" class="mt-1 text-sm text-red-400">{{ errors.customId }}</p>
                  <p v-if="formData.customId && !errors.customId" class="mt-1 text-xs text-purple-300/70">
                    <i class="ri-information-line mr-1"></i>
                    ID này sẽ được sử dụng để đăng nhập và hiển thị trong hệ thống. Ví dụ: john_doe_123
                  </p>
                  <p v-if="formData.customId" class="mt-1 text-xs text-purple-300/70">
                    {{ formData.customId.length }}/50 ký tự
                  </p>
                </div>

                <!-- Country -->
                <div v-if="isFieldEnabled('country')" data-dropdown="country">
                  <label class="block text-sm font-medium text-purple-200 mb-2">
                    {{ getFieldConfig('country')?.label || 'Quốc Gia' }} <span v-if="isFieldRequired('country')" class="text-red-400">*</span>
                  </label>
                  <div class="relative">
                    <button
                      type="button"
                      @click.stop="countryDropdownOpen = !countryDropdownOpen"
                      class="w-full px-4 py-3 bg-slate-800/70 border border-purple-500/30 rounded-lg text-white text-left flex items-center justify-between focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-500/50 transition-all"
                      :class="{ 'border-red-500': errors.country, 'border-purple-500': countryDropdownOpen }"
                    >
                      <span :class="{ 'text-gray-500': !formData.country }">
                        {{ formData.country || (getFieldConfig('country')?.placeholder || "Chọn quốc gia") }}
                      </span>
                      <i class="ri-arrow-down-s-line" :class="{ 'rotate-180': countryDropdownOpen }"></i>
                    </button>
                    <div
                      v-if="countryDropdownOpen"
                      class="absolute z-10 w-full mt-2 bg-slate-800 border border-purple-500/30 rounded-lg shadow-xl max-h-60 overflow-y-auto dropdown-enter-active"
                      @click.stop
                    >
                      <button
                        v-for="country in countries"
                        :key="country"
                        type="button"
                        @click="formData.country = country; countryDropdownOpen = false"
                        class="w-full px-4 py-2 text-left text-white hover:bg-purple-500/20 transition-colors"
                      >
                        {{ country }}
                      </button>
                    </div>
                  </div>
                  <p v-if="errors.country" class="mt-1 text-sm text-red-400">{{ errors.country }}</p>
                </div>

                <!-- Trading Experience -->
                <div v-if="isFieldEnabled('tradingExperience')" data-dropdown="experience">
                  <label class="block text-sm font-medium text-purple-200 mb-2">
                    {{ getFieldConfig('tradingExperience')?.label || 'Kinh Nghiệm Giao Dịch' }} <span v-if="isFieldRequired('tradingExperience')" class="text-red-400">*</span>
                  </label>
                  <div class="relative">
                    <button
                      type="button"
                      @click.stop="experienceDropdownOpen = !experienceDropdownOpen"
                      class="w-full px-4 py-3 bg-slate-800/70 border border-purple-500/30 rounded-lg text-white text-left flex items-center justify-between focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-500/50 transition-all"
                      :class="{ 'border-purple-500': experienceDropdownOpen }"
                    >
                      <span :class="{ 'text-gray-500': !formData.tradingExperience }">
                        {{ formData.tradingExperience || (getFieldConfig('tradingExperience')?.placeholder || "Chọn mức độ kinh nghiệm") }}
                      </span>
                      <i class="ri-arrow-down-s-line" :class="{ 'rotate-180': experienceDropdownOpen }"></i>
                    </button>
                    <div
                      v-if="experienceDropdownOpen"
                      class="absolute z-10 w-full mt-2 bg-slate-800 border border-purple-500/30 rounded-lg shadow-xl max-h-60 overflow-y-auto dropdown-enter-active"
                      @click.stop
                    >
                      <button
                        v-for="exp in tradingExperiences"
                        :key="exp"
                        type="button"
                        @click="formData.tradingExperience = exp; experienceDropdownOpen = false"
                        class="w-full px-4 py-2 text-left text-white hover:bg-purple-500/20 transition-colors"
                      >
                        {{ exp }}
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Referral Code - Centered -->
            <div v-if="isFieldEnabled('referralCode')" class="flex justify-center pt-4">
              <div class="w-full max-w-md">
                <label class="block text-sm font-medium text-purple-200 mb-2 text-center">
                  {{ getFieldConfig('referralCode')?.label || 'Mã Giới Thiệu' }} <span v-if="isFieldRequired('referralCode')" class="text-red-400">*</span>
                </label>
                <input
                  v-model="formData.referralCode"
                  type="text"
                  :placeholder="getFieldConfig('referralCode')?.placeholder || 'Nhập mã giới thiệu (nếu có)'"
                  class="w-full px-4 py-3 bg-slate-800/70 border border-purple-500/30 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-500/50 transition-all"
                  :required="isFieldRequired('referralCode')"
                />
              </div>
            </div>

            <!-- Terms and Conditions -->
            <div v-if="isFieldEnabled('agreeTerms') || isFieldEnabled('agreeMarketing')" class="space-y-4 pt-4 border-t border-purple-500/20">
              <div v-if="isFieldEnabled('agreeTerms')">
                <label class="flex items-start space-x-3 cursor-pointer">
                  <input
                    v-model="formData.agreeTerms"
                    type="checkbox"
                    class="mt-1 w-5 h-5 bg-slate-800 border-purple-500/30 rounded text-purple-600 focus:ring-purple-500 focus:ring-2"
                    :class="{ 'border-red-500': errors.agreeTerms }"
                    :required="isFieldRequired('agreeTerms')"
                  />
                  <span class="text-sm text-purple-200">
                    {{ getFieldConfig('agreeTerms')?.label || 'Tôi đồng ý với' }}
                    <a href="#" class="text-purple-400 hover:text-purple-300 underline">Điều khoản sử dụng</a>
                    và
                    <a href="#" class="text-purple-400 hover:text-purple-300 underline">Chính sách bảo mật</a>
                    của CMEETRADING
                  </span>
                </label>
                <p v-if="errors.agreeTerms" class="mt-1 text-sm text-red-400">{{ errors.agreeTerms }}</p>
              </div>
              <div v-if="isFieldEnabled('agreeMarketing')">
                <label class="flex items-start space-x-3 cursor-pointer">
                  <input
                    v-model="formData.agreeMarketing"
                    type="checkbox"
                    class="mt-1 w-5 h-5 bg-slate-800 border-purple-500/30 rounded text-purple-600 focus:ring-purple-500 focus:ring-2"
                    :required="isFieldRequired('agreeMarketing')"
                  />
                  <span class="text-sm text-purple-200">
                    {{ getFieldConfig('agreeMarketing')?.label || 'Tôi muốn nhận thông tin khuyến mãi và tin tức thị trường từ CMEETRADING' }}
                  </span>
                </label>
              </div>
            </div>

            <!-- Submit Button -->
            <div class="pt-6">
              <button
                type="submit"
                :disabled="isSubmitting"
                class="w-full relative group bg-gradient-to-r from-violet-600 via-purple-600 to-indigo-600 text-white px-8 py-4 rounded-button text-lg font-bold hover:shadow-2xl hover:shadow-purple-500/50 transition-all transform hover:scale-[1.02] disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <div class="absolute inset-0 bg-gradient-to-r from-violet-600 via-purple-600 to-indigo-600 rounded-button blur opacity-75"></div>
                <span class="relative z-10">
                  {{ isSubmitting ? "Đang xử lý..." : "Xác Nhận Đăng Ký" }}
                </span>
              </button>
              <p class="text-center text-xs text-purple-300/70 mt-3">
                <i class="fas fa-shield-alt mr-1"></i>
                Bảo mật SSL 256-bit • Xử lý trong vòng 24 giờ
              </p>
            </div>
          </form>
        </div>

        <!-- Security and Trust Elements -->
        <div class="mt-12 grid md:grid-cols-4 gap-6 observe">
          <div class="bg-slate-800/50 backdrop-blur-sm p-6 rounded-xl border border-purple-500/20 text-center">
            <i class="fas fa-shield-check text-emerald-400 text-3xl mb-3"></i>
            <h4 class="text-white font-semibold mb-1">SSL 256-bit</h4>
            <p class="text-gray-400 text-sm">Bảo mật cao cấp</p>
          </div>
          <div class="bg-slate-800/50 backdrop-blur-sm p-6 rounded-xl border border-purple-500/20 text-center">
            <i class="fas fa-certificate text-blue-400 text-3xl mb-3"></i>
            <h4 class="text-white font-semibold mb-1">CySEC</h4>
            <p class="text-gray-400 text-sm">Giấy phép hợp pháp</p>
          </div>
          <div class="bg-slate-800/50 backdrop-blur-sm p-6 rounded-xl border border-purple-500/20 text-center">
            <i class="fas fa-clock text-purple-400 text-3xl mb-3"></i>
            <h4 class="text-white font-semibold mb-1">Xử lý nhanh</h4>
            <p class="text-gray-400 text-sm">Trong 24 giờ</p>
          </div>
          <div class="bg-slate-800/50 backdrop-blur-sm p-6 rounded-xl border border-purple-500/20 text-center">
            <i class="fas fa-users text-yellow-400 text-3xl mb-3"></i>
            <h4 class="text-white font-semibold mb-1">100,000+</h4>
            <p class="text-gray-400 text-sm">Khách hàng tin tưởng</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Footer Simplified -->
    <footer class="bg-slate-900 py-12 mt-20">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="grid md:grid-cols-3 gap-8 mb-8">
          <div>
            <div class="flex items-center space-x-2 mb-4">
              <div class="w-10 h-10 bg-gradient-to-r from-purple-400 to-indigo-400 rounded-lg flex items-center justify-center">
                <i class="fas fa-gem text-white text-lg"></i>
              </div>
              <span class="text-white font-bold text-xl">CMEETRADING</span>
            </div>
            <p class="text-gray-300 text-sm mb-4">Nền tảng giao dịch premium hàng đầu với công nghệ tiên tiến</p>
            <div class="flex space-x-4">
              <a class="text-gray-400 hover:text-purple-400 cursor-pointer"><i class="fab fa-facebook text-xl"></i></a>
              <a class="text-gray-400 hover:text-purple-400 cursor-pointer"><i class="fab fa-twitter text-xl"></i></a>
              <a class="text-gray-400 hover:text-purple-400 cursor-pointer"><i class="fab fa-linkedin text-xl"></i></a>
            </div>
          </div>

          <div>
            <h3 class="text-white font-bold mb-4">Hỗ Trợ</h3>
            <ul class="space-y-2">
              <li><a class="text-gray-300 hover:text-white cursor-pointer text-sm">Trung tâm trợ giúp</a></li>
              <li><a class="text-gray-300 hover:text-white cursor-pointer text-sm">Liên hệ</a></li>
              <li><a class="text-gray-300 hover:text-white cursor-pointer text-sm">FAQ</a></li>
            </ul>
          </div>

          <div>
            <h3 class="text-white font-bold mb-4">Pháp Lý</h3>
            <ul class="space-y-2">
              <li><a class="text-gray-300 hover:text-white cursor-pointer text-sm">Điều khoản sử dụng</a></li>
              <li><a class="text-gray-300 hover:text-white cursor-pointer text-sm">Chính sách bảo mật</a></li>
              <li><a class="text-gray-300 hover:text-white cursor-pointer text-sm">Cảnh báo rủi ro</a></li>
              <li><a class="text-gray-300 hover:text-white cursor-pointer text-sm">Khiếu nại</a></li>
            </ul>
          </div>
        </div>
        <div class="border-t border-slate-700 pt-6 text-center">
          <p class="text-gray-400 text-sm">
            © 2025 CMEETRADING. Tất cả quyền được bảo lưu.
          </p>
        </div>
      </div>
    </footer>

  </div>
</template>

