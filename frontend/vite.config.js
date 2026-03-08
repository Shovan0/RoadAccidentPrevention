import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [
    react({ include: /\.(jsx|js|tsx|ts)$/ }),
  ],
  esbuild: {
    loader: 'jsx',
    include: /src\/.*\.js$/,
    exclude: [],
  },
  optimizeDeps: {
    esbuildOptions: {
      loader: { '.js': 'jsx' },
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
      },
      '/video_feed': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
      },
      '/download': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
      },
    },
  },
})
