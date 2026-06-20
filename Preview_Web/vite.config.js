import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  // 'base' ini wajib agar aplikasi Anda tidak error saat dibuka di GitHub Pages
  base: './', 
  server: {
    port: 8000,
  },
})