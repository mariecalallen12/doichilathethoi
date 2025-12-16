import { createI18n } from "vue-i18n";

const messages = {
  vi: {
    nav: {
      home: "Trang chủ",
      market: "Thị trường",
      trade: "Giao dịch",
      edu: "Giáo dục",
      analysis: "Phân tích",
    },
    hero: {
      title: "Giao Dịch Forex, Crypto & Vàng Đẳng Cấp Thượng Lưu",
      subtitle:
        "Trải nghiệm giao dịch thượng lưu với công nghệ AI tiên tiến, spread siêu thấp từ 0.0 pips, đòn bẩy linh hoạt lên đến 1:1000. Tận hưởng dịch vụ VIP độc quyền và thanh khoản vô hạn.",
      demo: "Demo VIP Miễn Phí",
      live: "Giao Dịch Thực",
    },
    cta: {
      login: "Đăng nhập",
      signup: "Đăng ký",
      support: "Support 24/7",
    },
    loginModal: {
      title: "Đăng Nhập",
      subtitle: "Truy cập tài khoản giao dịch của bạn",
      emailLabel: "Số điện thoại",
      emailPlaceholder: "Nhập số điện thoại",
      passwordLabel: "Mật khẩu",
      passwordPlaceholder: "Nhập mật khẩu",
      rememberMe: "Ghi nhớ đăng nhập",
      forgotPassword: "Quên mật khẩu?",
      loginButton: "Đăng nhập",
      loggingIn: "Đang đăng nhập...",
      or: "hoặc",
      googleLogin: "Đăng nhập bằng Google",
      facebookLogin: "Đăng nhập bằng Facebook",
      noAccount: "Chưa có tài khoản?",
      registerNow: "Đăng ký ngay",
      validation: {
        emailRequired: "Vui lòng nhập số điện thoại",
        emailInvalid: "Số điện thoại không hợp lệ",
        passwordRequired: "Vui lòng nhập mật khẩu",
        passwordMinLength: "Mật khẩu phải có ít nhất 6 ký tự",
      },
      errors: {
        loginFailed: "Đăng nhập thất bại. Vui lòng kiểm tra lại thông tin.",
      },
    },
  },
  en: {
    nav: {
      home: "Home",
      market: "Markets",
      trade: "Trading",
      edu: "Education",
      analysis: "Research",
    },
    hero: {
      title: "Trade Forex, Crypto & Gold at Elite Level",
      subtitle:
        "Experience elite trading with advanced AI, ultra-low spreads from 0.0 pips, flexible leverage up to 1:1000. Enjoy exclusive VIP service and deep liquidity.",
      demo: "Free VIP Demo",
      live: "Start Live Trading",
    },
    cta: {
      login: "Sign In",
      signup: "Get VIP",
      support: "Support 24/7",
    },
    loginModal: {
      title: "Sign In",
      subtitle: "Access your trading account",
      emailLabel: "Phone Number",
      emailPlaceholder: "Enter phone number",
      passwordLabel: "Password",
      passwordPlaceholder: "Enter password",
      rememberMe: "Remember me",
      forgotPassword: "Forgot password?",
      loginButton: "Sign In",
      loggingIn: "Signing in...",
      or: "or",
      googleLogin: "Sign in with Google",
      facebookLogin: "Sign in with Facebook",
      noAccount: "Don't have an account?",
      registerNow: "Register now",
      validation: {
        emailRequired: "Please enter phone number",
        emailInvalid: "Invalid phone number format",
        passwordRequired: "Please enter password",
        passwordMinLength: "Password must be at least 6 characters",
      },
      errors: {
        loginFailed: "Login failed. Please check your credentials.",
      },
    },
  },
};

export const i18n = createI18n({
  legacy: false,
  locale: "vi",
  fallbackLocale: "vi",
  messages,
});

