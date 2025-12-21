<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref } from "vue";
import { useI18n } from "vue-i18n";
import { useRouter } from "vue-router";
import { Swiper, SwiperSlide } from "swiper/vue";
import { Autoplay, Pagination, EffectCoverflow, Parallax } from "swiper/modules";
import ParticleCanvas from "../components/ParticleCanvas.vue";
import LoginModal from "../components/shared/LoginModal.vue";
import AOS from "aos";
import { useAccountStore } from "../stores/account";
import ChatWidget from "../components/support/ChatWidget.vue"; // Import ChatWidget

const { t, locale } = useI18n();
const router = useRouter();
const accountStore = useAccountStore();

const theme = ref("dark");
const mobileOpen = ref(false);
const showLoginModal = ref(false);
const currentLang = ref("vi");
const languages = [
  { value: "vi", label: "VI" },
  { value: "en", label: "EN" },
];

const toggleTheme = () => {
  theme.value = theme.value === "dark" ? "light" : "dark";
  document.documentElement.setAttribute("data-theme", theme.value);
};

const isLoggedIn = computed(() => !!localStorage.getItem("auth_token"));

const formattedAvailable = computed(() =>
  (accountStore.balance.available ?? 0).toLocaleString("vi-VN", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })
);

const formattedEquity = computed(() =>
  (accountStore.equity ?? 0).toLocaleString("vi-VN", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })
);

const changeLang = (val) => {
  currentLang.value = val;
  locale.value = val;
};

const openLoginModal = () => {
  showLoginModal.value = true;
};

const closeLoginModal = () => {
  showLoginModal.value = false;
};

const handleLoginSuccess = (response) => {
  // Login success handler - redirect is handled in LoginModal component
  console.log("Login successful:", response);
  
  // Store user data if available (backup, though LoginModal already handles this)
  if (response.user) {
    localStorage.setItem("user", JSON.stringify(response.user));
  }
  
  // Note: Redirect is handled in LoginModal.vue to avoid double redirect
  // This handler is kept for potential UI updates or logging
};

const tickerData = reactive([
  { pair: "EUR/USD", price: 1.0845, change: 0.12, history: [1.0845, 1.084, 1.0847], flash: false },
  { pair: "GBP/USD", price: 1.2634, change: -0.08, history: [1.2634, 1.2629, 1.2631], flash: false },
  { pair: "BTC/USD", price: 43250, change: 2.45, history: [43250, 43100, 43290], flash: false },
  { pair: "GOLD", price: 2045.3, change: 0.75, history: [2045.3, 2044.7, 2046.1], flash: false },
  { pair: "USD/JPY", price: 149.85, change: -0.15, history: [149.85, 149.7, 149.9], flash: false },
]);

const stats = [
  { label: "Khách hàng hoạt động", value: "100,000+" },
  { label: "Khối lượng giao dịch/tháng", value: "$2.5B+" },
  { label: "Năm hoạt động", value: "8" },
  { label: "Hỗ trợ khách hàng", value: "24/7" },
];

const compliance = [
  { name: "CySEC", license: "123/45", icon: "fas fa-certificate", color: "text-blue-400" },
  { name: "FCA", license: "678901", icon: "fas fa-shield-alt", color: "text-green-400" },
  { name: "ASIC", license: "AFS 987654", icon: "fas fa-landmark", color: "text-amber-400" },
  { name: "SSL 256-bit", license: "TLS 1.3", icon: "fas fa-lock", color: "text-purple-400" },
];

const testimonials = [
  {
    name: "Nguyễn Minh Anh",
    role: "Pro Trader",
    avatar: "/assets/images/testimonial-1.jpg",
    quote: "Spread thấp, thực thi nhanh, hỗ trợ khách hàng tuyệt vời. Tôi đã giao dịch 2 năm và rất hài lòng.",
  },
  {
    name: "Trần Thị Lan",
    role: "Investor",
    avatar: "/assets/images/testimonial-2.jpg",
    quote: "Nền tảng MT5 mượt, công cụ phân tích đầy đủ. Nạp rút tiền nhanh chóng, không có phí ẩn.",
  },
  {
    name: "Lê Văn Hùng",
    role: "Copy Trader",
    avatar: "/assets/images/testimonial-3.jpg",
    quote: "Copy trading giúp tôi học nhanh. Tài liệu giáo dục phong phú, phù hợp cho người mới.",
  },
];

const education = [
  { title: "Video Tutorials", desc: "50+ video từ cơ bản đến nâng cao", img: "/assets/images/edu-video.jpg", progress: 60 },
  { title: "Ebook Strategies", desc: "Chiến lược giao dịch từ chuyên gia", img: "/assets/images/edu-ebook.jpg", progress: 40 },
  { title: "Lịch Kinh Tế", desc: "Sự kiện quan trọng real-time", img: "/assets/images/edu-calendar.jpg", progress: 25 },
  { title: "Phân Tích Thị Trường", desc: "Báo cáo chuyên sâu hàng ngày", img: "/assets/images/edu-analysis.jpg", progress: 80 },
];

const categories = [
  {
    title: "Forex",
    instruments: "50+ cặp tiền",
    detail: "Spread từ 0.0 pips",
    icon: "ri-exchange-dollar-line",
    color: "from-blue-400 to-cyan-400",
  },
  {
    title: "Cryptocurrency",
    instruments: "20+ crypto",
    detail: "Giao dịch 24/7",
    icon: "ri-bit-coin-fill",
    color: "from-green-400 to-emerald-400",
  },
  {
    title: "Commodities",
    instruments: "Vàng, Dầu, Khí",
    detail: "Thanh khoản cao",
    icon: "ri-oil-line",
    color: "from-amber-400 to-orange-400",
  },
  {
    title: "Indices",
    instruments: "S&P 500, NASDAQ",
    detail: "Đòn bẩy linh hoạt",
    icon: "ri-stock-line",
    color: "from-purple-400 to-pink-400",
  },
];

const activeTraders = ref(12547);
let tickerTimer;
let traderTimer;

const sparkPath = (history) => {
  const points = history.slice(-8);
  const max = Math.max(...points);
  const min = Math.min(...points);
  const range = Math.max(max - min, 0.0001);
  return points
    .map((v, i) => {
      const x = (i / (points.length - 1 || 1)) * 100;
      const y = 100 - ((v - min) / range) * 100;
      return `${i === 0 ? "M" : "L"}${x},${y}`;
    })
    .join(" ");
};

const updateTicker = () => {
  tickerData.forEach((item) => {
    const delta = item.price * (Math.random() * 0.002 - 0.001);
    item.price = +(item.price + delta).toFixed(item.price > 2000 ? 2 : 4);
    item.history.push(item.price);
    if (item.history.length > 12) item.history.shift();
    item.change = +(Math.random() * 0.3 - 0.15).toFixed(2);
    item.flash = true;
    setTimeout(() => {
      item.flash = false;
    }, 500);
  });
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

onMounted(() => {
  AOS.init({ once: true, duration: 700, offset: 60 });
  document.documentElement.setAttribute("data-theme", theme.value);
  tickerTimer = setInterval(updateTicker, 3200);
  traderTimer = setInterval(() => {
    const delta = Math.floor(Math.random() * 600) - 300;
    activeTraders.value = Math.max(12000, activeTraders.value + delta);
  }, 5000);
  observeElems();
  if (isLoggedIn.value) {
    accountStore.fetchBalance().catch((err) => console.error("Fetch balance failed:", err));
  }
});

onBeforeUnmount(() => {
  clearInterval(tickerTimer);
  clearInterval(traderTimer);
});
</script>

<template>
  <div
    class="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-900 text-white relative overflow-hidden"
    :class="theme === 'light' ? 'brightness-105' : ''"
  >
    <div class="absolute inset-0 overflow-hidden pointer-events-none">
      <div class="absolute top-0 -left-10 w-72 h-72 bg-purple-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob"></div>
      <div class="absolute top-10 -right-10 w-80 h-80 bg-indigo-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob"></div>
      <div class="absolute -bottom-10 left-32 w-72 h-72 bg-blue-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob"></div>
    </div>

    <header class="bg-[var(--header-blur)] backdrop-blur-md shadow-2xl sticky top-0 z-50 border-b border-purple-500/20">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <div class="flex items-center space-x-4">
            <div class="relative w-12 h-12 bg-gradient-to-r from-purple-400 via-violet-500 to-indigo-500 rounded-xl flex items-center justify-center shadow-lg">
              <div class="absolute inset-0 bg-gradient-to-r from-purple-600 to-indigo-600 rounded-xl blur opacity-75"></div>
              <i class="fas fa-gem text-white text-xl relative z-10"></i>
              <div class="absolute -top-1 -right-1 w-3 h-3 bg-gradient-to-r from-yellow-400 to-orange-400 rounded-full animate-pulse"></div>
            </div>
            <div class="flex flex-col">
              <span class="text-transparent bg-gradient-to-r from-purple-300 via-violet-300 to-indigo-300 bg-clip-text font-bold text-2xl tracking-wide">CMEETRADING</span>
              <span class="text-purple-400/80 text-xs font-light tracking-widest">CMEETRADING</span>
            </div>
          </div>

          <nav class="hidden lg:flex space-x-8">
            <router-link to="/" class="relative text-purple-100 hover:text-transparent hover:bg-gradient-to-r hover:from-purple-300 hover:to-indigo-300 hover:bg-clip-text transition-all duration-300 cursor-pointer group" active-class="text-transparent bg-gradient-to-r from-purple-300 to-indigo-300 bg-clip-text">
              <span class="relative z-10">{{ t("nav.home") }}</span>
              <div class="absolute bottom-0 left-0 w-0 h-0.5 bg-gradient-to-r from-purple-400 to-indigo-400 group-hover:w-full transition-all duration-300"></div>
            </router-link>
            <router-link to="/market" class="relative text-purple-100 hover:text-transparent hover:bg-gradient-to-r hover:from-purple-300 hover:to-indigo-300 hover:bg-clip-text transition-all duration-300 cursor-pointer group" active-class="text-transparent bg-gradient-to-r from-purple-300 to-indigo-300 bg-clip-text">
              <span class="relative z-10">{{ t("nav.market") }}</span>
              <div class="absolute bottom-0 left-0 w-0 h-0.5 bg-gradient-to-r from-purple-400 to-indigo-400 group-hover:w-full transition-all duration-300"></div>
            </router-link>
            <router-link to="/trading" class="relative text-purple-100 hover:text-transparent hover:bg-gradient-to-r hover:from-purple-300 hover:to-indigo-300 hover:bg-clip-text transition-all duration-300 cursor-pointer group" active-class="text-transparent bg-gradient-to-r from-purple-300 to-indigo-300 bg-clip-text">
              <span class="relative z-10">{{ t("nav.trade") }}</span>
              <div class="absolute bottom-0 left-0 w-0 h-0.5 bg-gradient-to-r from-purple-400 to-indigo-400 group-hover:w-full transition-all duration-300"></div>
            </router-link>
            <router-link to="/education" class="relative text-purple-100 hover:text-transparent hover:bg-gradient-to-r hover:from-purple-300 hover:to-indigo-300 hover:bg-clip-text transition-all duration-300 cursor-pointer group" active-class="text-transparent bg-gradient-to-r from-purple-300 to-indigo-300 bg-clip-text">
              <span class="relative z-10">{{ t("nav.edu") }}</span>
              <div class="absolute bottom-0 left-0 w-0 h-0.5 bg-gradient-to-r from-purple-400 to-indigo-400 group-hover:w-full transition-all duration-300"></div>
            </router-link>
            <router-link to="/analysis" class="relative text-purple-100 hover:text-transparent hover:bg-gradient-to-r hover:from-purple-300 hover:to-indigo-300 hover:bg-clip-text transition-all duration-300 cursor-pointer group" active-class="text-transparent bg-gradient-to-r from-purple-300 to-indigo-300 bg-clip-text">
              <span class="relative z-10">{{ t("nav.analysis") }}</span>
              <div class="absolute bottom-0 left-0 w-0 h-0.5 bg-gradient-to-r from-purple-400 to-indigo-400 group-hover:w-full transition-all duration-300"></div>
            </router-link>
            <router-link to="/personal/overview" class="relative text-purple-100 hover:text-transparent hover:bg-gradient-to-r hover:from-purple-300 hover:to-indigo-300 hover:bg-clip-text transition-all duration-300 cursor-pointer group" active-class="text-transparent bg-gradient-to-r from-purple-300 to-indigo-300 bg-clip-text">
              <span class="relative z-10">Khu vực cá nhân</span>
              <div class="absolute bottom-0 left-0 w-0 h-0.5 bg-gradient-to-r from-purple-400 to-indigo-400 group-hover:w-full transition-all duration-300"></div>
            </router-link>
          </nav>

          <div class="flex items-center space-x-3 md:space-x-4">
            <router-link
              v-if="isLoggedIn"
              to="/personal/wallet"
              class="hidden xl:flex items-center space-x-2 bg-slate-800/70 text-purple-100 px-3 py-2 rounded-lg border border-purple-400/30 hover:bg-slate-700 transition"
            >
              <i class="fas fa-wallet text-purple-300"></i>
              <div class="flex flex-col text-left leading-tight">
                <span class="text-xs text-purple-300">Số dư ví</span>
                <span class="text-sm font-semibold text-white">{{ formattedAvailable }} USD</span>
              </div>
            </router-link>
            <ChatWidget />
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
            <button @click="openLoginModal" class="relative bg-gradient-to-r from-purple-600/80 to-indigo-600/80 backdrop-blur-sm text-white px-4 py-2 rounded-button hover:from-purple-600 hover:to-indigo-600 transition-all transform hover:scale-105 border border-purple-400/30 cursor-pointer whitespace-nowrap hidden sm:block">
              <span class="relative z-10">{{ t("cta.login") }}</span>
            </button>
            <router-link to="/register" class="relative bg-gradient-to-r from-violet-600 via-purple-600 to-indigo-600 text-white px-4 py-2 rounded-button hover:shadow-2xl hover:shadow-purple-500/40 transition-all transform hover:scale-105 cursor-pointer whitespace-nowrap hidden sm:block">
              <span class="relative z-10 font-semibold">{{ t("cta.signup") }}</span>
              <div class="absolute inset-0 bg-gradient-to-r from-violet-600 via-purple-600 to-indigo-600 rounded-button blur opacity-75"></div>
            </router-link>
            <button class="lg:hidden text-white text-2xl" @click="mobileOpen = !mobileOpen">
              <i :class="mobileOpen ? 'ri-close-line' : 'ri-menu-line'"></i>
            </button>
          </div>
        </div>
      </div>
      <div v-if="mobileOpen" class="lg:hidden border-t border-purple-500/20 bg-slate-950/90 backdrop-blur-md">
        <div class="px-4 py-4 space-y-3">
          <div class="flex items-center space-x-3">
            <select
              class="bg-slate-800/70 text-sm px-3 py-2 rounded-lg border border-purple-400/30 text-white focus:outline-none"
              :value="currentLang"
              @change="changeLang($event.target.value)"
            >
              <option v-for="lang in languages" :key="lang.value" :value="lang.value">{{ lang.label }}</option>
            </select>
            <button class="bg-slate-800/70 text-white px-3 py-2 rounded-lg border border-purple-400/30 hover:bg-slate-700 transition" @click="toggleTheme">
              <i :class="theme === 'dark' ? 'ri-sun-line' : 'ri-moon-line'"></i>
            </button>
          </div>
          <div class="flex flex-col space-y-2 text-purple-100">
            <router-link to="/" class="py-2 border-b border-purple-500/10">{{ t("nav.home") }}</router-link>
            <router-link to="/market" class="py-2 border-b border-purple-500/10">{{ t("nav.market") }}</router-link>
            <router-link to="/trading" class="py-2 border-b border-purple-500/10">{{ t("nav.trade") }}</router-link>
            <router-link to="/education" class="py-2 border-b border-purple-500/10">{{ t("nav.edu") }}</router-link>
            <router-link to="/analysis" class="py-2 border-b border-purple-500/10">{{ t("nav.analysis") }}</router-link>
            <router-link to="/personal/overview" class="py-2 border-b border-purple-500/10">Khu vực cá nhân</router-link>
          </div>
          <div class="flex items-center gap-3">
            <button @click="openLoginModal" class="flex-1 bg-gradient-to-r from-purple-600/80 to-indigo-600/80 text-white px-4 py-3 rounded-button border border-purple-400/30">
              {{ t("cta.login") }}
            </button>
            <router-link to="/register" class="flex-1 bg-gradient-to-r from-violet-600 via-purple-600 to-indigo-600 text-white px-4 py-3 rounded-button text-center">
              {{ t("cta.signup") }}
            </router-link>
          </div>
        </div>
      </div>
    </header>

    <section v-if="isLoggedIn" class="bg-slate-900/80 border-b border-purple-500/20 py-6">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4">
          <div class="space-y-1">
            <div class="text-purple-200 text-sm uppercase tracking-wide">Ví cá nhân</div>
            <div class="text-3xl font-bold text-white">{{ formattedAvailable }} USD</div>
            <div class="text-sm text-purple-300">Equity: {{ formattedEquity }} USD</div>
          </div>
          <div class="flex flex-wrap gap-3">
            <router-link
              to="/trading"
              class="px-4 py-3 bg-gradient-to-r from-emerald-500 to-green-500 text-white rounded-lg font-semibold hover:from-emerald-600 hover:to-green-600 transition-all"
            >
              Đặt lệnh Trading
            </router-link>
            <router-link
              to="/personal/wallet"
              class="px-4 py-3 bg-gradient-to-r from-purple-500 to-indigo-500 text-white rounded-lg font-semibold hover:from-purple-600 hover:to-indigo-600 transition-all"
            >
              Xem ví cá nhân
            </router-link>
          </div>
        </div>
      </div>
    </section>

    <div class="bg-gradient-to-r from-slate-950/95 via-purple-950/90 to-slate-950/95 backdrop-blur-md border-b border-purple-500/20 py-3 overflow-hidden relative">
      <div class="absolute inset-0 bg-gradient-to-r from-transparent via-purple-500/5 to-transparent"></div>
      <div class="animate-scroll flex space-x-6 md:space-x-12 text-sm relative z-10">
        <div
          v-for="item in tickerData"
          :key="item.pair"
          class="flex items-center space-x-3 whitespace-nowrap bg-purple-900/20 px-4 py-2 rounded-lg backdrop-blur-sm border border-purple-500/20"
          :class="item.flash ? 'flash' : ''"
        >
          <span class="text-purple-300 font-medium">{{ item.pair }}</span>
          <span :class="item.change >= 0 ? 'text-emerald-400 led-text font-bold' : 'text-red-400 led-text font-bold'">
            {{ item.price }}
          </span>
          <span
            :class="[
              'text-xs px-2 py-1 rounded-full',
              item.change >= 0 ? 'text-emerald-400 bg-emerald-500/20' : 'text-red-400 bg-red-500/20',
            ]"
          >
            {{ item.change >= 0 ? "+" : "" }}{{ item.change }}%
          </span>
          <svg viewBox="0 0 100 100" class="w-16 h-6">
            <path
              :d="sparkPath(item.history)"
              :stroke="item.change >= 0 ? '#34d399' : '#f87171'"
              fill="none"
              stroke-width="2"
            />
          </svg>
        </div>
      </div>
    </div>

    <section class="relative min-h-screen flex items-center justify-center overflow-hidden">
      <div
        class="absolute inset-0 bg-cover bg-center opacity-30"
        style="background-image: url('/assets/images/hero-bg.jpg')"
      ></div>
      <div class="absolute inset-0 bg-gradient-to-br from-purple-950/80 via-slate-950/60 to-indigo-950/80"></div>
      <ParticleCanvas />
      <div class="absolute inset-0">
        <div class="absolute top-20 left-10 w-20 h-20 border border-purple-400/30 rounded-lg rotate-45 animate-spin-slow"></div>
        <div class="absolute top-40 right-20 w-16 h-16 bg-gradient-to-r from-purple-500/20 to-indigo-500/20 rounded-full animate-float"></div>
        <div class="absolute bottom-32 left-32 w-12 h-12 border border-violet-400/40 rotate-12 animate-pulse"></div>
      </div>
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 py-16 lg:py-24">
        <div class="grid lg:grid-cols-2 gap-12 items-center">
          <div class="text-white observe">
            <div class="mb-4 flex items-center space-x-2">
              <div class="w-12 h-0.5 bg-gradient-to-r from-purple-400 to-violet-400"></div>
              <span class="text-purple-300 text-sm font-light tracking-widest uppercase">Premium Trading</span>
            </div>
            <h1 class="text-5xl sm:text-6xl lg:text-7xl font-bold mb-8 leading-tight">
              <span class="block mb-2">Giao Dịch</span>
              <span class="bg-gradient-to-r from-purple-300 via-violet-300 to-indigo-300 bg-clip-text text-transparent">Trading</span>,
              <span class="bg-gradient-to-r from-emerald-300 via-teal-300 to-cyan-300 bg-clip-text text-transparent">Crypto</span>
              &
              <span class="bg-gradient-to-r from-yellow-300 via-orange-300 to-amber-300 bg-clip-text text-transparent">Vàng</span>
              <span class="block mt-2 text-5xl lg:text-6xl">Đẳng Cấp Thượng Lưu</span>
            </h1>
            <p class="text-xl text-purple-200/90 mb-10 leading-relaxed max-w-2xl">
              {{ t("hero.subtitle") }}
            </p>
            <div class="flex items-center flex-wrap gap-4 sm:gap-8 mb-10">
              <div class="flex items-center space-x-2">
                <div class="w-3 h-3 bg-gradient-to-r from-emerald-400 to-green-400 rounded-full animate-pulse"></div>
                <span class="text-purple-200 text-sm">Spread từ 0.0 pips</span>
              </div>
              <div class="flex items-center space-x-2">
                <div class="w-3 h-3 bg-gradient-to-r from-purple-400 to-violet-400 rounded-full animate-pulse"></div>
                <span class="text-purple-200 text-sm">Đòn bẩy 1:1000</span>
              </div>
              <div class="flex items-center space-x-2">
                <div class="w-3 h-3 bg-gradient-to-r from-yellow-400 to-orange-400 rounded-full animate-pulse"></div>
                <span class="text-purple-200 text-sm">Thực thi tức thì</span>
              </div>
            </div>
            <div class="flex flex-col sm:flex-row gap-4 sm:gap-6 mb-8">
              <button class="relative group bg-gradient-to-r from-purple-600 via-violet-600 to-indigo-600 text-white px-10 py-5 rounded-button text-lg font-bold hover:shadow-2xl hover:shadow-purple-500/50 transition-all transform hover:scale-105 cursor-pointer whitespace-nowrap overflow-hidden">
                <div class="absolute inset-0 bg-gradient-to-r from-purple-600 via-violet-600 to-indigo-600 opacity-0 group-hover:opacity-100 transition-opacity blur"></div>
                <span class="relative z-10 flex items-center"><i class="fas fa-chart-line mr-3 text-xl"></i>{{ t("hero.demo") }}</span>
              </button>
              <button class="relative group bg-gradient-to-r from-amber-500 via-yellow-500 to-orange-500 text-black px-10 py-5 rounded-button text-lg font-bold hover:shadow-2xl hover:shadow-yellow-500/50 transition-all transform hover:scale-105 cursor-pointer whitespace-nowrap overflow-hidden">
                <div class="absolute inset-0 bg-gradient-to-r from-amber-400 via-yellow-400 to-orange-400 opacity-0 group-hover:opacity-100 transition-opacity blur"></div>
                <span class="relative z-10 flex items-center font-black"><i class="fas fa-crown mr-3 text-xl"></i>{{ t("hero.live") }}</span>
              </button>
            </div>
            <div class="flex flex-wrap gap-4 text-sm">
              <div class="flex items-center bg-gradient-to-r from-purple-900/40 to-indigo-900/40 backdrop-blur-sm px-4 py-2 rounded-lg border border-purple-500/20">
                <i class="fas fa-shield-check text-emerald-400 mr-3"></i>
                <span class="text-purple-200">Giấy phép CySEC &amp; FCA</span>
              </div>
              <div class="flex items-center bg-gradient-to-r from-purple-900/40 to-indigo-900/40 backdrop-blur-sm px-4 py-2 rounded-lg border border-purple-500/20">
                <i class="fas fa-lock text-violet-400 mr-3"></i>
                <span class="text-purple-200">Bảo mật Military Grade</span>
              </div>
              <div class="flex items-center bg-gradient-to-r from-purple-900/40 to-indigo-900/40 backdrop-blur-sm px-4 py-2 rounded-lg border border-purple-500/20">
                <i class="fas fa-infinity text-yellow-400 mr-3"></i>
                <span class="text-purple-200">Thanh khoản vô hạn</span>
              </div>
            </div>
          </div>

          <div class="relative observe">
            <div class="relative transform rotate-3 hover:rotate-0 transition-all duration-700 hover:scale-105">
              <div class="absolute -inset-4 bg-gradient-to-r from-purple-500 via-violet-500 to-indigo-500 rounded-2xl blur-lg opacity-30"></div>
              <div class="relative perspective-1000">
                <img
                  src="/assets/images/hero-platform.jpg"
                  alt="Luxury Trading Platform"
                  class="relative w-full h-auto rounded-2xl shadow-2xl border border-purple-500/30 transform rotate-y-6"
                  loading="lazy"
                />
                <img
                  src="/assets/images/platform-mt5.jpg"
                  alt="MT5 Mobile"
                  class="absolute -right-8 bottom-6 w-40 rounded-xl shadow-xl border border-purple-500/40 transform rotate-y-3"
                  loading="lazy"
                />
              </div>
              <div class="absolute inset-0 bg-gradient-to-tr from-purple-600/20 via-violet-500/15 to-indigo-600/20 rounded-2xl"></div>
              <div class="absolute -top-4 -right-4 w-8 h-8 bg-gradient-to-r from-yellow-400 to-orange-400 rounded-full animate-bounce shadow-lg"></div>
              <div class="absolute -bottom-2 -left-2 w-6 h-6 bg-gradient-to-r from-emerald-400 to-green-400 rounded-full animate-pulse shadow-lg"></div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="py-20 bg-slate-800">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-16 observe">
          <h2 class="text-4xl font-bold text-white mb-4">Danh Mục Tài Sản Giao Dịch</h2>
          <p class="text-xl text-gray-300">Giao dịch đa dạng trên một nền tảng duy nhất</p>
        </div>
        <div class="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
          <div
            v-for="item in categories"
            :key="item.title"
            class="bg-gradient-to-br from-slate-700 to-slate-800 p-8 rounded-xl hover:from-slate-700 hover:to-slate-900 transition-all transform hover:scale-105 cursor-pointer relative overflow-hidden observe"
          >
            <div class="absolute inset-0 opacity-40 blur-2xl" :class="`bg-gradient-to-r ${item.color}`"></div>
            <div class="relative text-center">
              <div
                class="w-16 h-16 mx-auto mb-4 bg-gradient-to-r rounded-full flex items-center justify-center animate-spin-slow"
                :class="item.color"
              >
                <i :class="`${item.icon} text-white text-2xl`"></i>
              </div>
              <h3 class="text-xl font-bold text-white mb-2">{{ item.title }}</h3>
              <p class="text-gray-300 mb-2">{{ item.instruments }}</p>
              <div class="text-sm text-blue-200">{{ item.detail }}</div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="py-20 bg-gradient-to-br from-slate-900 to-blue-900">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-16 observe">
          <h2 class="text-4xl font-bold text-white mb-4">Cách Thức Hoạt Động</h2>
          <p class="text-xl text-gray-300">Bắt đầu giao dịch chỉ trong 3 bước đơn giản</p>
        </div>
        <div class="grid md:grid-cols-3 gap-12">
          <div class="text-center observe" data-aos="fade-up">
            <div class="w-20 h-20 mx-auto mb-6 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-full flex items-center justify-center text-white text-2xl font-bold">
              <i class="ri-checkbox-circle-fill text-3xl"></i>
            </div>
            <h3 class="text-2xl font-bold text-white mb-4">Đăng Ký &amp; Xác Thực</h3>
            <p class="text-gray-300 leading-relaxed">
              Tạo tài khoản miễn phí và hoàn tất quy trình xác thực KYC theo tiêu chuẩn quốc tế chỉ trong vài phút
            </p>
          </div>
          <div class="text-center observe" data-aos="fade-up" data-aos-delay="100">
            <div class="w-20 h-20 mx-auto mb-6 bg-gradient-to-r from-green-500 to-emerald-500 rounded-full flex items-center justify-center text-white text-2xl font-bold">
              <i class="ri-wallet-3-fill text-3xl"></i>
            </div>
            <h3 class="text-2xl font-bold text-white mb-4">Nạp Tiền</h3>
            <p class="text-gray-300 leading-relaxed">Nạp tiền qua ngân hàng, ví điện tử hoặc thẻ tín dụng. Xử lý tức thì, không phí giao dịch</p>
          </div>
          <div class="text-center observe" data-aos="fade-up" data-aos-delay="200">
            <div class="w-20 h-20 mx-auto mb-6 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center text-white text-2xl font-bold">
              <i class="ri-line-chart-fill text-3xl"></i>
            </div>
            <h3 class="text-2xl font-bold text-white mb-4">Bắt Đầu Giao Dịch</h3>
            <p class="text-gray-300 leading-relaxed">
              Sử dụng nền tảng MT5 hoặc WebTrader để giao dịch với biểu đồ chuyên nghiệp và công cụ phân tích
            </p>
          </div>
        </div>
      </div>
    </section>

    <section class="py-20 bg-slate-800">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="grid lg:grid-cols-2 gap-12 items-center">
          <div class="observe">
            <h2 class="text-4xl font-bold text-white mb-6">Nền Tảng Giao Dịch Chuyên Nghiệp</h2>
            <p class="text-xl text-gray-300 mb-8">Trải nghiệm giao dịch tối ưu với công nghệ hàng đầu</p>
            <div class="space-y-4 mb-8">
              <div class="flex items-center space-x-3">
                <i class="fas fa-check-circle text-green-400"></i>
                <span class="text-white">Biểu đồ TradingView tích hợp</span>
              </div>
              <div class="flex items-center space-x-3">
                <i class="fas fa-check-circle text-green-400"></i>
                <span class="text-white">100+ chỉ báo kỹ thuật</span>
              </div>
              <div class="flex items-center space-x-3">
                <i class="fas fa-check-circle text-green-400"></i>
                <span class="text-white">Giao dịch 1-click</span>
              </div>
              <div class="flex items-center space-x-3">
                <i class="fas fa-check-circle text-green-400"></i>
                <span class="text-white">Copy Trading tự động</span>
              </div>
            </div>
            <button class="bg-gradient-to-r from-blue-500 to-cyan-500 text-white px-8 py-4 rounded-button text-lg font-semibold hover:from-blue-600 hover:to-cyan-600 transition-all cursor-pointer whitespace-nowrap">
              <i class="fas fa-desktop mr-2"></i>Dùng Thử Demo
            </button>
            <div class="mt-4 text-sm text-gray-400 flex items-center gap-4 flex-wrap">
              <span class="flex items-center"><i class="fas fa-users mr-2"></i>{{ activeTraders.toLocaleString() }} người đang giao dịch</span>
              <span class="flex items-center"><i class="fas fa-shield-alt mr-2"></i>2FA &amp; Biometric Ready</span>
              <span class="flex items-center"><i class="fas fa-wifi mr-2"></i>WebSocket realtime</span>
            </div>
          </div>
          <div class="relative observe">
            <div class="relative">
              <img src="/assets/images/platform-mt5.jpg" alt="MT5 Platform" class="w-full h-auto rounded-lg shadow-2xl" loading="lazy" />
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="py-20 bg-gradient-to-br from-slate-900 to-blue-900 relative overflow-hidden">
      <div class="parallax-layer" data-speed="0.4"></div>
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative">
        <div class="text-center mb-16 observe">
          <h2 class="text-4xl font-bold text-white mb-4">Tuân Thủ Pháp Luật &amp; Bảo Mật</h2>
          <p class="text-xl text-gray-300">Được quản lý bởi các cơ quan uy tín quốc tế</p>
        </div>
        <div class="grid md:grid-cols-2 lg:grid-cols-4 gap-8 mb-12">
          <div
            v-for="item in compliance"
            :key="item.name"
            class="bg-slate-800 p-6 rounded-xl text-center border border-purple-500/10 observe"
          >
            <i :class="`${item.icon} ${item.color} text-3xl mb-4`"></i>
            <h3 class="text-white font-bold mb-2">{{ item.name }}</h3>
            <p class="text-gray-300 text-sm">Giấy phép: {{ item.license }}</p>
          </div>
        </div>
        <div class="bg-red-900/20 border border-red-500/30 rounded-lg p-6 observe">
          <div class="flex items-start space-x-3">
            <i class="fas fa-exclamation-triangle text-red-400 text-xl mt-1"></i>
            <div>
              <h4 class="text-red-400 font-bold mb-2">Cảnh Báo Rủi Ro</h4>
              <p class="text-gray-300 text-sm leading-relaxed">
                Giao dịch CFD và Forex có rủi ro cao và có thể không phù hợp với tất cả nhà đầu tư. Bạn có thể mất một phần hoặc toàn bộ khoản đầu tư của mình. Vui lòng đảm bảo bạn hiểu rõ các rủi ro liên quan.
              </p>
              <p class="text-gray-400 text-xs mt-2">Bảo hiểm tiền gửi: Lên đến €20,000. Chuẩn SSL 256-bit. 2FA &amp; Biometric được khuyến nghị.</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="py-20 bg-slate-800">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-16 observe">
          <h2 class="text-4xl font-bold text-white mb-4">Tài Nguyên Giáo Dục</h2>
          <p class="text-xl text-gray-300">Nâng cao kỹ năng giao dịch với tài liệu chuyên nghiệp</p>
        </div>
        <div class="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
          <div
            v-for="item in education"
            :key="item.title"
            class="bg-gradient-to-br from-slate-700 to-slate-800 rounded-xl overflow-hidden hover:transform hover:scale-105 transition-all cursor-pointer observe"
          >
            <img :src="item.img" :alt="item.title" class="w-full h-48 object-cover" loading="lazy" />
            <div class="p-6 space-y-3">
              <h3 class="text-white font-bold mb-1">{{ item.title }}</h3>
              <p class="text-gray-300 text-sm mb-2">{{ item.desc }}</p>
              <div class="h-2 bg-slate-600 rounded-full overflow-hidden">
                <div class="h-full bg-gradient-to-r from-purple-400 to-indigo-400" :style="{ width: `${item.progress}%` }"></div>
              </div>
              <div class="flex items-center justify-between text-sm text-gray-300">
                <span>Tiến độ: {{ item.progress }}%</span>
                <i class="fas fa-play-circle text-purple-300"></i>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="py-20 bg-gradient-to-br from-slate-900 to-blue-900 relative overflow-hidden">
      <div class="parallax-layer" data-speed="0.3"></div>
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative">
        <div class="text-center mb-12 observe">
          <h2 class="text-4xl font-bold text-white mb-3">Khách Hàng Nói Gì</h2>
          <p class="text-xl text-gray-300">Hơn 100,000 trader tin tưởng lựa chọn</p>
        </div>
        <Swiper
          :modules="[Autoplay, Pagination, EffectCoverflow, Parallax]"
          :slides-per-view="1"
          :space-between="24"
          :autoplay="{ delay: 2800 }"
          :pagination="{ clickable: true }"
          effect="coverflow"
          :breakpoints="{ 768: { slidesPerView: 2 }, 1024: { slidesPerView: 3 } }"
          class="pb-12"
        >
          <SwiperSlide v-for="item in testimonials" :key="item.name">
            <div class="bg-slate-800 p-8 rounded-xl shadow-lg observe">
              <div class="flex items-center mb-4">
                <img :src="item.avatar" alt="Client" class="w-12 h-12 rounded-full mr-4" loading="lazy" />
                <div>
                  <h4 class="text-white font-bold">{{ item.name }}</h4>
                  <div class="text-sm text-gray-400">{{ item.role }}</div>
                  <div class="flex text-yellow-400">
                    <i class="fas fa-star" v-for="n in 5" :key="n"></i>
                  </div>
                </div>
              </div>
              <p class="text-gray-300 italic">"{{ item.quote }}"</p>
            </div>
          </SwiperSlide>
        </Swiper>

        <div class="grid md:grid-cols-4 gap-8 text-center observe">
          <div v-for="item in stats" :key="item.label">
            <div class="text-3xl font-bold text-white mb-2">{{ item.value }}</div>
            <div class="text-gray-300">{{ item.label }}</div>
          </div>
        </div>
      </div>
    </section>

    <footer class="bg-slate-900 py-16">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="grid md:grid-cols-4 gap-8 mb-12">
          <div>
            <div class="flex items-center space-x-2 mb-6">
              <div class="w-10 h-10 bg-gradient-to-r from-blue-400 to-cyan-400 rounded-lg flex items-center justify-center">
                <i class="fas fa-chart-line text-white text-lg"></i>
              </div>
              <span class="text-white font-bold text-xl">TradePro</span>
            </div>
            <p class="text-gray-300 mb-4">Nền tảng giao dịch Forex, Crypto và hàng hóa hàng đầu Việt Nam</p>
            <div class="flex space-x-4">
              <a class="text-gray-400 hover:text-blue-400 cursor-pointer"><i class="fab fa-facebook text-xl"></i></a>
              <a class="text-gray-400 hover:text-blue-400 cursor-pointer"><i class="fab fa-twitter text-xl"></i></a>
              <a class="text-gray-400 hover:text-blue-400 cursor-pointer"><i class="fab fa-linkedin text-xl"></i></a>
              <a class="text-gray-400 hover:text-blue-400 cursor-pointer"><i class="fab fa-youtube text-xl"></i></a>
            </div>
          </div>

          <div>
            <h3 class="text-white font-bold mb-4">Giao Dịch</h3>
            <ul class="space-y-2">
              <li><a class="text-gray-300 hover:text-white cursor-pointer">Forex</a></li>
              <li><a class="text-gray-300 hover:text-white cursor-pointer">Cryptocurrency</a></li>
              <li><a class="text-gray-300 hover:text-white cursor-pointer">Hàng hóa</a></li>
              <li><a class="text-gray-300 hover:text-white cursor-pointer">Chỉ số</a></li>
            </ul>
          </div>

          <div>
            <h3 class="text-white font-bold mb-4">Hỗ Trợ</h3>
            <ul class="space-y-2">
              <li><router-link to="/help" class="text-gray-300 hover:text-white cursor-pointer">Trung tâm trợ giúp</router-link></li>
              <li><router-link to="/contact" class="text-gray-300 hover:text-white cursor-pointer">Liên hệ</router-link></li>
              <li><router-link to="/faq" class="text-gray-300 hover:text-white cursor-pointer">FAQ</router-link></li>
            </ul>
          </div>

          <div>
            <h3 class="text-white font-bold mb-4">Pháp Lý</h3>
            <ul class="space-y-2">
              <li><router-link to="/terms" class="text-gray-300 hover:text-white cursor-pointer">Điều khoản sử dụng</router-link></li>
              <li><router-link to="/privacy" class="text-gray-300 hover:text-white cursor-pointer">Chính sách bảo mật</router-link></li>
              <li><router-link to="/risk-warning" class="text-gray-300 hover:text-white cursor-pointer">Cảnh báo rủi ro</router-link></li>
              <li><router-link to="/complaints" class="text-gray-300 hover:text-white cursor-pointer">Khiếu nại</router-link></li>
            </ul>
          </div>
        </div>
        <div class="border-t border-slate-700 pt-8">
          <div class="flex flex-col md:flex-row justify-between items-start gap-4 md:items-center">
            <div class="text-gray-400 text-sm">
              <div>© 2025 TradePro. Tất cả quyền được bảo lưu.</div>
              <div class="mt-1">Địa chỉ: 123 Nguyễn Huệ, Quận 1, TP.HCM</div>
              <div class="mt-1">Hotline: +84 1900 1234 • Email: support@tradpro.vn</div>
            </div>
            <div class="flex items-center space-x-4 text-gray-400 text-2xl">
              <i class="fab fa-cc-visa"></i>
              <i class="fab fa-cc-mastercard"></i>
              <i class="fab fa-paypal"></i>
              <i class="fas fa-university"></i>
            </div>
          </div>
        </div>
      </div>
    </footer>


    <!-- Login Modal -->
    <LoginModal
      :is-open="showLoginModal"
      @close="closeLoginModal"
      @login-success="handleLoginSuccess"
    />
  </div>
</template>
