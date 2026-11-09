# Price X-Ray (@PriceXRay) — Official Design System & Token Architecture

## 1. Visual World & Aesthetic Direction
**Forensic Supply-Chain Telemetry & Laboratory Dossier**
Designed around an optical/X-ray inspection instrument aesthetic. High-contrast Deep Carbon surfaces (`#0B0E14`) allow product photography and three semantic forensic signal colors to read with laboratory clarity without relying on decorative neon halos or generic SaaS card templates.

- **Surface Mode:** Persuade + Operate hybrid (high-speed episode lookup + side-by-side specification verification + immediate affiliate conversion).
- **Iconography:** Strictly 1.75px–2px stroke inline vector SVGs (zero emoji glyphs).
- **Elevation System:** Directional dark-room physical elevation shadows (`0 16px 36px -8px rgba(2, 6, 23, 0.85)`) paired with 1px specular surface borders (`rgba(255, 255, 255, 0.08)`) and crisp semantic borders (`rgba(0, 240, 255, 0.3)`). Zero blurred colored halos.

---

## 2. Three-Layer Token Architecture

### Layer 1: Primitive Tokens (`:root`)
| Token | Value | Role |
|---|---|---|
| `--primitive-carbon-950` | `#0B0E14` | Official Price X-Ray Deep Carbon background |
| `--primitive-carbon-900` | `#121722` | Primary forensic instrument panel |
| `--primitive-carbon-850` | `#171E2C` | Elevated interactive card / control surface |
| `--primitive-carbon-800` | `#1E2738` | Hover / active control surface |
| `--primitive-cyan-400` | `#00F0FF` | Official X-Ray Cyan (specs, OEM links, focus) |
| `--primitive-crimson-500` | `#FF2A54` | Official Markup Crimson (retail brand & logo tax) |
| `--primitive-emerald-400` | `#00E676` | Official Factory Emerald (Factory Twin price & savings) |
| `--primitive-slate-50` | `#F8FAFC` | Primary high-contrast foreground text |
| `--primitive-slate-300` | `#CBD5E1` | Secondary reading copy |
| `--primitive-slate-400` | `#94A3B8` | Muted metadata & technical captions |

### Layer 2: Semantic Tokens
| Token | Mapping | Purpose |
|---|---|---|
| `--surface-canvas` | `var(--primitive-carbon-950)` | Page background |
| `--surface-panel` | `var(--primitive-carbon-900)` | Dossier cards and sticky command bar |
| `--surface-elevated` | `var(--primitive-carbon-850)` | Spec callout boxes and interactive pills |
| `--signal-xray` | `var(--primitive-cyan-400)` | Forensic verification, OEM telemetry, active filter |
| `--signal-markup` | `var(--primitive-crimson-500)` | Overpriced retail brand price & Logo Tax ratio bar |
| `--signal-twin` | `var(--primitive-emerald-400)` | Verified Factory Twin price, savings badge, primary CTA |

### Layer 3: Typography Scale & Roles
- **Display & Headings (`--font-display`):** `'Montserrat', 'Inter', system-ui, sans-serif`
  - `h1`: `clamp(2rem, 4vw, 2.75rem)` (`32px–44px`), Weight `900`, Tracking `-0.03em`, Line-height `1.1`
  - `h2`: `clamp(1.375rem, 2.5vw, 1.75rem)` (`22px–28px`), Weight `800`, Tracking `-0.025em`, Line-height `1.2`
  - `h3`: `1.125rem` (`18px`), Weight `800`, Tracking `-0.015em`, Line-height `1.3`
- **Body & UI Controls (`--font-sans`):** `'Inter', system-ui, -apple-system, sans-serif`
  - `body`: `1rem` (`16px`), Weight `400–600`, Line-height `1.6`, Measure `45ch–72ch`
- **Forensic Data & Bill of Materials (`--font-mono`):** `'JetBrains Mono', ui-monospace, monospace`
  - Enforces `font-variant-numeric: tabular-nums` on all prices, percentages, episode numbers, and spec codes.
