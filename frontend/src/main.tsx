import React from "react"
import ReactDOM from "react-dom/client"
import App from "./App"
import "./index.css"

if ("serviceWorker" in navigator && process.env.NODE_ENV !== "test") {
  window.addEventListener("load", () => {
    navigator.serviceWorker
      .register("/sw.js")
      .then((reg) => {
        console.log("[GoviSense] Service Worker registered with scope:", reg.scope)
      })
      .catch((err) => {
        console.warn("[GoviSense] Service Worker registration failed:", err)
      })
  })
}

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
