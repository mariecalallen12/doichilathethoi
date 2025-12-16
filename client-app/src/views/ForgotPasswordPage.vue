<script setup>
import { onMounted, reactive, ref, nextTick } from "vue";
import { useRouter } from "vue-router";
import { useI18n } from "vue-i18n";
import ParticleCanvas from "../components/ParticleCanvas.vue";
import AOS from "aos";
import { authApi } from "../services/api/auth";

const router = useRouter();
const { t } = useI18n();

const currentStep = ref(1); // 1: Request, 2: Verify, 3: Reset
const formData = reactive({
  email: "",
  token: "",
  newPassword: "",
  confirmPassword: "",
});

const errors = reactive({
  email: "",
  token: "",
  newPassword: "",
  confirmPassword: "",
});

const showPassword = ref(false);
const showConfirmPassword = ref(false);
const isSubmitting = ref(false);
const errorMessage = ref("");
const successMessage = ref("");

// Validation
const validateEmail = (email) => {
  if (!email) {
    return "Email là bắt buộc";
  }
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!re.test(email)) {
    return "Email không hợp lệ";
  }
  return "";
};

const validatePassword = (password) => {
  if (!password) {
    return "Mật khẩu là bắt buộc";
  }
  if (password.length < 8) {
    return "Mật khẩu phải có ít nhất 8 ký tự";
  }
  if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(password)) {
    return "Mật khẩu phải chứa chữ hoa, chữ thường và số";
  }
  return "";
};

// Step 1: Request password reset
const handleRequestReset = async () => {
  errorMessage.value = "";
  errors.email = validateEmail(formData.email);

  if (errors.email) {
    return;
  }

  isSubmitting.value = true;

  try {
    await authApi.forgotPassword(formData.email);
    successMessage.value = "Email đặt lại mật khẩu đã được gửi. Vui lòng kiểm tra hộp thư của bạn.";
    currentStep.value = 2;
  } catch (error) {
    if (error.response?.data?.detail) {
      errorMessage.value = error.response.data.detail;
    } else if (error.message) {
      errorMessage.value = error.message;
    } else {
      errorMessage.value = "Không thể gửi email đặt lại mật khẩu. Vui lòng thử lại.";
    }
  } finally {
    isSubmitting.value = false;
  }
};

// Step 2: Verify token and reset password
const handleResetPassword = async () => {
  errorMessage.value = "";
  errors.token = formData.token ? "" : "Mã xác thực là bắt buộc";
  errors.newPassword = validatePassword(formData.newPassword);
  errors.confirmPassword = formData.confirmPassword
    ? formData.newPassword === formData.confirmPassword
      ? ""
      : "Mật khẩu xác nhận không khớp"
    : "Vui lòng xác nhận mật khẩu";

  if (errors.token || errors.newPassword || errors.confirmPassword) {
    return;
  }

  isSubmitting.value = true;

  try {
    await authApi.resetPassword({
      token: formData.token,
      new_password: formData.newPassword,
    });
    successMessage.value = "Mật khẩu đã được đặt lại thành công!";
    currentStep.value = 3;
    
    // Redirect to login after 2 seconds
    setTimeout(() => {
      router.push("/login");
    }, 2000);
  } catch (error) {
    if (error.response?.data?.detail) {
      errorMessage.value = error.response.data.detail;
    } else if (error.message) {
      errorMessage.value = error.message;
    } else {
      errorMessage.value = "Không thể đặt lại mật khẩu. Vui lòng thử lại.";
    }
  } finally {
    isSubmitting.value = false;
  }
};

const goToLogin = () => {
  router.push("/login");
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

        <!-- Back to Login -->
        <button
          @click="goToLogin"
          class="text-white/80 hover:text-white text-sm font-medium transition-colors"
        >
          <i class="ri-arrow-left-line mr-1"></i>
          Quay lại đăng nhập
        </button>
      </div>
    </nav>

    <!-- Main Content -->
    <div class="relative z-10 flex items-center justify-center min-h-[calc(100vh-80px)] px-4 py-12">
      <div class="w-full max-w-md">
        <!-- Forgot Password Card -->
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
              <i class="ri-lock-password-line text-white text-3xl relative z-10"></i>
            </div>
          </div>

          <!-- Step 1: Request Reset -->
          <div v-if="currentStep === 1">
            <h2 class="text-3xl font-bold text-white text-center mb-2">
              Quên Mật Khẩu?
            </h2>
            <p class="text-purple-200/90 text-center mb-8 text-sm">
              Nhập email của bạn để nhận liên kết đặt lại mật khẩu
            </p>

            <form @submit.prevent="handleRequestReset" class="space-y-5">
              <!-- Email Field -->
              <div>
                <label class="block text-white/90 text-sm font-medium mb-2">
                  Email
                </label>
                <div class="relative">
                  <input
                    v-model="formData.email"
                    type="email"
                    placeholder="Nhập email của bạn"
                    class="w-full px-4 py-3 pl-12 pr-4 bg-white/10 border border-purple-400/30 rounded-lg text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-purple-400/50 focus:border-purple-400 transition-all"
                    :class="{ 'border-red-400': errors.email }"
                  />
                  <i class="ri-mail-line absolute left-4 top-1/2 -translate-y-1/2 text-white/60"></i>
                </div>
                <p v-if="errors.email" class="mt-1 text-sm text-red-400">{{ errors.email }}</p>
              </div>

              <!-- Error Message -->
              <div v-if="errorMessage" class="bg-red-500/20 border border-red-400/30 rounded-lg p-3">
                <p class="text-red-300 text-sm text-center">{{ errorMessage }}</p>
              </div>

              <!-- Submit Button -->
              <button
                type="submit"
                :disabled="isSubmitting"
                class="w-full bg-gradient-to-r from-purple-600 via-violet-600 to-indigo-600 text-white py-3 rounded-lg font-semibold hover:from-purple-500 hover:via-violet-500 hover:to-indigo-500 transition-all transform hover:scale-[1.02] disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
              >
                <span v-if="!isSubmitting">Gửi Email Đặt Lại</span>
                <span v-else class="flex items-center justify-center">
                  <i class="ri-loader-4-line animate-spin mr-2"></i>
                  Đang gửi...
                </span>
              </button>
            </form>
          </div>

          <!-- Step 2: Reset Password -->
          <div v-if="currentStep === 2">
            <h2 class="text-3xl font-bold text-white text-center mb-2">
              Đặt Lại Mật Khẩu
            </h2>
            <p class="text-purple-200/90 text-center mb-8 text-sm">
              Nhập mã xác thực từ email và mật khẩu mới
            </p>

            <!-- Success Message -->
            <div v-if="successMessage" class="bg-green-500/20 border border-green-400/30 rounded-lg p-3 mb-5">
              <p class="text-green-300 text-sm text-center">{{ successMessage }}</p>
            </div>

            <form @submit.prevent="handleResetPassword" class="space-y-5">
              <!-- Token Field -->
              <div>
                <label class="block text-white/90 text-sm font-medium mb-2">
                  Mã Xác Thực
                </label>
                <div class="relative">
                  <input
                    v-model="formData.token"
                    type="text"
                    placeholder="Nhập mã xác thực từ email"
                    class="w-full px-4 py-3 pl-12 pr-4 bg-white/10 border border-purple-400/30 rounded-lg text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-purple-400/50 focus:border-purple-400 transition-all"
                    :class="{ 'border-red-400': errors.token }"
                  />
                  <i class="ri-key-line absolute left-4 top-1/2 -translate-y-1/2 text-white/60"></i>
                </div>
                <p v-if="errors.token" class="mt-1 text-sm text-red-400">{{ errors.token }}</p>
              </div>

              <!-- New Password Field -->
              <div>
                <label class="block text-white/90 text-sm font-medium mb-2">
                  Mật Khẩu Mới
                </label>
                <div class="relative">
                  <input
                    v-model="formData.newPassword"
                    :type="showPassword ? 'text' : 'password'"
                    placeholder="Nhập mật khẩu mới"
                    class="w-full px-4 py-3 pl-12 pr-12 bg-white/10 border border-purple-400/30 rounded-lg text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-purple-400/50 focus:border-purple-400 transition-all"
                    :class="{ 'border-red-400': errors.newPassword }"
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
                <p v-if="errors.newPassword" class="mt-1 text-sm text-red-400">{{ errors.newPassword }}</p>
              </div>

              <!-- Confirm Password Field -->
              <div>
                <label class="block text-white/90 text-sm font-medium mb-2">
                  Xác Nhận Mật Khẩu
                </label>
                <div class="relative">
                  <input
                    v-model="formData.confirmPassword"
                    :type="showConfirmPassword ? 'text' : 'password'"
                    placeholder="Nhập lại mật khẩu mới"
                    class="w-full px-4 py-3 pl-12 pr-12 bg-white/10 border border-purple-400/30 rounded-lg text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-purple-400/50 focus:border-purple-400 transition-all"
                    :class="{ 'border-red-400': errors.confirmPassword }"
                  />
                  <i class="ri-lock-password-line absolute left-4 top-1/2 -translate-y-1/2 text-white/60"></i>
                  <button
                    type="button"
                    @click="showConfirmPassword = !showConfirmPassword"
                    class="absolute right-4 top-1/2 -translate-y-1/2 text-white/60 hover:text-white transition-colors"
                  >
                    <i :class="showConfirmPassword ? 'ri-eye-off-line' : 'ri-eye-line'"></i>
                  </button>
                </div>
                <p v-if="errors.confirmPassword" class="mt-1 text-sm text-red-400">{{ errors.confirmPassword }}</p>
              </div>

              <!-- Error Message -->
              <div v-if="errorMessage" class="bg-red-500/20 border border-red-400/30 rounded-lg p-3">
                <p class="text-red-300 text-sm text-center">{{ errorMessage }}</p>
              </div>

              <!-- Submit Button -->
              <button
                type="submit"
                :disabled="isSubmitting"
                class="w-full bg-gradient-to-r from-purple-600 via-violet-600 to-indigo-600 text-white py-3 rounded-lg font-semibold hover:from-purple-500 hover:via-violet-500 hover:to-indigo-500 transition-all transform hover:scale-[1.02] disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
              >
                <span v-if="!isSubmitting">Đặt Lại Mật Khẩu</span>
                <span v-else class="flex items-center justify-center">
                  <i class="ri-loader-4-line animate-spin mr-2"></i>
                  Đang xử lý...
                </span>
              </button>
            </form>
          </div>

          <!-- Step 3: Success -->
          <div v-if="currentStep === 3" class="text-center">
            <div class="mb-6">
              <div class="w-20 h-20 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                <i class="ri-check-line text-green-400 text-4xl"></i>
              </div>
              <h2 class="text-3xl font-bold text-white mb-2">
                Thành Công!
              </h2>
              <p class="text-purple-200/90 text-sm mb-8">
                Mật khẩu của bạn đã được đặt lại thành công. Đang chuyển đến trang đăng nhập...
              </p>
            </div>
          </div>

          <!-- Back to Login -->
          <div class="mt-6 text-center">
            <button
              @click="goToLogin"
              class="text-purple-300 hover:text-purple-200 text-sm font-medium transition-colors"
            >
              <i class="ri-arrow-left-line mr-1"></i>
              Quay lại đăng nhập
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Additional styles if needed */
</style>

