import react from '@vitejs/plugin-react';
import { defineConfig } from 'vite';

// In development the API and uploaded media are proxied to Django, so the
// app always talks to relative /api and /media URLs.
const apiTarget = process.env.VITE_PROXY_TARGET || 'http://localhost:8000';

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': apiTarget,
      '/media': apiTarget,
    },
  },
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.js'],
  },
});
