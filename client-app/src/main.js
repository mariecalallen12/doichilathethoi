import { createApp } from "vue";
import { createPinia } from "pinia";
import "./style.css";
import "./styles/trading.css";
import "./styles/market.css";
import "./styles/themes.css";
import "@fortawesome/fontawesome-free/css/all.min.css";
import "remixicon/fonts/remixicon.css";
import "swiper/swiper-bundle.css";
import "aos/dist/aos.css";
import { i18n } from "./i18n";
import router from "./router";
import App from "./App.vue";
import { useWebSocketStore } from "./stores/websocket";
import { logWarning, logInfo, startTimer } from "./services/utils/logging";
import { setupDevToolsIntegration } from "./services/diagnostics/devToolsIntegration";

// Register PWA service worker if available
// PWA plugin may be disabled in production builds to avoid lightweight-charts issues
if ("serviceWorker" in navigator) {
  // Use dynamic import with error handling for PWA registration
  // This allows the app to work even if PWA plugin is disabled
  import("virtual:pwa-register")
    .then((module) => {
      if (module && module.registerSW) {
        module.registerSW({ immediate: true });
      }
    })
    .catch(() => {
      // PWA plugin is disabled or not available, continue without it
      // This is expected in production builds where PWA is disabled
    });
}

const pinia = createPinia();
const app = createApp(App);

// Global error message translation interceptor
// This ensures "Not Found" is always translated to Vietnamese
if (typeof window !== 'undefined') {
  // Intercept all toast events
  const originalDispatchEvent = window.dispatchEvent;
  window.dispatchEvent = function(event) {
    if (event.type === 'toast' && event.detail) {
      const message = event.detail.message;
      if (message === 'Not Found' || message === 'Not found' || message === 'not found' ||
          (typeof message === 'string' && message.toLowerCase().trim() === 'not found')) {
        console.log('[DEBUG] Global interceptor: Translating "Not Found" in toast event');
        event.detail.message = 'Không tìm thấy tài nguyên yêu cầu';
      }
    }
    return originalDispatchEvent.call(this, event);
  };
  
  // Also intercept console.error for debugging
  const originalConsoleError = console.error;
  console.error = function(...args) {
    if (args.some(arg => typeof arg === 'string' && arg.includes('Not Found'))) {
      console.log('[DEBUG] Global interceptor: Found "Not Found" in console.error');
    }
    return originalConsoleError.apply(console, args);
  };
}

app.use(pinia);
app.use(i18n);
app.use(router);

router.isReady().then(() => {
  const stopPerfTimer = startTimer("app_initial_render");

  // Initialize WebSocket connection (only if store is available)
  try {
    const wsStore = useWebSocketStore();
    const wsUrl =
      import.meta.env.VITE_WS_URL ||
      (typeof window !== "undefined" ? window.location.origin : "http://localhost:8000");
    wsStore.connect(wsUrl);
  } catch (error) {
    logWarning("ws_init_failed", { error: error?.message });
  }

  // Setup DevTools integration for diagnostics
  try {
    setupDevToolsIntegration();
  } catch (error) {
    logWarning("diagnostics_devtools_setup_failed", { error: error?.message });
  }

  app.mount("#app");

  const duration = stopPerfTimer();
  logInfo("app_mounted", { durationMs: duration });
});
