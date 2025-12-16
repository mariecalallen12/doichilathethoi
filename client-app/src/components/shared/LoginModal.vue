<template>
  <Teleport to="body">
    <Transition name="modal">
      <div
        v-if="isOpen"
        class="fixed inset-0 z-[9999] flex items-center justify-center p-4"
        @click.self="handleClose"
      >
        <!-- Backdrop with blur -->
        <div class="absolute inset-0 bg-black/60 backdrop-blur-sm" @click="handleClose"></div>

        <!-- Modal Content -->
        <div
          class="relative w-full max-w-md bg-gradient-to-br from-purple-900 via-purple-800 to-indigo-900 rounded-2xl shadow-2xl overflow-hidden transform transition-all"
        >
          <!-- Close Button -->
          <button
            @click="handleClose"
            class="absolute top-4 right-4 z-10 w-8 h-8 flex items-center justify-center text-white/80 hover:text-white hover:bg-white/10 rounded-full transition-all"
          >
            <i class="ri-close-line text-xl"></i>
          </button>

          <!-- Modal Body -->
          <div class="relative p-8">
            <!-- Logo Diamond -->
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
              {{ t("loginModal.title") }}
            </h2>
            <p class="text-purple-200/90 text-center mb-8 text-sm">
              {{ t("loginModal.subtitle") }}
            </p>

            <!-- Login Form -->
            <form @submit.prevent="handleSubmit" class="space-y-5">
              <!-- Phone Number Field -->
              <div>
                <label class="block text-white/90 text-sm font-medium mb-2">
                  {{ t("loginModal.emailLabel") }}
                </label>
                <div class="relative">
                  <input
                    v-model="formData.phone"
                    type="tel"
                    :placeholder="t('loginModal.emailPlaceholder')"
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
                  {{ t("loginModal.passwordLabel") }}
                </label>
                <div class="relative">
                  <input
                    v-model="formData.password"
                    :type="showPassword ? 'text' : 'password'"
                    :placeholder="t('loginModal.passwordPlaceholder')"
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
                  <span class="ml-2 text-white/80 text-sm">{{ t("loginModal.rememberMe") }}</span>
                </label>
                <button
                  type="button"
                  class="text-purple-300 hover:text-purple-200 text-sm transition-colors"
                >
                  {{ t("loginModal.forgotPassword") }}
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
                <span v-if="!isSubmitting">{{ t("loginModal.loginButton") }}</span>
                <span v-else class="flex items-center justify-center">
                  <i class="ri-loader-4-line animate-spin mr-2"></i>
                  {{ t("loginModal.loggingIn") }}
                </span>
              </button>
            </form>

            <!-- Divider -->
            <div class="flex items-center my-6">
              <div class="flex-1 h-px bg-white/20"></div>
              <span class="px-4 text-white/60 text-sm">{{ t("loginModal.or") }}</span>
              <div class="flex-1 h-px bg-white/20"></div>
            </div>

            <!-- Social Login Buttons -->
            <div class="space-y-3">
              <!-- Google Login -->
              <button
                type="button"
                @click="handleGoogleLogin"
                class="w-full bg-white/10 hover:bg-white/20 border border-white/20 text-white py-3 rounded-lg font-medium transition-all flex items-center justify-center gap-3"
              >
                <i class="ri-google-fill text-xl"></i>
                <span>{{ t("loginModal.googleLogin") }}</span>
              </button>

              <!-- Facebook Login -->
              <button
                type="button"
                @click="handleFacebookLogin"
                class="w-full bg-white/10 hover:bg-white/20 border border-white/20 text-white py-3 rounded-lg font-medium transition-all flex items-center justify-center gap-3"
              >
                <i class="ri-facebook-fill text-xl"></i>
                <span>{{ t("loginModal.facebookLogin") }}</span>
              </button>
            </div>

            <!-- Register Link -->
            <div class="mt-6 text-center">
              <p class="text-white/70 text-sm">
                {{ t("loginModal.noAccount") }}
                <router-link
                  to="/register"
                  @click="handleClose"
                  class="text-purple-300 hover:text-purple-200 font-semibold transition-colors"
                >
                  {{ t("loginModal.registerNow") }}
                </router-link>
              </p>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { reactive, ref, watch, onBeforeUnmount, nextTick } from "vue";
import { useRouter } from "vue-router";
import { useI18n } from "vue-i18n";
import { accountApi } from "../../services/api/account";

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(["close", "login-success"]);

const router = useRouter();
const { t } = useI18n();

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
    return t("loginModal.validation.emailRequired");
  }
  // Remove spaces and validate phone number format (Vietnamese phone numbers: 10-11 digits, may start with +84 or 0)
  const cleanedPhone = phone.replace(/\s/g, "");
  const phoneRegex = /^(\+84|0)[1-9][0-9]{8,9}$/;
  if (!phoneRegex.test(cleanedPhone)) {
    return t("loginModal.validation.emailInvalid");
  }
  return "";
};

const validatePassword = (password) => {
  if (!password) {
    return t("loginModal.validation.passwordRequired");
  }
  if (password.length < 6) {
    return t("loginModal.validation.passwordMinLength");
  }
  return "";
};

const validateForm = () => {
  errors.phone = validatePhone(formData.phone);
  errors.password = validatePassword(formData.password);
  return !errors.phone && !errors.password;
};

// Watch for real-time validation
watch(
  () => formData.phone,
  () => {
    if (errors.phone) {
      errors.phone = validatePhone(formData.phone);
    }
  }
);

watch(
  () => formData.password,
  () => {
    if (errors.password) {
      errors.password = validatePassword(formData.password);
    }
  }
);

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
    const response = await accountApi.login({
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

    // Emit success event
    emit("login-success", response);
    
    // Close modal
    handleClose();

    // Wait for next tick to ensure localStorage is updated
    await nextTick();

    // Redirect to personal overview or redirect query param
    const redirect = router.currentRoute.value.query.redirect;
    router.push(redirect || "/personal/overview");
  } catch (error) {
    // Handle both axios errors and Error objects
    if (error.response?.data?.detail) {
      errorMessage.value = error.response.data.detail;
    } else if (error.message) {
      errorMessage.value = error.message;
    } else {
      errorMessage.value = t("loginModal.errors.loginFailed");
    }
  } finally {
    isSubmitting.value = false;
  }
};

// Handle close
const handleClose = () => {
  emit("close");
  // Reset form
  formData.phone = "";
  formData.password = "";
  formData.rememberMe = false;
  errors.phone = "";
  errors.password = "";
  errorMessage.value = "";
};

// Social login handlers (UI only for now)
const handleGoogleLogin = () => {
  console.log("Google login clicked");
  // TODO: Implement Google OAuth
};

const handleFacebookLogin = () => {
  console.log("Facebook login clicked");
  // TODO: Implement Facebook OAuth
};

// Close on Escape key
let escapeHandler = null;

watch(
  () => props.isOpen,
  (isOpen) => {
    if (isOpen) {
      escapeHandler = (e) => {
        if (e.key === "Escape") {
          handleClose();
        }
      };
      document.addEventListener("keydown", escapeHandler);
    } else {
      if (escapeHandler) {
        document.removeEventListener("keydown", escapeHandler);
        escapeHandler = null;
      }
    }
  }
);

onBeforeUnmount(() => {
  if (escapeHandler) {
    document.removeEventListener("keydown", escapeHandler);
  }
});
</script>

<style scoped>
/* Modal Transition */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-active .relative,
.modal-leave-active .relative {
  transition: transform 0.3s ease, opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .relative,
.modal-leave-to .relative {
  transform: scale(0.9) translateY(-20px);
  opacity: 0;
}
</style>

