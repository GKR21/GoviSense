import { defineConfig } from "vite"
import react from "@vitejs/plugin-react"
import tailwindcss from "@tailwindcss/vite"
import { fileURLToPath } from "node:url"
import net from "node:net"

const remoteBackend = "https://govisense-production.up.railway.app"
const localBackend = "http://127.0.0.1:8000"
const explicitBackend = process.env.GOVISENSE_BACKEND_URL

let isLocalBackendAlive = false

function probeLocalBackend() {
  const socket = new net.Socket()
  socket.setTimeout(250)
  socket.on("connect", () => {
    isLocalBackendAlive = true
    socket.destroy()
  })
  socket.on("timeout", () => {
    isLocalBackendAlive = false
    socket.destroy()
  })
  socket.on("error", () => {
    isLocalBackendAlive = false
    socket.destroy()
  })
  socket.connect(8000, "127.0.0.1")
}

probeLocalBackend()
const probeTimer = setInterval(probeLocalBackend, 2500)
if (probeTimer.unref) probeTimer.unref()

function resolveTarget(): string {
  if (explicitBackend) return explicitBackend
  return isLocalBackendAlive ? localBackend : remoteBackend
}

const proxyConfig = {
  target: explicitBackend || remoteBackend,
  changeOrigin: true,
  secure: false,
  router: () => resolveTarget(),
  configure: (proxy: any) => {
    proxy.on("error", (err: Error, req: any, res: any) => {
      if (res && !res.headersSent && typeof res.writeHead === "function") {
        res.writeHead(502, { "Content-Type": "application/json" })
        res.end(JSON.stringify({ error: "Backend proxy gateway error", message: err.message }))
      }
    })
  },
}

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
  server: {
    host: "127.0.0.1",
    port: Number(process.env.PORT || 3000),
    strictPort: false,
    proxy: {
      "/api": proxyConfig,
    },
  },
  preview: {
    host: "127.0.0.1",
    port: Number(process.env.PORT || 3000),
    strictPort: false,
    proxy: {
      "/api": proxyConfig,
    },
  },
})
