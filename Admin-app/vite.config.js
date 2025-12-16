import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  base: "/admin/",
  server: {
    port: 3001,
  },
  build: {
    // Production build optimizations
    target: 'es2015',
    minify: 'esbuild', // Use esbuild instead of terser (faster and included)
    rollupOptions: {
      output: {
        manualChunks: {
          'vue-vendor': ['vue', 'vue-router', 'pinia'],
          'ui-vendor': ['@fortawesome/fontawesome-free'],
        },
      },
    },
    chunkSizeWarningLimit: 1000,
    assetsDir: 'assets',
    sourcemap: false, // Disable sourcemaps in production for smaller builds
  },
});
