import { resolve } from 'node:path';

import { defineConfig } from 'vite';
import solidPlugin from 'vite-plugin-solid';

const src = resolve(import.meta.dirname, 'src');

export default defineConfig({
  root: src,
  base: './',
  plugins: [solidPlugin()],
  build: {
    target: 'esnext',
    outDir: resolve(import.meta.dirname, 'dist'),
    emptyOutDir: true,
    rollupOptions: {
      input: {
        bar: resolve(src, 'bar.html'),
        'apple-menu': resolve(src, 'apple-menu.html'),
        spotify: resolve(src, 'spotify.html'),
      },
    },
  },
});
