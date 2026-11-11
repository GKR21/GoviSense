import React from "react"
import ReactDOM from "react-dom/client"
import App from "./App"
import "./index.css"

class RootErrorBoundary extends React.Component<
  { children: React.ReactNode },
  { error: Error | null }
> {
  constructor(props: { children: React.ReactNode }) {
    super(props)
    this.state = { error: null }
  }

  static getDerivedStateFromError(error: Error) {
    return { error }
  }

  render() {
    if (this.state.error) {
      return (
        <div
          style={{
            minHeight: "100vh",
            display: "grid",
            placeItems: "center",
            padding: "24px",
            background: "#0c1422",
            color: "#f0fdf8",
            fontFamily: "Inter, system-ui, sans-serif",
          }}
        >
          <div style={{ maxWidth: 480, textAlign: "center" }}>
            <h1 style={{ fontSize: "1.25rem", marginBottom: "8px" }}>
              GoviSense failed to load
            </h1>
            <p style={{ color: "#94a3b8", fontSize: "0.9rem", marginBottom: "16px" }}>
              {this.state.error.message}
            </p>
            <button
              type="button"
              onClick={() => window.location.reload()}
              style={{
                padding: "8px 16px",
                borderRadius: "8px",
                background: "#10b981",
                color: "#07130d",
                fontWeight: 600,
                border: "none",
                cursor: "pointer",
              }}
            >
              Reload page
            </button>
          </div>
        </div>
      )
    }
    return this.props.children
  }
}

if ("serviceWorker" in navigator && import.meta.env.MODE !== "test") {
  window.addEventListener("load", () => {
    navigator.serviceWorker
      .register("/sw.js")
      .then((reg) => {
        console.log("[GoviSense] Service Worker registered with scope:", reg.scope)
        reg.update().catch(() => { })
      })
      .catch((err) => {
        console.warn("[GoviSense] Service Worker registration failed:", err)
      })
  })
}

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <RootErrorBoundary>
      <App />
    </RootErrorBoundary>
  </React.StrictMode>,
)
