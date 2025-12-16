<script setup>
import { onBeforeUnmount, onMounted, reactive, ref, nextTick } from "vue";
import { useRouter } from "vue-router";
import { useI18n } from "vue-i18n";
import ParticleCanvas from "../components/ParticleCanvas.vue";
import AOS from "aos";
import { authApi } from "../services/api/auth";

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
  phone: "",
  password: "",
  rememberMe: false,
});

const errors = reactive({
  phone: "",
  password: "",
});

const showPassword = ref(false);
const isSubmitting = ref(false);
const errorMessage = ref("");

// Validation
const validatePhone = (phone) => {
  if (!phone) {
    return t("loginModal.validation.emailRequired") || "Số điện thoại là bắt buộc";
  }
  // Remove spaces and validate phone number format (Vietnamese phone numbers: 10-11 digits, may start with +84 or 0)
  const cleanedPhone = phone.replace(/\s/g, "");
  const phoneRegex = /^(\+84|0)[1-9][0-9]{8,9}$/;
  if (!phoneRegex.test(cleanedPhone)) {
    return t("loginModal.validation.emailInvalid") || "Vui lòng nhập số điện thoại hợp lệ";
  }
  return "";
};

const validatePassword = (password) => {
  if (!password) {
    return t("loginModal.validation.passwordRequired") || "Mật khẩu là bắt buộc";
  }
  if (password.length < 6) {
    return t("loginModal.validation.passwordMinLength") || "Mật khẩu phải có ít nhất 6 ký tự";
  }
  return "";
};

const validateForm = () => {
  errors.phone = validatePhone(formData.phone);
  errors.password = validatePassword(formData.password);
  return !errors.phone && !errors.password;
};

// Handle form submit
const handleSubmit = async () => {
  errorMessage.value = "";
  
  if (!validateForm()) {
    return;
  }

  isSubmitting.value = true;

  try {
    // Clean phone number (remove spaces)
    const cleanedPhone = formData.phone.replace(/\s/g, "");
    const response = await authApi.login({
      phone_number: cleanedPhone,
      password: formData.password,
      remember_me: formData.rememberMe,
    });

    // Extract token from multiple possible response formats
    let token = null;
    if (response.token) {
      token = response.token;
    } else if (response.access_token) {
      token = response.access_token;
    } else if (response.data?.token) {
      token = response.data.token;
    } else if (response.data?.access_token) {
      token = response.data.access_token;
    }

    // Store token if found
    if (token) {
      localStorage.setItem("auth_token", token);
      
      // Store refresh token if available
      if (response.refresh_token) {
        localStorage.setItem("refresh_token", response.refresh_token);
      } else if (response.data?.refresh_token) {
        localStorage.setItem("refresh_token", response.data.refresh_token);
      }
      
      if (formData.rememberMe) {
        localStorage.setItem("remember_me", "true");
      }
    }

    // Store user data if available
    if (response.user) {
      localStorage.setItem("user", JSON.stringify(response.user));
    } else if (response.data?.user) {
      localStorage.setItem("user", JSON.stringify(response.data.user));
    }

    // Wait for next tick to ensure localStorage is updated
    await nextTick();

    // Redirect to personal overview or redirect query param
    const redirect = router.currentRoute.value.query.redirect;
    router.push(redirect || "/personal/overview");
  } catch (error) {
    if (error.response?.data?.detail) {
      errorMessage.value = error.response.data.detail;
    } else if (error.message) {
      errorMessage.value = error.message;
    } else {
      errorMessage.value = "Đăng nhập thất bại. Vui lòng thử lại.";
    }
  } finally {
    isSubmitting.value = false;
  }
};

// Navigate to register
const goToRegister = () => {
  router.push("/register");
};

// Navigate to forgot password
const goToForgotPassword = () => {
  router.push("/forgot-password");
};

onMounted(() => {
  nextTick(() => {
    AOS.init({
      duration: 1000,
      once: true,
    });
  });
});
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-purple-900 via-indigo-900 to-purple-900 relative overflow-hidden">
    <!-- Particle Background -->
    <ParticleCanvas />

    <!-- Navigation -->
    <nav class="relative z-10 px-4 sm:px-6 lg:px-8 py-4">
      <div class="max-w-7xl mx-auto flex items-center justify-between">
        <!-- Logo -->
        <router-link to="/" class="flex items-center space-x-2">
          <div class="w-10 h-10 bg-gradient-to-r from-purple-500 to-indigo-500 rounded-lg flex items-center justify-center">
            <i class="fas fa-gem text-white text-xl"></i>
          </div>
          <span class="text-white text-xl font-bold">CMEETRADING</span>
        </router-link>

        <!-- Right Side -->
        <div class="flex items-center space-x-4">
          <!-- Language Selector -->
          <div class="hidden sm:flex items-center space-x-2">
            <button
              v-for="lang in languages"
              :key="lang.value"
              @click="changeLang(lang.value)"
              :class="[
                'px-3 py-1 rounded text-sm font-medium transition-all',
                currentLang === lang.value
                  ? 'bg-purple-600 text-white'
                  : 'text-white/70 hover:text-white hover:bg-white/10'
              ]"
            >
              {{ lang.label }}
            </button>
          </div>

          <!-- Register Link -->
          <router-link
            to="/register"
            class="text-white/80 hover:text-white text-sm font-medium transition-colors"
          >
            {{ t("cta.register") || "Đăng ký" }}
          </router-link>
        </div>
      </div>
    </nav>

    <!-- Main Content -->
    <div class="relative z-10 flex items-center justify-center min-h-[calc(100vh-80px)] px-4 py-12">
      <div class="w-full max-w-md">
        <!-- Login Card -->
        <div
          class="bg-gradient-to-br from-purple-900/90 via-purple-800/90 to-indigo-900/90 backdrop-blur-xl rounded-2xl shadow-2xl p-8 border border-purple-500/30"
          data-aos="fade-up"
        >
          <!-- Logo -->
          <div class="flex justify-center mb-6">
            <div
              class="relative w-20 h-20 bg-gradient-to-r from-purple-500 via-violet-500 to-indigo-500 rounded-2xl flex items-center justify-center shadow-lg"
            >
              <div class="absolute inset-0 bg-gradient-to-r from-purple-600 to-indigo-600 rounded-2xl blur opacity-75"></div>
              <i class="fas fa-gem text-white text-3xl relative z-10"></i>
            </div>
          </div>

          <!-- Title -->
          <h2 class="text-3xl font-bold text-white text-center mb-2">
            {{ t("loginModal.title") || "Đăng Nhập" }}
          </h2>
          <p class="text-purple-200/90 text-center mb-8 text-sm">
            {{ t("loginModal.subtitle") || "Chào mừng trở lại!" }}
          </p>

          <!-- Login Form -->
          <form @submit.prevent="handleSubmit" class="space-y-5">
            <!-- Phone Number Field -->
            <div>
              <label class="block text-white/90 text-sm font-medium mb-2">
                {{ t("loginModal.emailLabel") || "Số điện thoại" }}
              </label>
              <div class="relative">
                <input
                  v-model="formData.phone"
                  type="tel"
                  :placeholder="t('loginModal.emailPlaceholder') || 'Nhập số điện thoại'"
                  class="w-full px-4 py-3 pl-12 pr-4 bg-white/10 border border-purple-400/30 rounded-lg text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-purple-400/50 focus:border-purple-400 transition-all"
                  :class="{ 'border-red-400': errors.phone }"
                />
                <i class="ri-phone-line absolute left-4 top-1/2 -translate-y-1/2 text-white/60"></i>
              </div>
              <p v-if="errors.phone" class="mt-1 text-sm text-red-400">{{ errors.phone }}</p>
            </div>

            <!-- Password Field -->
            <div>
              <label class="block text-white/90 text-sm font-medium mb-2">
                {{ t("loginModal.passwordLabel") || "Mật khẩu" }}
              </label>
              <div class="relative">
                <input
                  v-model="formData.password"
                  :type="showPassword ? 'text' : 'password'"
                  :placeholder="t('loginModal.passwordPlaceholder') || 'Nhập mật khẩu'"
                  class="w-full px-4 py-3 pl-12 pr-12 bg-white/10 border border-purple-400/30 rounded-lg text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-purple-400/50 focus:border-purple-400 transition-all"
                  :class="{ 'border-red-400': errors.password }"
                />
                <i class="ri-lock-line absolute left-4 top-1/2 -translate-y-1/2 text-white/60"></i>
                <button
                  type="button"
                  @click="showPassword = !showPassword"
                  class="absolute right-4 top-1/2 -translate-y-1/2 text-white/60 hover:text-white transition-colors"
                >
                  <i :class="showPassword ? 'ri-eye-off-line' : 'ri-eye-line'"></i>
                </button>
              </div>
              <p v-if="errors.password" class="mt-1 text-sm text-red-400">{{ errors.password }}</p>
            </div>

            <!-- Remember Me & Forgot Password -->
            <div class="flex items-center justify-between">
              <label class="flex items-center cursor-pointer">
                <input
                  v-model="formData.rememberMe"
                  type="checkbox"
                  class="w-4 h-4 rounded border-purple-400/30 bg-white/10 text-purple-500 focus:ring-purple-400/50 focus:ring-2"
                />
                <span class="ml-2 text-white/80 text-sm">{{ t("loginModal.rememberMe") || "Ghi nhớ đăng nhập" }}</span>
              </label>
              <button
                type="button"
                @click="goToForgotPassword"
                class="text-purple-300 hover:text-purple-200 text-sm transition-colors"
              >
                {{ t("loginModal.forgotPassword") || "Quên mật khẩu?" }}
              </button>
            </div>

            <!-- Error Message -->
            <div v-if="errorMessage" class="bg-red-500/20 border border-red-400/30 rounded-lg p-3">
              <p class="text-red-300 text-sm text-center">{{ errorMessage }}</p>
            </div>

            <!-- Login Button -->
            <button
              type="submit"
              :disabled="isSubmitting"
              class="w-full bg-gradient-to-r from-purple-600 via-violet-600 to-indigo-600 text-white py-3 rounded-lg font-semibold hover:from-purple-500 hover:via-violet-500 hover:to-indigo-500 transition-all transform hover:scale-[1.02] disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
            >
              <span v-if="!isSubmitting">{{ t("loginModal.loginButton") || "Đăng Nhập" }}</span>
              <span v-else class="flex items-center justify-center">
                <i class="ri-loader-4-line animate-spin mr-2"></i>
                {{ t("loginModal.loggingIn") || "Đang đăng nhập..." }}
              </span>
            </button>
          </form>

          <!-- Divider -->
          <div class="flex items-center my-6">
            <div class="flex-1 h-px bg-white/20"></div>
            <span class="px-4 text-white/60 text-sm">{{ t("loginModal.or") || "Hoặc" }}</span>
            <div class="flex-1 h-px bg-white/20"></div>
          </div>

          <!-- Social Login Buttons -->
          <div class="space-y-3">
            <!-- Google Login -->
            <button
              type="button"
              class="w-full bg-white/10 hover:bg-white/20 border border-white/20 text-white py-3 rounded-lg font-medium transition-all flex items-center justify-center gap-3"
            >
              <i class="ri-google-fill text-xl"></i>
              <span>{{ t("loginModal.googleLogin") || "Đăng nhập với Google" }}</span>
            </button>

            <!-- Facebook Login -->
            <button
              type="button"
              class="w-full bg-white/10 hover:bg-white/20 border border-white/20 text-white py-3 rounded-lg font-medium transition-all flex items-center justify-center gap-3"
            >
              <i class="ri-facebook-fill text-xl"></i>
              <span>{{ t("loginModal.facebookLogin") || "Đăng nhập với Facebook" }}</span>
            </button>
          </div>

          <!-- Register Link -->
          <div class="mt-6 text-center">
            <p class="text-white/70 text-sm">
              {{ t("loginModal.noAccount") || "Chưa có tài khoản?" }}
              <button
                @click="goToRegister"
                class="text-purple-300 hover:text-purple-200 font-semibold transition-colors"
              >
                {{ t("loginModal.registerNow") || "Đăng ký ngay" }}
              </button>
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Additional styles if needed */
</style>

