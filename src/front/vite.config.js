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
      '/events': 'http://127.0.0.1:5000',
      '/listings': 'http://127.0.0.1:5000',
      '/me': 'http://127.0.0.1:5000',
      '/auth': 'http://127.0.0.1:5000',
    }
  }
})
