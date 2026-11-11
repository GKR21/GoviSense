import React, { useState, useEffect } from "react"
import {
  AlertCircle,
  AlertTriangle,
  BarChart3,
  Check,
  CheckCircle2,
  LockKeyhole,
  LogIn,
  Mail,
  MapPin,
  Eye,
  EyeOff,
  ShieldCheck,
  Sprout,
  Settings,
  Database,
  Shield,
  User,
  X,
} from "lucide-react"
import { Button } from "../../components/common"
import { loginUser, registerUser, type AuthUser } from "../../api"

export interface LoginScreenProps {
  onLogin: (role: "Officer" | "Admin" | "Farmer", user?: AuthUser) => void
}

export function LoginScreen({ onLogin }: LoginScreenProps) {
  const [role, setRole] = useState<"Officer" | "Admin">("Officer")
  const [mode, setMode] = useState<"signin" | "signup">("signin")
  const [fullName, setFullName] = useState("")
  const [district, setDistrict] = useState("Anuradhapura")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [showPassword, setShowPassword] = useState(false)
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [toastNotification, setToastNotification] = useState<{ title: string; message: string } | null>(null)
  const [hasPasswordError, setHasPasswordError] = useState(false)

  useEffect(() => {
    if (!toastNotification) return
    const timer = setTimeout(() => {
      setToastNotification(null)
    }, 6000)
    return () => clearTimeout(timer)
  }, [toastNotification])

  const handleRoleChange = (selectedRole: "Officer" | "Admin") => {
    setRole(selectedRole)
    setErrorMessage(null)
    setToastNotification(null)
    setHasPasswordError(false)
    if (selectedRole === "Admin" && mode === "signup") {
      setMode("signin")
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setErrorMessage(null)
    setToastNotification(null)
    setHasPasswordError(false)

    if (!email.trim() || !password.trim() || (mode === "signup" && (!fullName.trim() || !confirmPassword.trim()))) {
      const msg = mode === "signup" ? "Complete all required registration fields." : "Please enter your username and password."
      setErrorMessage(msg)
      setToastNotification({ title: "Incomplete Fields", message: msg })
      return
    }
    if (mode === "signup" && role === "Admin") {
      const msg = "System Administrator accounts cannot be created via public sign up. Accounts must be provisioned internally."
      setErrorMessage(msg)
      setToastNotification({ title: "Registration Restricted", message: msg })
      return
    }
    if (mode === "signup" && password !== confirmPassword) {
      const msg = "Passwords do not match."
      setErrorMessage(msg)
      setHasPasswordError(true)
      setToastNotification({ title: "Password Mismatch", message: msg })
      return
    }
    if (mode === "signup" && password.length < 8) {
      const msg = "Password must be at least 8 characters."
      setErrorMessage(msg)
      setHasPasswordError(true)
      setToastNotification({ title: "Password Too Short", message: msg })
      return
    }

    setIsLoading(true)
    try {
      const res = mode === "signup"
        ? await registerUser({ full_name: fullName, role: "officer", district, username: email, password })
        : await loginUser(email, password, role)
      if (res.success && res.user) {
        setHasPasswordError(false)
        setToastNotification(null)
        onLogin(res.user.role, res.user)
      } else {
        const errorText = res.error || "Invalid credentials — please try again."
        const isPasswordIssue = /password|credential|incorrect|invalid|unauthorized|401/i.test(errorText)
        setHasPasswordError(isPasswordIssue)
        setErrorMessage(errorText)
        setToastNotification({
          title: isPasswordIssue ? "Invalid Password / Credentials" : "Authentication Failed",
          message: errorText,
        })
      }
    } catch (err: any) {
      const errorText = err.message || "Failed to connect to authentication service."
      setErrorMessage(errorText)
      setToastNotification({
        title: "Connection Error",
        message: errorText,
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="login-preview">
      {toastNotification && (
        <div className="auth-toast" role="alert" aria-live="assertive">
          <div className="auth-toast__icon">
            <AlertTriangle size={20} />
          </div>
          <div className="auth-toast__body">
            <strong>{toastNotification.title}</strong>
            <span>{toastNotification.message}</span>
          </div>
          <button
            type="button"
            className="auth-toast__close"
            onClick={() => setToastNotification(null)}
            aria-label="Dismiss notification"
          >
            <X size={16} />
          </button>
        </div>
      )}
      <div className="login-story">
        <div className="brand brand--login">
          <div className="brand__mark">
            <img src="/govisense-logo.png" alt="GoviSense logo" />
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

        {role !== "Admin" ? (
          <div className="auth-mode-toggle" role="tablist" aria-label="Authentication mode">
            <button type="button" className={mode === "signin" ? "active" : ""} onClick={() => { setMode("signin"); setErrorMessage(null) }}>Sign In</button>
            <button type="button" className={mode === "signup" ? "active" : ""} onClick={() => { setMode("signup"); setErrorMessage(null) }}>Sign Up / Register</button>
          </div>
        ) : (
          <div className="admin-auth-notice">
            <ShieldCheck size={16} />
            <span>Administrator sign-in only. New administrator accounts cannot be created via public sign up.</span>
          </div>
        )}

        <div className="role-picker">
          {[
            ["Officer", "Agricultural Officer", "Planning & Policy", BarChart3],
            ["Admin", "Administrator", "Data Catalogue & Security", ShieldCheck],
          ]
            .filter(([value]) => mode !== "signup" || value !== "Admin")
            .map(([value, name, detail, Icon]) => (
            <button
              className={role === value ? "active" : ""}
              type="button"
              onClick={() => handleRoleChange(value as "Officer" | "Admin")}
              key={value as string}
            >
              <Icon size={19} /><span><strong>{name as string}</strong><small>{detail as string}</small></span>
              {role === value && <Check size={15} />}
            </button>
          ))}
        </div>

        {errorMessage && (
          <div className="auth-notification" role="alert" aria-live="assertive">
            <AlertCircle size={20} className="auth-notification__icon" />
            <div className="auth-notification__content">
              <strong>{hasPasswordError ? "Invalid Password or Credentials" : "Authentication Notice"}</strong>
              <p>{errorMessage}</p>
            </div>
            <button
              type="button"
              className="auth-notification__close"
              onClick={() => {
                setErrorMessage(null)
                setHasPasswordError(false)
              }}
              aria-label="Dismiss notification"
            >
              <X size={15} />
            </button>
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
          {mode === "signup" && (
            <label className="login-field">
              <span>Full name</span>
              <div className="auth-input-shell">
                <User size={16} aria-hidden="true" />
                <input
                  type="text"
                  required
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="Your full name"
                  autoComplete="name"
                />
              </div>
            </label>
          )}
          {mode === "signup" && (
            <label className="login-field">
              <span>District</span>
              <div className="auth-input-shell auth-select-shell">
                <MapPin size={16} aria-hidden="true" />
                <select
                  value={district}
                  onChange={(e) => setDistrict(e.target.value)}
                  aria-label="Select district"
                  className="district-select"
                >
                  <option value="Anuradhapura">Anuradhapura</option>
                  <option value="Polonnaruwa">Polonnaruwa</option>
                  <option value="Kurunegala">Kurunegala</option>
                  <option value="Matale">Matale</option>
                  <option value="Hambantota">Hambantota</option>
                  <option value="Jaffna">Jaffna</option>
                </select>
              </div>
            </label>
          )}
          <label className="login-field">
            <span>Email / username</span>
            <div className="auth-input-shell">
              <Mail size={16} aria-hidden="true" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => {
                  setEmail(e.target.value)
                  if (errorMessage) setErrorMessage(null)
                  if (hasPasswordError) setHasPasswordError(false)
                }}
                placeholder="name@agriculture.gov.lk"
                autoComplete="email"
              />
            </div>
          </label>

          <label className="login-field">
            <span>Password</span>
            <div className={`auth-input-shell auth-password-shell ${hasPasswordError ? "auth-input-shell--error" : ""}`}>
              <LockKeyhole size={16} aria-hidden="true" />
              <input
                type={showPassword ? "text" : "password"}
                required
                value={password}
                onChange={(e) => {
                  setPassword(e.target.value)
                  if (hasPasswordError) setHasPasswordError(false)
                  if (errorMessage) setErrorMessage(null)
                }}
                placeholder={mode === "signup" ? "At least 8 characters" : "Enter password"}
                autoComplete="current-password"
                aria-invalid={hasPasswordError}
              />
              <button type="button" className="password-toggle" aria-label={showPassword ? "Hide password" : "Show password"} onClick={() => setShowPassword((value) => !value)}>{showPassword ? <EyeOff size={16} /> : <Eye size={16} />}</button>
            </div>
            {hasPasswordError && (
              <span className="auth-field-error-hint">
                <AlertCircle size={12} />
                <span>Incorrect password. Please verify your password.</span>
              </span>
            )}
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

        {role !== "Admin" && (
          <button type="button" className="auth-inline-toggle" onClick={() => { setMode(mode === "signin" ? "signup" : "signin"); setErrorMessage(null) }}>
            {mode === "signin" ? "New to GoviSense? Create an account" : "Already have an account? Sign in"}
          </button>
        )}
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
