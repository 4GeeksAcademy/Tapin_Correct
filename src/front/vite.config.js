import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
      },
      '/events': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
      },
      '/listings': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
      },
      '/me': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
      },
      '/register': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
      },
      '/login': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
      },
      '/refresh': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
      },
      '/reset-password': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
      },
    }
  }
})
