import React, { useState } from "react"
import {
  BarChart3,
  Check,
  LockKeyhole,
  LogIn,
  Settings,
  ShieldCheck,
  Sprout,
} from "lucide-react"
import { Button } from "../../components/common"

export function LoginScreen({ onLogin }: { onLogin: (role: "Officer" | "Admin" | "Farmer") => void }) {
  const [role, setRole] = useState<"Officer" | "Admin" | "Farmer">("Officer")
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
            <small>Every output includes confidence and data versions.</small>
          </span>
        </div>
      </div>
      <div className="login-form-card">
        <span className="login-icon">
          <LogIn size={22} />
        </span>
        <h2>Welcome back</h2>
        <p>Choose your role and continue to the demo workspace.</p>
        <div className="role-picker">
          {[
            ["Officer", BarChart3],
            ["Admin", Settings],
            ["Farmer", Sprout],
          ].map(([name, Icon]) => (
            <button
              className={role === name ? "active" : ""}
              type="button"
              onClick={() => setRole(name as "Officer" | "Admin" | "Farmer")}
              key={name as string}
            >
              <Icon size={19} />
              <span>{name as string}</span>
              {role === name && <Check size={15} />}
            </button>
          ))}
        </div>
        <label className="login-field">
          <span>Email address</span>
          <input
            key={role}
            defaultValue={
              role === "Admin"
                ? "admin@govisense.lk"
                : role === "Farmer"
                ? "sunil@farmer.govisense.lk"
                : "nimal@agriculture.gov.lk"
            }
          />
        </label>
        <label className="login-field">
          <span>Password</span>
          <div>
            <LockKeyhole size={16} />
            <input type="password" defaultValue="prototype" />
          </div>
        </label>
        <Button icon={LogIn} onClick={() => onLogin(role)}>
          Continue as {role}
        </Button>
        <small>Demo only · No real credentials required</small>
      </div>
    </div>
  )
}

