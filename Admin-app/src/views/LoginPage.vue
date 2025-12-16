<script setup>
import { ref, reactive } from "vue";
import { useRouter, useRoute } from "vue-router";
import ParticleBackground from "../components/ParticleBackground.vue";
import { useAuthStore } from "../store/auth";

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();

const formData = reactive({
  username: "",
  password: "",
  rememberMe: false,
});

const showPassword = ref(false);
const isSubmitting = ref(false);
const errorMessage = ref("");

const handleSubmit = async (e) => {
  e.preventDefault();
  errorMessage.value = "";
  isSubmitting.value = true;
  
  try {
    // Login and wait for it to complete
    await authStore.login({
      email: formData.username, // Use email for login
      password: formData.password
    });
    
    // Ensure auth state is fully updated before redirect
    // Wait a tick to ensure store state is propagated
    await new Promise(resolve => setTimeout(resolve, 100));
    
    // Verify authentication state before redirect
    if (!authStore.isAuthenticated) {
      throw new Error('Xác thực không thành công. Vui lòng thử lại.');
    }
    
    // Get redirect path from query or default to dashboard
    const redirectPath = route.query.redirect || "/dashboard";
    
    // Use named route if possible, otherwise use path
    // Ensure path is relative to router base (/admin/)
    let redirectTarget;
    if (redirectPath === "/dashboard" || redirectPath === "/admin/dashboard") {
      redirectTarget = { name: "Dashboard" };
    } else if (redirectPath.startsWith("/admin/")) {
      // Remove /admin/ prefix as router base already handles it
      const pathWithoutBase = redirectPath.replace(/^\/admin\//, "/");
      redirectTarget = pathWithoutBase;
    } else {
      // Use path as-is, router will handle base path
      redirectTarget = redirectPath.startsWith("/") ? redirectPath : `/${redirectPath}`;
    }
    
    console.log('[Login] Redirecting to:', redirectTarget);
    
    // Perform redirect
    await router.push(redirectTarget);
    
    // If still on login page after redirect, force navigation
    if (route.name === "Login") {
      console.warn('[Login] Still on login page, forcing redirect to dashboard');
      router.replace({ name: "Dashboard" });
    }
  } catch (error) {
    console.error('Login error:', error);
    
    // Handle different error types with better user feedback
    if (error.name === 'NetworkError' || error.message?.includes('fetch') || error.message?.includes('CORS')) {
      errorMessage.value = 'Không thể kết nối đến server. Vui lòng kiểm tra cấu hình API hoặc liên hệ quản trị viên.';
    } else if (error.message?.includes('401') || error.message?.includes('Unauthorized')) {
      errorMessage.value = 'Email hoặc mật khẩu không đúng. Vui lòng thử lại.';
    } else if (error.message?.includes('429') || error.message?.includes('Rate limit')) {
      errorMessage.value = 'Quá nhiều yêu cầu. Vui lòng đợi vài giây rồi thử lại.';
    } else if (error.message) {
      errorMessage.value = error.message;
    } else if (error.detail) {
      errorMessage.value = error.detail;
    } else {
      errorMessage.value = "Đăng nhập thất bại. Vui lòng thử lại.";
    }
  } finally {
    isSubmitting.value = false;
  }
};
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-900 via-indigo-900 to-slate-900 relative overflow-hidden">
    <!-- Particle Background -->
    <ParticleBackground />

    <!-- Header -->
    <header class="relative z-10 px-6 py-6 sm:px-8 sm:py-8">
      <div class="flex items-center space-x-3">
        <div class="w-10 h-10 sm:w-12 sm:h-12 bg-gradient-button rounded-lg flex items-center justify-center shadow-lg">
          <i class="fas fa-crown text-white text-lg sm:text-xl"></i>
        </div>
        <div>
          <h1 class="text-white text-xl sm:text-2xl font-bold font-secular">AdminPortal</h1>
          <p class="text-white/60 text-xs sm:text-sm font-light uppercase tracking-widest">Administrator System</p>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="relative z-10 flex items-center justify-center min-h-[calc(100vh-200px)] px-4 py-8">
      <div class="w-full max-w-md">
        <!-- Login Card -->
        <div class="glass-effect rounded-2xl p-10 shadow-glass-lg relative">
          <!-- Gradient Border Effect -->
          <div class="absolute inset-0 rounded-2xl bg-gradient-to-r from-blue-primary/30 via-purple-primary/30 to-blue-primary/30 opacity-60 blur-xl -z-10"></div>
          
          <!-- Shield Icon -->
          <div class="flex justify-center mb-6">
          <div class="w-20 h-20 bg-gradient-button rounded-full flex items-center justify-center shadow-lg relative">
            <div class="absolute inset-0 bg-gradient-button rounded-full blur-xl opacity-50"></div>
              <i class="fas fa-shield-alt text-white text-3xl relative z-10"></i>
            </div>
          </div>

          <!-- Title -->
          <h2 class="text-3xl font-bold text-white text-center mb-2">Đăng nhập quản trị</h2>
          <p class="text-white/70 text-base text-center mb-8">Truy cập vào hệ thống quản lý</p>

          <!-- Login Form -->
          <form @submit.prevent="handleSubmit" class="space-y-5">
            <!-- Username Field -->
            <div>
              <div class="relative">
                <i class="fas fa-user absolute left-4 top-1/2 -translate-y-1/2 text-white/60 text-sm"></i>
                <input
                  v-model="formData.username"
                  type="text"
                  placeholder="Tên đăng nhập"
                  class="w-full px-4 py-3 pl-12 pr-4 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/50 transition-all"
                  required
                />
              </div>
            </div>

            <!-- Password Field -->
            <div>
              <div class="relative">
                <i class="fas fa-lock absolute left-4 top-1/2 -translate-y-1/2 text-white/60 text-sm"></i>
                <input
                  v-model="formData.password"
                  :type="showPassword ? 'text' : 'password'"
                  placeholder="Mật khẩu"
                  class="w-full px-4 py-3 pl-12 pr-12 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/50 transition-all"
                  required
                />
                <button
                  type="button"
                  @click="showPassword = !showPassword"
                  class="absolute right-4 top-1/2 -translate-y-1/2 text-white/60 hover:text-white transition-colors"
                >
                  <i :class="showPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
                </button>
              </div>
            </div>

            <!-- Remember Me & Forgot Password -->
            <div class="flex items-center justify-between">
              <label class="flex items-center cursor-pointer group">
                <input
                  v-model="formData.rememberMe"
                  type="checkbox"
                  class="w-4 h-4 rounded border-white/30 bg-white/10 text-primary focus:ring-primary/50 focus:ring-2 cursor-pointer"
                />
                <span class="ml-2 text-white/80 text-sm group-hover:text-white transition-colors">Ghi nhớ đăng nhập</span>
              </label>
              <a href="#" class="text-primary-light hover:text-primary text-sm transition-colors">Quên mật khẩu?</a>
            </div>

            <!-- Error Message -->
            <div v-if="errorMessage" class="bg-red-500/20 border border-red-500/50 rounded-lg p-3 flex items-start space-x-2">
              <i class="fas fa-exclamation-circle text-red-400 mt-0.5"></i>
              <p class="text-red-300 text-sm flex-1">{{ errorMessage }}</p>
            </div>

            <!-- Login Button -->
            <button
              type="submit"
              :disabled="isSubmitting"
              class="w-full bg-gradient-button text-white py-3.5 rounded-lg font-semibold hover:opacity-90 transition-all transform hover:scale-[1.02] disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none flex items-center justify-center space-x-2 shadow-lg"
            >
              <span v-if="!isSubmitting" class="flex items-center">
                Đăng nhập hệ thống
                <i class="fas fa-arrow-right ml-2 text-sm"></i>
              </span>
              <span v-else class="flex items-center">
                <i class="fas fa-spinner fa-spin mr-2"></i>
                Đang đăng nhập...
              </span>
            </button>

            <!-- Terms -->
            <p class="text-white/60 text-xs text-center mt-4">
              Bằng việc đăng nhập, bạn đồng ý với
              <a href="#" class="text-primary-light hover:text-primary underline">Điều khoản sử dụng</a>
            </p>
          </form>
        </div>
      </div>
    </main>

    <!-- Footer -->
    <footer class="relative z-10 px-4 py-6">
      <div class="flex flex-col items-center space-y-4">
        <!-- Security Badge -->
        <div class="bg-yellow-400/20 border border-yellow-400/40 rounded-full px-5 py-2.5 flex items-center space-x-2 shadow-md">
          <i class="fas fa-shield-alt text-yellow-400 text-sm"></i>
          <span class="text-yellow-300 text-xs sm:text-sm font-medium">Kết nối được bảo mật bằng SSL 256-bit</span>
        </div>
        
        <!-- Designed By -->
        <div class="flex items-center space-x-2 text-white/40 text-xs">
          <span>Designed by</span>
          <div class="w-4 h-4 bg-gradient-button rounded-sm"></div>
        </div>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.glass-effect {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

input[type="checkbox"] {
  appearance: none;
  -webkit-appearance: none;
  -moz-appearance: none;
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.1);
  cursor: pointer;
  position: relative;
  transition: all 0.3s ease;
}

input[type="checkbox"]:checked {
  background: linear-gradient(135deg, #0066cc 0%, #0052a3 100%);
  border-color: rgba(0, 102, 204, 0.5);
}

input[type="checkbox"]:checked::after {
  content: "✓";
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: white;
  font-size: 12px;
  font-weight: bold;
}

input[type="checkbox"]:hover {
  border-color: rgba(255, 255, 255, 0.5);
}
</style>

