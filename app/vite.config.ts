import tailwindcss from '@tailwindcss/vite';
import { defineConfig } from 'vitest/config';

export default defineConfig({
  base: './',
  plugins: [tailwindcss()],
  server: { host: '127.0.0.1', strictPort: true },
  preview: { host: '127.0.0.1', strictPort: true },
  test: { environment: 'node', include: ['src/**/*.test.ts'] },
});
