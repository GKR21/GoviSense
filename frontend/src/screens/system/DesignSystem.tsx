import React, { useState } from "react"
import {
  AlertCircle,
  BookOpen,
  CheckCircle2,
  Database,
  Eye,
  Plus,
  ShieldCheck,
  Sprout,
  TriangleAlert,
} from "lucide-react"
import type { View } from "../../types"
import { Button, DemoRibbon, StateCard, WorkspaceSwitcher } from "../../components/common"
import { SupplyChart } from "../../components/charts"

export function DesignSystem({
  view = "system",
  setView,
}: {
  view?: View
  setView?: (view: View) => void
}) {
  const [tab, setTab] = useState("Overview")
  const [toggle, setToggle] = useState(true)
  return (
    <div className="system-page">
      <DemoRibbon />
      <aside className="system-aside">
        <div className="brand">
          <div className="brand__mark">
            <Sprout size={23} />
          </div>
          <div>
            <strong>GoviSense</strong>
            <span>Component library · 1.0</span>
          </div>
        </div>
        <div className="system-index">
          <span>FOUNDATIONS</span>
          <a href="#foundations">Colour & type</a>
          <a href="#spacing">Spacing & elevation</a>
          <span>COMPONENTS</span>
          <a href="#actions">Actions & inputs</a>
          <a href="#signals">Risk & confidence</a>
          <a href="#states">System states</a>
          <a href="#data">Data visualisation</a>
        </div>
        <div className="a11y-card">
          <Eye size={18} />
          <div>
            <strong>WCAG AA</strong>
            <span>Colour + icon + text</span>
          </div>
        </div>
      </aside>
      <main className="system-main">
        <header className="system-header">
          <div>
            <span>GOVISENSE / FOUNDATIONS</span>
            <h1>Product design system</h1>
            <p>
              Calm, precise and traceable interfaces for agricultural decisions.
            </p>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            {setView && <WorkspaceSwitcher view={view} setView={setView} compact={true} />}
            <Button variant="secondary" icon={BookOpen}>
              Usage guide
            </Button>
          </div>
        </header>

        <section className="system-section" id="foundations">
          <div className="section-label">
            <span>01</span>
            <div>
              <h2>Foundations</h2>
              <p>
                Semantic tokens support light mode today and dark mode later.
              </p>
            </div>
          </div>
          <div className="system-card">
            <div className="system-card__head">
              <div>
                <h3>Colour tokens</h3>
                <p>Named by role, never by visual appearance.</p>
              </div>
              <span className="code-label">tokens.color.*</span>
            </div>
            <div className="swatch-grid">
              {[
                ["Primary", "#1B7F4B", "primary"],
                ["Primary dark", "#0F4D2E", "primary-dark"],
                ["Primary tint", "#E8F5EE", "primary-tint"],
                ["Ink", "#14211B", "ink"],
                ["Neutral 600", "#4A5A52", "neutral"],
                ["Background", "#F6F8F7", "background"],
                ["Shortage", "#D64545", "shortage"],
                ["Balanced", "#2E9E5B", "balanced"],
                ["Oversupply", "#E8A317", "oversupply"],
                ["Information", "#2F6FDE", "info"],
              ].map(([name, hex, token]) => (
                <div className="swatch" key={name}>
                  <i className={`swatch__colour swatch__colour--${token}`} />
                  <span>
                    <strong>{name}</strong>
                    <small>{hex}</small>
                  </span>
                </div>
              ))}
            </div>
          </div>
          <div className="foundation-grid">
            <div className="system-card">
              <div className="system-card__head">
                <div>
                  <h3>Typography</h3>
                  <p>Inter for English and numerical data.</p>
                </div>
              </div>
              <div className="type-samples">
                <div className="type-32">Decision clarity</div>
                <div className="type-24">Supply Pressure</div>
                <div className="type-20">Expected harvest</div>
                <div className="type-16">
                  Body text for explanations and actions.
                </div>
                <div className="type-14">Supporting data and labels</div>
                <div className="type-12">METADATA · VERSION 3.2</div>
              </div>
            </div>
            <div className="system-card" id="spacing">
              <div className="system-card__head">
                <div>
                  <h3>Shape & elevation</h3>
                  <p>Soft containment with restrained depth.</p>
                </div>
              </div>
              <div className="shape-samples">
                <div className="shape shape--sm">
                  <span>8</span>
                </div>
                <div className="shape shape--md">
                  <span>12</span>
                </div>
                <div className="shape shape--lg">
                  <span>16</span>
                </div>
              </div>
              <div className="spacing-scale">
                {[4, 8, 12, 16, 24, 32].map((item) => (
                  <div key={item}>
                    <i style={{ width: `${item * 1.7}px` }} />
                    <span>{item}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        <section className="system-section" id="actions">
          <div className="section-label">
            <span>02</span>
            <div>
              <h2>Actions & inputs</h2>
              <p>Clear hierarchy, visible focus and 44–48px targets.</p>
            </div>
          </div>
          <div className="system-card component-board">
            <div className="component-group">
              <span className="component-label">BUTTONS</span>
              <div className="component-row">
                <Button>Primary</Button>
                <Button variant="secondary">Secondary</Button>
                <Button variant="ghost">Ghost</Button>
                <Button variant="danger">Destructive</Button>
                <Button disabled>Disabled</Button>
              </div>
            </div>
            <div className="component-group">
              <span className="component-label">CONTROLS</span>
              <div className="component-row">
                <label className="text-field">
                  <span>District</span>
                  <div>
                    <Search size={16} />
                    <input value="Anuradhapura" readOnly />
                  </div>
                  <small>Coverage available</small>
                </label>
                <SelectControl label="Season" value="Maha 2026" />
                <label className="toggle-control">
                  <span>
                    <strong>Include uncertainty</strong>
                    <small>Show low and high ranges</small>
                  </span>
                  <input
                    type="checkbox"
                    checked={toggle}
                    onChange={() => setToggle(!toggle)}
                  />
                  <i />
                </label>
              </div>
            </div>
            <div className="component-group">
              <span className="component-label">TABS & CHIPS</span>
              <div className="component-row">
                <div className="tabs">
                  {["Overview", "Scenarios", "Sources"].map((item) => (
                    <button
                      onClick={() => setTab(item)}
                      className={tab === item ? "active" : ""}
                      type="button"
                      key={item}
                    >
                      {item}
                    </button>
                  ))}
                </div>
                <span className="chip">
                  <Leaf size={14} />
                  Big onion
                  <X size={13} />
                </span>
                <span className="chip chip--neutral">Maha 2026</span>
              </div>
            </div>
          </div>
        </section>

        <section className="system-section" id="signals">
          <div className="section-label">
            <span>03</span>
            <div>
              <h2>Signals & status</h2>
              <p>Never rely on colour alone: pair colour, icon and label.</p>
            </div>
          </div>
          <div className="foundation-grid">
            <div className="system-card">
              <div className="system-card__head">
                <div>
                  <h3>Risk badges</h3>
                  <p>SPI interpretation across every output.</p>
                </div>
              </div>
              <div className="badge-stack">
                <RiskBadge risk="shortage" />
                <RiskBadge risk="balanced" />
                <RiskBadge risk="oversupply" />
              </div>
            </div>
            <div className="system-card">
              <div className="system-card__head">
                <div>
                  <h3>Confidence badges</h3>
                  <p>Model and source freshness.</p>
                </div>
              </div>
              <div className="badge-stack">
                <ConfidenceBadge level="High" />
                <ConfidenceBadge level="Medium" />
                <ConfidenceBadge level="Low" />
                <ConfidenceBadge level="Outdated" />
              </div>
            </div>
          </div>
          <div className="system-card states-board" id="states">
            <div className="system-card__head">
              <div>
                <h3>Key system states</h3>
                <p>Patterns shared by officer and farmer experiences.</p>
              </div>
            </div>
            <div className="states-grid">
              <StateCard
                icon={CheckCircle2}
                title="Success"
                body="Decision recorded and versioned."
                variant="success"
              />
              <StateCard
                icon={TriangleAlert}
                title="Outdated data"
                body="Source has not updated in 45 days."
                variant="warning"
              />
              <StateCard
                icon={AlertCircle}
                title="Low confidence"
                body="Interpret this range with caution."
                variant="info"
              />
              <StateCard
                icon={ShieldCheck}
                title="Permission denied"
                body="Ask an administrator for access."
                variant="neutral"
              />
              <StateCard
                icon={Database}
                title="No records yet"
                body="New data will appear here."
                variant="neutral"
              />
              <div className="state-card state-card--skeleton">
                <span />
                <div>
                  <strong />
                  <p />
                  <p />
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className="system-section" id="data">
          <div className="section-label">
            <span>04</span>
            <div>
              <h2>Data visualisation</h2>
              <p>Ranges first, point estimates second, provenance always.</p>
            </div>
          </div>
          <div className="system-card viz-card">
            <div className="system-card__head">
              <div>
                <h3>Supply band chart</h3>
                <p>
                  Low–High scenario band, middle line and dashed demand
                  reference.
                </p>
              </div>
              <ConfidenceBadge level="High" />
            </div>
            <SupplyChart
              area={2131}
              yieldValue={16.45}
              selectedMonth={6}
              onSelectMonth={() => {}}
            />
          </div>
        </section>
      </main>
    </div>
  )
}

