import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000, // <--- Ganti ke port 3000 (atau port lain selain 8000)
    strictPort: true, // Memaksa Vite error jika port 3000 ternyata dipakai, tidak asal lompat port
  }
})