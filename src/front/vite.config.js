import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
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
