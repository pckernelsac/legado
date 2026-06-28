import path from "node:path";

import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    host: true,
    port: 5173,
    // Bind mounts en Docker (Windows/WSL) no propagan eventos inotify; sin
    // polling el HMR no detecta los cambios de archivos.
    watch: { usePolling: true, interval: 300 },
  },
  build: {
    target: "es2022",
    sourcemap: false,
    rollupOptions: {
      output: {
        manualChunks: {
          react: ["react", "react-dom", "react-router-dom"],
          query: ["@tanstack/react-query", "axios"],
          motion: ["framer-motion"],
          map: ["leaflet", "react-leaflet"],
        },
      },
    },
  },
});
