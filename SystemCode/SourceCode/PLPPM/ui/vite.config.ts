import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
  build: { manifest: true,
  // outDir:'static'
  },
  base: process.env.mode === "dev" ? "/" : "/static/",
  plugins: [react()],
})
