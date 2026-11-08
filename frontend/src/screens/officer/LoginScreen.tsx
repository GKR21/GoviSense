import React, { useState } from "react"
import {
  AlertCircle,
  BarChart3,
  Check,
  CheckCircle2,
  Info,
  LockKeyhole,
  LogIn,
  Mail,
  Settings,
  ShieldCheck,
  Sprout,
} from "lucide-react"
import { Button } from "../../components/common"
import { loginUser, type AuthUser } from "../../api"

export interface LoginScreenProps {
  onLogin: (role: "Officer" | "Admin" | "Farmer", user?: AuthUser) => void
}

const DEFAULT_CREDENTIALS: Record<"Officer" | "Admin" | "Farmer", { email: string; pass: string }> = {
  Officer: { email: "nimal@agriculture.gov.lk", pass: "officer123" },
  Admin: { email: "admin@govisense.lk", pass: "admin123" },
  Farmer: { email: "sunil@farmer.govisense.lk", pass: "farmer123" },
}

export function LoginScreen({ onLogin }: LoginScreenProps) {
  const [role, setRole] = useState<"Officer" | "Admin" | "Farmer">("Officer")
  const [email, setEmail] = useState("nimal@agriculture.gov.lk")
  const [password, setPassword] = useState("officer123")
  const [isLoading, setIsLoading] = useState(false)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [showCredsHint, setShowCredsHint] = useState(false)

  const handleRoleChange = (selectedRole: "Officer" | "Admin" | "Farmer") => {
    setRole(selectedRole)
    const defaults = DEFAULT_CREDENTIALS[selectedRole]
    setEmail(defaults.email)
    setPassword(defaults.pass)
    setErrorMessage(null)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setErrorMessage(null)

    if (!email.trim() || !password.trim()) {
      setErrorMessage("Please enter both email address and password.")
      return
    }

    setIsLoading(true)
    try {
      const res = await loginUser(email, password, role)
      if (res.success && res.user) {
        onLogin(res.user.role, res.user)
      } else {
        setErrorMessage(res.error || "Invalid credentials — please try again.")
      }
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to connect to authentication service.")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="login-preview">
      <div className="login-story">
        <div className="brand brand--login">
          <div className="brand__mark">
            <Sprout size={23} />
          </div>
          <div>
            <strong>GoviSense</strong>
            <span>Agricultural decision support</span>
          </div>
        </div>
        <div>
          <span className="eyebrow">SRI LANKA · PILOT WORKSPACE</span>
          <h1>Decisions grounded in supply, demand and uncertainty.</h1>
          <p>
            A shared monthly picture for agricultural planning officers and
            farming communities.
          </p>
        </div>
        <div className="login-proof">
          <ShieldCheck size={18} />
          <span>
            <strong>Traceable by design</strong>
            <small>Every output includes confidence, authentication, and data versions.</small>
          </span>
        </div>
      </div>

      <div className="login-form-card">
        <span className="login-icon">
          <LogIn size={22} />
        </span>
        <h2>Welcome back</h2>
        <p>Sign in with your official Department of Agriculture credentials.</p>

        <div className="role-picker">
          {[
            ["Officer", BarChart3],
            ["Admin", Settings],
            ["Farmer", Sprout],
          ].map(([name, Icon]) => (
            <button
              className={role === name ? "active" : ""}
              type="button"
              onClick={() => handleRoleChange(name as "Officer" | "Admin" | "Farmer")}
              key={name as string}
            >
              <Icon size={19} />
              <span>{name as string}</span>
              {role === name && <Check size={15} />}
            </button>
          ))}
        </div>

        {errorMessage && (
          <div
            className="alert-banner alert-banner--warning"
            style={{
              padding: "10px 14px",
              marginBottom: "14px",
              fontSize: "12px",
              display: "flex",
              alignItems: "center",
              gap: "8px",
            }}
          >
            <AlertCircle size={16} />
            <span>{errorMessage}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
          <label className="login-field">
            <span>Email address</span>
            <div style={{ position: "relative", display: "flex", alignItems: "center" }}>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="name@agriculture.gov.lk"
                autoComplete="email"
              />
            </div>
          </label>

          <label className="login-field">
            <span>Password</span>
            <div>
              <LockKeyhole size={16} />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter password"
                autoComplete="current-password"
              />
            </div>
          </label>

          <Button
            type="submit"
            icon={LogIn}
            disabled={isLoading}
          >
            {isLoading ? "Authenticating..." : `Sign in as ${role}`}
          </Button>
        </form>

        <div style={{ marginTop: "14px", display: "flex", flexDirection: "column", gap: "6px", alignItems: "center" }}>
          <small style={{ color: "var(--ink-muted)", fontSize: "11px", display: "flex", alignItems: "center", gap: "5px" }}>
            <ShieldCheck size={13} color="var(--primary)" />
            Government RBAC & JWT Session Security
          </small>

          <button
            type="button"
            onClick={() => setShowCredsHint(!showCredsHint)}
            style={{
              background: "none",
              border: "none",
              color: "var(--primary)",
              fontSize: "11px",
              cursor: "pointer",
              display: "inline-flex",
              alignItems: "center",
              gap: "4px",
              padding: 0,
            }}
          >
            <Info size={12} />
            {showCredsHint ? "Hide test credentials" : "Show test credentials"}
          </button>

          {showCredsHint && (
            <div
              style={{
                marginTop: "4px",
                padding: "8px 12px",
                borderRadius: "6px",
                background: "rgba(0,0,0,0.25)",
                border: "1px solid var(--border)",
                fontSize: "11px",
                color: "var(--ink-muted)",
                textAlign: "left",
                width: "100%",
                lineHeight: 1.5,
              }}
            >
              <div><strong>Officer:</strong> nimal@agriculture.gov.lk / officer123</div>
              <div><strong>Admin:</strong> admin@govisense.lk / admin123</div>
              <div><strong>Farmer:</strong> sunil@farmer.govisense.lk / farmer123</div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
