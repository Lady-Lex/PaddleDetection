import { fileURLToPath, URL } from 'node:url';

import vue from '@vitejs/plugin-vue';
import { defineConfig } from 'vite';

import mkcert from "vite-plugin-mkcert";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),

    mkcert(),
  ],
  server: {
    https: true,
  },

  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  }
})
