import React, { useState } from "react"
import {
  AlertCircle,
  BarChart3,
  Check,
  CheckCircle2,
  LockKeyhole,
  LogIn,
  Mail,
  Eye,
  EyeOff,
  ShieldCheck,
  Settings,
  Sprout,
  Database,
  Shield,
} from "lucide-react"
import { Button } from "../../components/common"
import { loginUser, registerUser, type AuthUser } from "../../api"

export interface LoginScreenProps {
  onLogin: (role: "Officer" | "Admin" | "Farmer", user?: AuthUser) => void
}

export function LoginScreen({ onLogin }: LoginScreenProps) {
  const [role, setRole] = useState<"Officer" | "Admin" | "Farmer">("Officer")
  const [mode, setMode] = useState<"signin" | "signup">("signin")
  const [fullName, setFullName] = useState("")
  const [district, setDistrict] = useState("Anuradhapura")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [showPassword, setShowPassword] = useState(false)
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

    if (!email.trim() || !password.trim() || (mode === "signup" && (!fullName.trim() || !confirmPassword.trim()))) {
      setErrorMessage(mode === "signup" ? "Complete all required registration fields." : "Please enter your username and password.")
      return
    }
    if (mode === "signup" && role === "Admin") { setErrorMessage("System Administrator accounts must be provisioned by an administrator."); return }
    if (mode === "signup" && password !== confirmPassword) { setErrorMessage("Passwords do not match."); return }
    if (mode === "signup" && password.length < 8) { setErrorMessage("Password must be at least 8 characters."); return }

    setIsLoading(true)
    try {
      const res = mode === "signup"
        ? await registerUser({ full_name: fullName, role: role.toLowerCase() as "officer" | "farmer", district, username: email, password })
        : await loginUser(email, password, role)
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
          <h1>Decisions Grounded in Supply, Demand &amp; Uncertainty</h1>
          <p>
            A shared monthly picture for agricultural planning officers and
            farming communities.
          </p>
        </div>
        <ul className="login-features">
          <li><Database size={16} /><span>Empirical CBSL &amp; DOA Price Telemetry</span></li>
          <li><BarChart3 size={16} /><span>80% Quantile Harvest Prediction Bands</span></li>
          <li><Shield size={16} /><span>Cryptographic SHA-256 Decision Ledger</span></li>
        </ul>
        <div className="login-proof">
          <ShieldCheck size={18} />
          <span>
            <strong>Traceable by Design</strong>
            <small>Every output includes confidence, authentication, and data versions.</small>
          </span>
        </div>
      </div>

      <div className="login-form-card">
        <span className="login-icon">
          <LogIn size={22} />
        </span>
        <h2>{mode === "signin" ? "Welcome back" : "Create your account"}</h2>
        <p>{mode === "signin" ? "Sign in to your GoviSense workspace." : "Register for your role-based GoviSense workspace."}</p>

        <div className="auth-mode-toggle" role="tablist" aria-label="Authentication mode">
          <button type="button" className={mode === "signin" ? "active" : ""} onClick={() => { setMode("signin"); setErrorMessage(null) }}>Sign In</button>
          <button type="button" className={mode === "signup" ? "active" : ""} onClick={() => { setMode("signup"); setErrorMessage(null) }}>Sign Up / Register</button>
        </div>

        <div className="role-picker">
          {[
            ["Officer", "Agricultural Officer", "Planning & Policy", BarChart3],
            ["Farmer", "Registered Farmer", "Advisory & Declarations", Sprout],
            ["Admin", "Administrator", "Data Catalogue & Security", ShieldCheck],
          ].map(([value, name, detail, Icon]) => (
            <button
              className={role === value ? "active" : ""}
              type="button"
              onClick={() => handleRoleChange(value as "Officer" | "Admin" | "Farmer")}
              key={value as string}
            >
              <Icon size={19} /><span><strong>{name as string}</strong><small>{detail as string}</small></span>
              {role === value && <Check size={15} />}
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
          {mode === "signup" && <label className="login-field"><span>Full name</span><input type="text" required value={fullName} onChange={(e) => setFullName(e.target.value)} placeholder="Your full name" /></label>}
          {mode === "signup" && <label className="login-field"><span>District</span><select value={district} onChange={(e) => setDistrict(e.target.value)}><option>Anuradhapura</option><option>Polonnaruwa</option><option>Kurunegala</option><option>Matale</option><option>Hambantota</option><option>Jaffna</option></select></label>}
          <label className="login-field">
            <span>Email / username</span>
            <div style={{ position: "relative", display: "flex", alignItems: "center" }}>
              <Mail size={16} />
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
                type={showPassword ? "text" : "password"}
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder={mode === "signup" ? "At least 8 characters" : "Enter password"}
                autoComplete="current-password"
              />
              <button type="button" className="password-toggle" aria-label={showPassword ? "Hide password" : "Show password"} onClick={() => setShowPassword((value) => !value)}>{showPassword ? <EyeOff size={16} /> : <Eye size={16} />}</button>
            </div>
          </label>
          {mode === "signup" && <label className="login-field"><span>Confirm password</span><input type="password" required value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} placeholder="Re-enter password" /></label>}

          <Button
            type="submit"
            icon={LogIn}
            disabled={isLoading}
          >
            {isLoading ? (mode === "signin" ? "Signing in..." : "Creating account...") : (mode === "signin" ? `Sign in as ${role}` : `Create ${role} account`)}
          </Button>
        </form>

        <button type="button" className="auth-inline-toggle" onClick={() => { setMode(mode === "signin" ? "signup" : "signin"); setErrorMessage(null) }}>
          {mode === "signin" ? "New to GoviSense? Create an account" : "Already have an account? Sign in"}
        </button>
        <div className="auth-security-note">
          <small style={{ color: "var(--ink-muted)", fontSize: "11px", display: "flex", alignItems: "center", gap: "5px" }}>
            <ShieldCheck size={13} color="var(--primary)" />
            Secured with Government RBAC &amp; HS256 JWT encryption
          </small>
        </div>
      </div>
    </div>
  )
}
