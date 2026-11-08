import React, { useState } from "react"
import {
  Check,
  Languages,
  Moon,
  Save,
  Settings,
  Sun,
} from "lucide-react"
import { Button, PageHeading, SliderField, RiskBadge, SelectControl } from "../../components/common"

export function SettingsScreen() {
  const [lang, setLang] = useState("English")
  const [defaultDistrict, setDefaultDistrict] = useState("Anuradhapura")
  return (
    <>
      <PageHeading
        eyebrow="Workspace controls"
        icon={Settings}
        title="Settings & assumptions"
        description="Set organisation defaults for risk bands, lead times, losses and access."
        actions={<Button icon={Save}>Save changes</Button>}
      />
      <div className="settings-layout">
        <section className="panel settings-card">
          <div className="panel-heading">
            <div>
              <h2>Supply pressure bands</h2>
              <p>Applied to every crop and month.</p>
            </div>
          </div>
          <div className="settings-fields">
            <label>
              <span>Shortage below</span>
              <input defaultValue="0.80" />
            </label>
            <label>
              <span>Balanced upper limit</span>
              <input defaultValue="1.20" />
            </label>
          </div>
          <div className="band-preview">
            <RiskBadge risk="shortage" />
            <RiskBadge risk="balanced" />
            <RiskBadge risk="oversupply" />
          </div>
        </section>
        <section className="panel settings-card">
          <div className="panel-heading">
            <div>
              <h2>Operational assumptions</h2>
              <p>Defaults remain editable per scenario.</p>
            </div>
          </div>
          <div className="settings-fields">
            <label>
              <span>Import lead time</span>
              <div>
                <input defaultValue="7" />
                <small>weeks</small>
              </div>
            </label>
            <label>
              <span>Post-harvest loss</span>
              <div>
                <input defaultValue="12" />
                <small>%</small>
              </div>
            </label>
          </div>
        </section>
        <section className="panel settings-card">
          <div className="panel-heading">
            <div>
              <h2>Language & region</h2>
              <p>Officer workspace defaults.</p>
            </div>
          </div>
          <SelectControl
            label="Interface language"
            value={lang}
            options={["English", "Sinhala (සිංහල)", "Tamil (தமிழ்)"]}
            onChange={setLang}
          />
          <SelectControl
            label="Default district"
            value={defaultDistrict}
            options={["Anuradhapura", "Polonnaruwa", "Kurunegala", "Matale", "Hambantota", "Jaffna"]}
            onChange={setDefaultDistrict}
          />
        </section>
        <section className="panel settings-card">
          <div className="panel-heading">
            <div>
              <h2>Roles & access</h2>
              <p>Three active roles in this workspace.</p>
            </div>
          </div>
          {[
            ["Officer", "Model outputs and decisions"],
            ["Admin", "Sources, roles and settings"],
            ["Farmer", "Own advice and reports"],
          ].map(([role, detail]) => (
            <div className="role-row" key={role}>
              <span>
                <strong>{role}</strong>
                <small>{detail}</small>
              </span>
              <Button variant="ghost">Manage</Button>
            </div>
          ))}
        </section>
      </div>
    </>
  )
}

