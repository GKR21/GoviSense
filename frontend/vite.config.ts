import { defineConfig } from "vite"
import react from "@vitejs/plugin-react"
import tailwindcss from "@tailwindcss/vite"
import path from "node:path"

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      "@": path.resolve(import.meta.dirname, "./src"),
    },
  },
  server: {
    host: "0.0.0.0",
    port: Number(process.env.PORT || 8443),
    strictPort: true,
    proxy: {
      "/api": {
        target: process.env.GOVISENSE_BACKEND_URL || "https://govisense-production.up.railway.app",
        changeOrigin: true,
      },
    },
  },
  preview: {
    host: "0.0.0.0",
    port: Number(process.env.PORT || 8443),
    strictPort: true,
    proxy: {
      "/api": {
        target: process.env.GOVISENSE_BACKEND_URL || "https://govisense-production.up.railway.app",
        changeOrigin: true,
      },
    },
  },
})
