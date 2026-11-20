/// <reference types="vitest" />
import { defineConfig, type ProxyOptions } from 'vite';
import react from '@vitejs/plugin-react';

// The live inference API (FastAPI, `make api`) is optional; the page falls back to the static export.
const apiPort = process.env.SIGHTGLASS_API_PORT || '8000';
const api: ProxyOptions = {
  target: `http://127.0.0.1:${apiPort}`,
  changeOrigin: true,
  configure(proxy) {
    proxy.on('error', (_err, _req, res) => {
      const r = res as import('node:http').ServerResponse;
      if (!r.headersSent && typeof r.writeHead === 'function') {
        r.writeHead(502, { 'Content-Type': 'application/json' });
        r.end(JSON.stringify({ error: `The live API is not running on port ${apiPort}. Start it with "make api".` }));
      }
    });
  },
};

export default defineConfig({
  plugins: [react()],
  base: './',
  build: { outDir: 'dist', emptyOutDir: true, target: 'es2020', assetsInlineLimit: 0 },
  server: { port: 5173, proxy: { '/api': api } },
  preview: { port: 4173, proxy: { '/api': api } },
  test: { globals: true, environment: 'jsdom', setupFiles: './src/test/setup.ts', css: false },
});
