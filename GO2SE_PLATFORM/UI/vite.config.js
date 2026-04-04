import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@integration': path.resolve(__dirname, '../integration'),
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8004',
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://localhost:8004',
        ws: true,
      },
    },
  },
})
