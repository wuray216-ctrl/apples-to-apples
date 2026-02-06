import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: '/apples-to-apples/', // Change this to your repo name
  build: {
    outDir: 'dist',
  },
})
