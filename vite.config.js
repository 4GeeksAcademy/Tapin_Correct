import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [react()],
    root: 'src/front',
    publicDir: 'src/front/src/assets',
    server: {
        port: 3000
    },
    build: {
        outDir: '../dist',
        emptyOutDir: true,
    },
    resolve: {
        alias: {
            '@': path.resolve(__dirname, 'src/front/src')
        }
    },
    test: {
        environment: 'jsdom',
        setupFiles: path.resolve(__dirname, 'src/front/src/test/setup.js'),
        globals: true
    }
})
