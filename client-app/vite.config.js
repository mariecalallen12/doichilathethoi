import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import { VitePWA } from "vite-plugin-pwa";

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    // Only enable PWA in dev mode to avoid lightweight-charts build issues
    // TODO: Fix lightweight-charts compatibility with vite-plugin-pwa
    ...(process.env.NODE_ENV !== 'production' ? [VitePWA({
      registerType: "autoUpdate",
      scope: "/",
      // Don't register service worker on admin paths
      injectRegister: "inline",
      workbox: {
        navigateFallback: "/",
        navigateFallbackDenylist: [/^\/admin/, /^\/api/], // Don't cache admin paths and API
        runtimeCaching: [
          {
            urlPattern: /^https:\/\/cmeetrading\.com\/admin\/.*/i,
            handler: "NetworkOnly", // Always fetch from network for admin paths
          },
          {
            // Don't cache registration fields config API - always fetch from network
            urlPattern: /\/api\/client\/settings\/registration-fields/i,
            handler: "NetworkOnly",
          },
          {
            // Don't cache API calls - always use network
            urlPattern: /\/api\/.*/i,
            handler: "NetworkFirst",
            options: {
              cacheName: "api-cache",
              networkTimeoutSeconds: 10,
              cacheableResponse: {
                statuses: [0, 200],
              },
            },
          },
        ],
        // Skip waiting to ensure latest service worker is used
        skipWaiting: true,
        clientsClaim: true,
      },
      manifest: {
        name: "LuxeTrade",
        short_name: "LuxeTrade",
        theme_color: "#0b0b15",
        background_color: "#0b0b15",
        display: "standalone",
        start_url: "/",
        icons: [
          { src: "/vite.svg", sizes: "192x192", type: "image/svg+xml" },
          { src: "/vite.svg", sizes: "512x512", type: "image/svg+xml" },
        ],
      },
    })] : []),
  ],
  // Explicit base path for root deployment
  base: "/",
  server: {
    port: 3002,
  },
  build: {
    // Ensure assets are referenced correctly
    assetsDir: "assets",
    // Source maps disabled for production
    sourcemap: false,
    // Code splitting optimization
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor-vue': ['vue', 'vue-router', 'pinia'],
          'vendor-charts': ['echarts'],
          'vendor-utils': ['axios', 'lodash-es', 'date-fns'],
          'vendor-ui': ['swiper', '@fullcalendar/vue3', 'plyr', 'pdfjs-dist'],
        },
      },
      // Externalize virtual PWA module when PWA plugin is disabled
      external: (id) => {
        // When PWA is disabled in production, externalize the virtual module
        if (process.env.NODE_ENV === 'production' && id === 'virtual:pwa-register') {
          return true;
        }
        return false;
      },
    },
    // Chunk size warning limit
    chunkSizeWarningLimit: 1000,
    // CommonJS options for better compatibility
    commonjsOptions: {
      transformMixedEsModules: true,
      // Exclude lightweight-charts from commonjs processing - it's already ESM
      exclude: [/lightweight-charts/],
      // Include AOS and other CommonJS packages
      include: [/aos/, /node_modules/],
    },
  },
  // Optimize dependencies
  optimizeDeps: {
    exclude: ['lightweight-charts'],
  },
  // Resolve options
  resolve: {
    alias: {
      // Use the main entry point for lightweight-charts
      'lightweight-charts': 'lightweight-charts',
    },
    // Dedupe to avoid multiple versions
    dedupe: ['lightweight-charts'],
    // Conditions for package exports resolution
    // Include default and other common conditions for better compatibility
    conditions: ['production', 'import', 'default', 'module', 'browser'],
  },
  // SSR options - disable SSR for lightweight-charts
  ssr: {
    noExternal: [],
    external: ['lightweight-charts'],
  },
});
