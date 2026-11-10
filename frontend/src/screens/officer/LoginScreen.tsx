import React, { useState } from "react"
import {
  AlertCircle,
  BarChart3,
  Check,
  CheckCircle2,
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

export function LoginScreen({ onLogin }: LoginScreenProps) {
  const [role, setRole] = useState<"Officer" | "Admin" | "Farmer">("Officer")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  const handleRoleChange = (selectedRole: "Officer" | "Admin" | "Farmer") => {
    setRole(selectedRole)
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

        </div>
      </div>
    </div>
  )
}
