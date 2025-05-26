import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          // Separate vendor libraries
          vendor: ['vue', 'vue-router'],
          supabase: ['@supabase/supabase-js'],
          ui: ['radix-vue', 'lucide-vue-next'],
          socket: ['socket.io-client']
        }
      }
    },
    chunkSizeWarningLimit: 600 // Adjust if needed
  },
  server: {
    proxy: {
      '/socket.io': {
        target: 'http://localhost:5001',
        ws: true,
        changeOrigin: true
      },
      '/api': {
        target: 'http://localhost:5001',
        changeOrigin: true
      }
    }
  }
})