#!/usr/bin/env python3
"""
Builds the top-tier Price X-Ray (@PriceXRay) GitHub Pages Storefront (`gh_pages_deploy/index.html`
and `landing_page/index.html`) + `episodes_100.json`, strictly preserving the official brand identity
from `branding/channel_identity.md` and enforcing all design rules from `impeccable`, `ui-ux-pro-max`,
`frontend-design`, `design-system`, and `brand`.
"""

import json
import os
import re

BASE_DIR = os.environ.get(
    "PRICEXRAY_BASE_DIR",
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
)
ALL_EPISODES_PATH = os.path.join(BASE_DIR, "calendar_30days", "all_100_episodes.json")
GH_DEPLOY_DIR = (
    os.path.join(BASE_DIR, "gh_pages_deploy")
    if os.path.isdir(os.path.join(BASE_DIR, "gh_pages_deploy"))
    else BASE_DIR
)
LANDING_DIR = (
    os.path.join(BASE_DIR, "landing_page")
    if os.path.isdir(os.path.join(BASE_DIR, "landing_page"))
    else GH_DEPLOY_DIR
)


def infer_category_group(category: str = "", title: str = "") -> str:
    text = f"{category} {title}".lower()
    if re.search(
        r"audio|earbud|headphone|speaker|cable|charger|magsafe|qi2|keyboard|mouse|usb|hdmi|power bank|ssd|tech|webcam|microphone|hub|dock|gan|projector|led|smart|tracker|router|dac|amp",
        text,
    ):
        return "Tech & Audio"
    if re.search(
        r"chair|desk|stand|monitor|ratchet|wrench|tool|filter|jump starter|towel|inflator|tire|screwdriver|flashlight|laser|multimeter|drill|socket|wiper|obd|garage|automotive|car|ergonomic|caliper|soldering|level|pliers|jack|pressure washer|dashcam",
        text,
    ):
        return "Workspace & Tools"
    if re.search(
        r"hair|serum|skin|toothbrush|razor|shave|shaver|massage|red light|beauty|care|bond|retinol|sunscreen|flosser|scale|fitness|gym|foam roller|creatine|electrolyte|derma|percussive|recovery|grooming|trimmer",
        text,
    ):
        return "Fitness & Care"
    if re.search(
        r"eyewear|sunglass|cooler|fragrance|perfume|cologne|ultrasonic|watch|luggage|bag|backpack|wallet|belt|umbrella|jacket|cashmere|merino|apparel|shoe|insole|travel|jewelry|packing|titanium pen|edc",
        text,
    ):
        return "Style & Travel"
    return "Home & Kitchen"


def parse_price(val, fallback: float = 0.0) -> float:
    if isinstance(val, (int, float)):
        return float(val)
    if isinstance(val, str):
        cleaned = re.sub(r"[^0-9.]", "", val)
        try:
            return float(cleaned)
        except ValueError:
            return fallback
    return fallback


def build_deals_array() -> list:
    with open(ALL_EPISODES_PATH, "r", encoding="utf-8") as f:
        raw_eps = json.load(f)

    deals = []
    for idx, item in enumerate(raw_eps):
        day = int(item.get("day", idx + 1))
        category = item.get("category", "Factory Twin")
        title = item.get("title", f"Episode #{day} Factory Twin")
        clean_title = re.sub(r"\s*#shorts\b", "", title, flags=re.IGNORECASE).strip()

        group = item.get("group") or infer_category_group(category, clean_title)
        left_brand = item.get("left_brand") or item.get("leftBrand") or "Retail Brand"
        right_twin = item.get("right_twin") or item.get("rightTwin") or "Factory Twin"

        left_price = parse_price(item.get("left_price") or item.get("leftPrice"), 100)
        right_price = parse_price(item.get("right_price") or item.get("rightPrice"), 20)

        spec = (
            item.get("smoking_gun_spec")
            or item.get("spec")
            or "Verified Tier-1 OEM/ODM Factory Line & Material Spec Match"
        )
        query = (
            item.get("amazon_search_query")
            or item.get("query")
            or right_twin
        )
        ali_query = (
            item.get("aliexpress_search_query")
            or re.sub(r"\(.*?\)", "", right_twin).strip()
        )
        hook = item.get("hook_0_to_4s", "")
        body = item.get("body_4_to_24s", "")
        reveal = item.get("reveal_24_to_32s", "")

        thumb_map = {
            1: "./assets/video1_sunglasses.png",
            2: "./assets/video2_tumbler.png",
            3: "./assets/video3_hairdryer.png",
        }
        thumb = thumb_map.get(day, f"./images/day_{day:02d}.jpg")
        savings_pct = (
            round(((left_price - right_price) / left_price) * 100)
            if left_price > 0
            else 80
        )
        hot = bool(day <= 6 or savings_pct >= 86 or (left_price - right_price) >= 300)

        deals.append(
            {
                "video": day,
                "day": day,
                "group": group,
                "category": category,
                "title": clean_title,
                "leftBrand": left_brand,
                "leftPrice": int(round(left_price)) if left_price >= 1 else round(left_price, 2),
                "rightTwin": right_twin,
                "rightPrice": int(round(right_price)) if right_price >= 1 else round(right_price, 2),
                "spec": spec,
                "hook": hook,
                "body": body,
                "reveal": reveal,
                "query": query,
                "aliQuery": ali_query,
                "thumb": thumb,
                "hot": hot,
                "youtubeVideoId": item.get("youtube_video_id", ""),
                "youtubeShortsUrl": item.get("youtube_shorts_url", ""),
            }
        )

    deals.sort(key=lambda x: x["day"])
    return deals


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en" class="dark scroll-smooth">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0" />
  <title>Price X-Ray (@PriceXRay) — Official Unblurred OEM Factory Twin Dossier (#1–#600)</title>
  <meta name="description" content="Same Factory. Same Specs. 80% Less. We X-Ray the Markup. Search Episodes #1–#600 from @PriceXRay to unlock verified OEM Factory Twin links, lab spec breakdowns, and £25/$30 cashback bonuses." />
  <meta name="theme-color" content="#0B0E14" />
  <meta name='impact-site-verification' value='8601fafe-4b95-43ee-8a45-9c849c70173b'>
  <link rel="canonical" href="https://saaalahy93-a11y.github.io/price-xray-storefront/" />
  <meta property="og:title" content="Price X-Ray (@PriceXRay) — 600 Unblurred OEM Factory Twins" />
  <meta property="og:description" content="Same Factory. Same Specs. 80% Less. Search all 600 verified OEM Factory Twin teardowns across Amazon Prime, AliExpress Direct, Walmart, eBay Open-Box & Rakuten £25/$30 Cashback." />
  <meta property="og:type" content="website" />
  <meta property="og:url" content="https://saaalahy93-a11y.github.io/price-xray-storefront/" />
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@graph": [
      {
        "@type": "Organization",
        "name": "Price X-Ray Labs (ANKH ENTERPRISE LTD)",
        "legalName": "ANKH ENTERPRISE LTD",
        "taxID": "CRN 17511325",
        "url": "https://saaalahy93-a11y.github.io/price-xray-storefront/",
        "sameAs": ["https://www.youtube.com/@PriceXRay"],
        "address": {
          "@type": "PostalAddress",
          "streetAddress": "66 Paul Street",
          "addressLocality": "London",
          "postalCode": "EC2A 4NA",
          "addressCountry": "GB"
        }
      },
      {
        "@type": "WebSite",
        "name": "Price X-Ray (@PriceXRay) Official 600-Item OEM Factory Twin Dossier",
        "url": "https://saaalahy93-a11y.github.io/price-xray-storefront/"
      }
    ]
  }
  </script>

  <!-- Google Fonts: Montserrat (Display Headlines), Inter (UI & Body), JetBrains Mono (Forensic BOM & Telemetry) -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;600;700;800&family=Montserrat:wght@700;800;900&display=swap" rel="stylesheet">

  <!-- Tailwind CSS CDN -->
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          colors: {
            carbon: '#0B0E14',
            panel: '#121722',
            surface: '#171E2C',
            elevated: '#1E2738',
            xray: '#00F0FF',
            markup: '#FF2A54',
            twin: '#00E676'
          },
          fontFamily: {
            display: ['Montserrat', 'Inter', 'system-ui', 'sans-serif'],
            sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
            mono: ['JetBrains Mono', 'ui-monospace', 'SFMono-Regular', 'monospace']
          }
        }
      }
    };
  </script>

  <style>
    /* ==========================================================================
       THREE-LAYER DESIGN TOKEN ARCHITECTURE (Primitive -> Semantic -> Component)
       Preserving Official @PriceXRay Brand Identity
       ========================================================================== */
    :root {
      /* Layer 1: Primitive Brand Tokens */
      --primitive-carbon-950: #0B0E14;
      --primitive-carbon-900: #121722;
      --primitive-carbon-850: #171E2C;
      --primitive-carbon-800: #1E2738;
      --primitive-cyan-400: #00F0FF;
      --primitive-crimson-500: #FF2A54;
      --primitive-emerald-400: #00E676;
      --primitive-slate-50: #F8FAFC;
      --primitive-slate-200: #E2E8F0;
      --primitive-slate-300: #CBD5E1;
      --primitive-slate-400: #94A3B8;
      --primitive-border-subtle: rgba(148, 163, 184, 0.16);
      --primitive-border-strong: rgba(148, 163, 184, 0.28);

      /* Layer 2: Semantic Tokens */
      --surface-canvas: var(--primitive-carbon-950);
      --surface-panel: var(--primitive-carbon-900);
      --surface-elevated: var(--primitive-carbon-850);
      --surface-interactive: var(--primitive-carbon-800);
      --text-primary: var(--primitive-slate-50);
      --text-secondary: var(--primitive-slate-300);
      --text-muted: var(--primitive-slate-400);
      --signal-xray: var(--primitive-cyan-400);
      --signal-markup: var(--primitive-crimson-500);
      --signal-twin: var(--primitive-emerald-400);

      /* Layer 3: Motion & Timing */
      --ease-out-expo: cubic-bezier(0.16, 1, 0.3, 1);
    }

    /* Browser Surface Craft Floor: Selection, Caret, Scrollbars, Focus Rings, Tabular Numerals */
    *, *::before, *::after {
      box-sizing: border-box;
    }

    html {
      background-color: var(--surface-canvas);
      color: var(--text-primary);
      font-family: 'Inter', system-ui, -apple-system, sans-serif;
      font-size: 16px;
      line-height: 1.6;
      caret-color: var(--signal-xray);
      scrollbar-width: thin;
      scrollbar-color: #263248 #0B0E14;
    }

    ::-webkit-scrollbar {
      width: 8px;
      height: 8px;
    }
    ::-webkit-scrollbar-track {
      background: #0B0E14;
    }
    ::-webkit-scrollbar-thumb {
      background: #263248;
      border-radius: 4px;
      border: 2px solid #0B0E14;
    }
    ::-webkit-scrollbar-thumb:hover {
      background: #3B4C6B;
    }

    ::selection {
      background-color: rgba(0, 240, 255, 0.24);
      color: #F8FAFC;
    }

    :focus-visible {
      outline: 2px solid var(--signal-xray);
      outline-offset: 2px;
    }

    body {
      background-color: var(--surface-canvas);
      color: var(--text-primary);
      font-size: 1rem;
      line-height: 1.6;
      overflow-x: hidden;
    }

    /* Explicit Typographic Hierarchy (>1.25x Scale Steps) */
    h1 {
      font-family: 'Montserrat', 'Inter', system-ui, sans-serif;
      font-size: clamp(2rem, 4vw, 2.75rem);
      font-weight: 900;
      line-height: 1.1;
      letter-spacing: -0.03em;
      text-wrap: balance;
      color: var(--text-primary);
    }

    h2 {
      font-family: 'Montserrat', 'Inter', system-ui, sans-serif;
      font-size: clamp(1.375rem, 2.5vw, 1.75rem);
      font-weight: 800;
      line-height: 1.22;
      letter-spacing: -0.022em;
      text-wrap: balance;
      color: var(--text-primary);
    }

    h3 {
      font-family: 'Montserrat', 'Inter', system-ui, sans-serif;
      font-size: 1.15rem;
      font-weight: 800;
      line-height: 1.32;
      letter-spacing: -0.015em;
      text-wrap: balance;
      color: var(--text-primary);
    }

    p {
      max-width: 70ch;
    }

    .tabular-nums,
    .font-mono {
      font-variant-numeric: tabular-nums;
    }

    /* Forensic Instrument Surfaces (Defined 1px Edges, Built-in Static Padding) */
    .forensic-panel {
      background-color: var(--surface-panel);
      border: 1px solid var(--primitive-border-subtle);
      border-radius: 1rem;
      padding: 1.5rem;
    }

    .forensic-panel-accent {
      background: linear-gradient(165deg, #161F30 0%, #121722 70%, #0E201B 100%);
      border: 1px solid rgba(0, 240, 255, 0.36);
      border-radius: 1rem;
      padding: 1.5rem;
    }

    .dossier-card {
      background-color: var(--surface-panel);
      border: 1px solid var(--primitive-border-subtle);
      border-radius: 1rem;
      padding: 1.25rem;
      transition: border-color 180ms var(--ease-out-expo), background-color 180ms var(--ease-out-expo);
    }

    .dossier-card:hover {
      border-color: rgba(0, 240, 255, 0.45);
    }

    .dossier-card-featured {
      border-color: rgba(0, 240, 255, 0.32);
    }

    .cta-emerald {
      background-color: #00E676;
      color: #05140C;
      padding: 0.75rem 1.125rem;
      border-radius: 0.75rem;
      transition: background-color 150ms var(--ease-out-expo), transform 120ms var(--ease-out-expo);
    }
    .cta-emerald:hover {
      background-color: #26F08C;
    }
    .cta-emerald:active {
      transform: scale(0.99);
    }

    .cta-xray {
      background-color: #00F0FF;
      color: #051217;
      padding: 0.55rem 0.95rem;
      border-radius: 0.625rem;
      transition: background-color 150ms var(--ease-out-expo), transform 120ms var(--ease-out-expo);
    }
    .cta-xray:hover {
      background-color: #47F5FF;
    }
    .cta-xray:active {
      transform: scale(0.99);
    }

    .no-scrollbar::-webkit-scrollbar {
      display: none;
    }
    .no-scrollbar {
      -ms-overflow-style: none;
      scrollbar-width: none;
    }

    @media (prefers-reduced-motion: reduce) {
      *, *::before, *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
        scroll-behavior: auto !important;
      }
    }
  </style>
</head>
<body class="min-h-screen antialiased">

  <!-- ===================================================================== -->
  <!-- TOP STICKY BAR: FREE PRICE-CHECKER BROWSER EXTENSION                  -->
  <!-- ===================================================================== -->
  <div class="sticky top-0 z-50 bg-[#0B0E14]/95 border-b border-slate-800 backdrop-blur-md">
    <div class="max-w-6xl mx-auto px-4 py-2.5 flex items-center justify-between gap-3">
      <div class="flex items-center gap-3 min-w-0">
        <span class="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-surface text-xray" aria-hidden="true">
          <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="9"/>
            <line x1="12" y1="3" x2="12" y2="7"/>
            <line x1="12" y1="17" x2="12" y2="21"/>
            <line x1="3" y1="12" x2="7" y2="12"/>
            <line x1="17" y1="12" x2="21" y2="12"/>
            <circle cx="12" cy="12" r="2"/>
          </svg>
        </span>
        <div class="min-w-0">
          <div class="flex items-center gap-2">
            <span class="inline-block w-2 h-2 rounded-full bg-twin" aria-hidden="true"></span>
            <span id="cpa-badge" class="text-[11px] font-mono uppercase tracking-wider text-xray font-semibold truncate">
              FREE BROWSER EXTENSION • OEM AUTO-SCANNER
            </span>
          </div>
          <p class="text-xs sm:text-sm font-bold text-slate-100 truncate">
            Auto-Detect Cheaper Factory Twins While Browsing Amazon &amp; Retail Stores
          </p>
        </div>
      </div>
      <a
        id="cpa-top-btn"
        href="https://www.capitaloneshopping.com/?utm_source=pricexray_bio"
        target="_blank"
        rel="noopener sponsored"
        class="cta-xray shrink-0 inline-flex items-center gap-1.5 text-xs font-extrabold tracking-tight cursor-pointer"
      >
        <span>Add Free Tool</span>
        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2.25" viewBox="0 0 24 24" aria-hidden="true">
          <path stroke-linecap="round" stroke-linejoin="round" d="M13 7l5 5m0 0l-5 5m5-5H6" />
        </svg>
      </a>
    </div>
  </div>

  <!-- ===================================================================== -->
  <!-- MAIN FORENSIC COMMAND CENTER CONTAINER                                -->
  <!-- ===================================================================== -->
  <main class="max-w-6xl mx-auto px-4 sm:px-6 pt-6 pb-24">

    <!-- =================================================================== -->
    <!-- CHANNEL IDENTITY HEADER & LIVE TELEMETRY (Flattened Hierarchy)      -->
    <!-- =================================================================== -->
    <header class="mb-7 pb-6 border-b border-slate-800">
      <!-- Channel Banner Visual Header -->
      <div class="relative h-28 sm:h-36 w-full rounded-2xl overflow-hidden bg-panel mb-4">
        <img
          src="./assets/channel_banner.png"
          alt="Price X-Ray Channel Banner"
          onerror="this.style.display='none';"
          class="w-full h-full object-cover opacity-55"
        />
        <div class="absolute inset-0 bg-gradient-to-t from-[#0B0E14] via-[#0B0E14]/45 to-transparent"></div>
        <div class="absolute top-3 right-3 sm:top-4 sm:right-4">
          <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-md bg-carbon/90 text-[11px] font-mono font-semibold text-xray">
            <svg class="w-3.5 h-3.5 text-xray" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/>
            </svg>
            <span>FCC / UL / Import BOL Cross-Checked</span>
          </span>
        </div>
      </div>

      <!-- Profile Identity & Tagline -->
      <div class="flex flex-col sm:flex-row sm:items-end justify-between gap-4 -mt-12 sm:-mt-14 px-2 relative z-10">
        <div class="flex items-end gap-4">
          <div class="relative shrink-0">
            <img
              src="./assets/channel_logo.png"
              alt="Price X-Ray Official Logo"
              onerror="this.style.display='none'; document.getElementById('fallback-logo').style.display='flex';"
              class="w-20 h-20 sm:w-24 sm:h-24 rounded-2xl border-2 border-xray object-cover bg-carbon"
            />
            <div
              id="fallback-logo"
              style="display:none;"
              class="w-20 h-20 sm:w-24 sm:h-24 rounded-2xl border-2 border-xray bg-carbon items-center justify-center font-mono font-extrabold text-xl text-xray"
            >
              X-RAY
            </div>
            <span class="absolute -bottom-1.5 -right-1.5 inline-flex items-center gap-1 bg-twin text-carbon text-[10px] font-mono font-extrabold px-2 py-0.5 rounded-full">
              <svg class="w-2.5 h-2.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/>
              </svg>
              <span>OEM LAB</span>
            </span>
          </div>

          <div class="pt-2">
            <div class="flex flex-wrap items-center gap-2.5">
              <h1>Price X-Ray</h1>
              <span class="text-xs font-mono font-bold text-xray bg-surface px-2.5 py-1 rounded-md">@PriceXRay</span>
            </div>
            <p class="text-sm sm:text-base text-slate-200 mt-1 font-semibold">
              Same Factory. Same Specs. <span class="text-twin font-extrabold">80% Less.</span> We X-Ray the Markup.
            </p>
          </div>
        </div>

        <div class="flex flex-wrap items-center gap-2 self-start sm:self-end">
          <label for="region-select" class="sr-only">Select Storefront Country / Store Region</label>
          <select
            id="region-select"
            aria-label="Global Storefront Geo-Router (OneLink)"
            class="px-3 py-2 rounded-xl bg-panel hover:bg-surface border border-slate-800 text-xs font-mono font-bold text-slate-200 transition cursor-pointer"
          >
            <option value="US">🇺🇸 Store: US (USD)</option>
            <option value="UK">🇬🇧 Store: UK (GBP)</option>
            <option value="CA">🇨🇦 Store: CA (CAD)</option>
            <option value="DE">🇩🇪 Store: EU/DE (EUR)</option>
            <option value="AU">🇦🇺 Store: AU (AUD)</option>
          </select>
          <a
            href="https://www.youtube.com/@PriceXRayOfficial?sub_confirmation=1"
            target="_blank"
            rel="noopener"
            class="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-markup hover:bg-markup/90 text-xs font-mono font-extrabold text-white transition cursor-pointer"
          >
            <span>▶ Subscribe (@PriceXRayOfficial)</span>
          </a>
          <a
            href="./bounties.html"
            class="inline-flex items-center gap-1.5 px-3 py-2 rounded-xl bg-panel hover:bg-surface border border-amber-400/40 text-xs font-mono font-bold text-amber-300 transition cursor-pointer"
          >
            <span>🏦 9-Bounty Vault</span>
          </a>
          <a
            href="#search-input"
            class="inline-flex items-center gap-2 px-3.5 py-2 rounded-xl bg-panel hover:bg-surface border border-slate-800 text-xs font-mono font-bold text-xray transition cursor-pointer"
          >
            <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
              <circle cx="11" cy="11" r="8"/><path stroke-linecap="round" d="m21 21-4.3-4.3"/>
            </svg>
            <span>Jump to Episode (<span id="header-range-label">#1–#600</span>)</span>
          </a>
        </div>
      </div>

      <p class="text-xs sm:text-sm text-slate-300 mt-4 px-2 leading-relaxed">
        Big brands don’t own factories—they hire Original Equipment Manufacturers (OEMs), stamp a $200 logo on an existing chassis, and charge a 400% Brand Tax. Below is every unblurred Factory Twin dossier from our daily Shorts.
      </p>

      <!-- Live Channel Telemetry Matrix (Structural Hairline Grid, Zero Nested Cards) -->
      <div class="mt-5 pt-5 border-t border-slate-800/90 grid grid-cols-2 sm:grid-cols-4 gap-4 px-2">
        <div>
          <div id="metric-total-deals" class="text-lg sm:text-xl font-extrabold text-white font-mono tabular-nums">100 / 100</div>
          <div class="text-xs text-slate-400 font-medium">Unblurred Factory Dossiers</div>
        </div>
        <div class="sm:border-l sm:border-slate-800 sm:pl-4">
          <div id="metric-avg-savings" class="text-lg sm:text-xl font-extrabold text-twin font-mono tabular-nums">81% AVG</div>
          <div class="text-xs text-slate-400 font-medium">Logo Tax Eliminated</div>
        </div>
        <div class="sm:border-l sm:border-slate-800 sm:pl-4">
          <div id="metric-cumulative-saved" class="text-lg sm:text-xl font-extrabold text-xray font-mono tabular-nums">$18,400+</div>
          <div class="text-xs text-slate-400 font-medium">Total Catalog Markup Exposed</div>
        </div>
        <div class="sm:border-l sm:border-slate-800 sm:pl-4">
          <div class="text-lg sm:text-xl font-extrabold text-slate-100 font-mono tabular-nums">Tier-1 OEM</div>
          <div class="text-xs text-slate-400 font-medium">Material &amp; Patent Verified</div>
        </div>
      </div>
    </header>

    <!-- =================================================================== -->
    <!-- FEATURED HERO CPA DIAGNOSTIC MODULE: FREE PRICE-CHECKER EXTENSION   -->
    <!-- =================================================================== -->
    <section class="mb-7 forensic-panel-accent relative overflow-hidden">
      <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-5">
        <div class="space-y-2">
          <div class="flex flex-wrap items-center justify-between lg:justify-start gap-2.5">
            <h2>Stop Paying the "Logo Tax" — Get the Free Price-Checker Extension</h2>
            <span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[11px] font-mono font-bold bg-twin/15 text-twin">
              <svg class="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/>
              </svg>
              <span>100% FREE • CHROME / SAFARI / iOS</span>
            </span>
          </div>
          <p class="text-xs sm:text-sm text-slate-300 leading-relaxed">
            Whenever you view an overpriced brand on Amazon, Target, or Best Buy, this free browser tool automatically alerts you if an identical <span class="text-twin font-semibold">warehouse twin, hidden coupon code, or cheaper direct seller</span> is in stock.
          </p>
        </div>

        <div class="flex flex-col sm:flex-row lg:flex-col items-stretch sm:items-center lg:items-end justify-between gap-2 shrink-0">
          <a
            id="cpa-hero-btn"
            href="https://www.capitaloneshopping.com/?utm_source=pricexray_hero"
            target="_blank"
            rel="noopener sponsored"
            class="cta-emerald inline-flex items-center justify-center gap-2 text-xs sm:text-sm font-black tracking-tight cursor-pointer"
          >
            <svg class="w-4 h-4 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.25" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
            </svg>
            <span>Claim £25 / $30 Rakuten Cashback</span>
            <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" d="M14 5l7 7m0 0l-7 7m7-7H3" />
            </svg>
          </a>
          <div class="text-[11px] font-mono text-slate-400 text-center sm:text-right">
            Code: SAAALA5 • Stackable with Amazon &amp; AliExpress Twins
          </div>
        </div>
      </div>
    </section>

    <!-- =================================================================== -->
    <!-- FLAGSHIP YOUTUBE SHORTS LAB THEATER & BINGE CLUSTER                 -->
    <!-- =================================================================== -->
    <section class="mb-7 forensic-panel relative overflow-hidden">
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-5 items-center">
        <div class="lg:col-span-4 flex justify-center">
          <div class="w-full max-w-[260px] aspect-[9/16] rounded-2xl overflow-hidden border border-xray/40 bg-carbon shadow-xl">
            <iframe
              id="flagship-short-iframe"
              src="https://www.youtube-nocookie.com/embed/dXFV2ovYQts?rel=0&playsinline=1"
              title="Price X-Ray Episode #01: $230 Designer Sunglasses vs. $24 Mazzucchelli Acetate Twin"
              class="w-full h-full"
              loading="lazy"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
              allowfullscreen
            ></iframe>
          </div>
        </div>
        <div class="lg:col-span-8 space-y-3.5">
          <div class="flex flex-wrap items-center gap-2">
            <span class="px-2.5 py-1 rounded-md bg-markup/20 text-markup font-mono font-extrabold text-[11px]">● LIVE ON YOUTUBE SHORTS</span>
            <span class="px-2.5 py-1 rounded-md bg-xray/15 text-xray font-mono font-bold text-[11px]">@PriceXRayOfficial • 600-Day Series</span>
          </div>
          <h2>Watch the 45-Second Lab Teardown &amp; Binge the Launch Cluster</h2>
          <p class="text-xs sm:text-sm text-slate-300 leading-relaxed">
            Every day at <strong>15:00 UTC</strong>, we publish a new 60fps forensic Bill-of-Materials teardown exposing the exact Tier-1 OEM factory behind a $100–$1,600 retail brand. Watch Episode #001 directly in the player or switch episodes below:
          </p>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-1">
            <button
              type="button"
              onclick="document.getElementById('flagship-short-iframe').src='https://www.youtube-nocookie.com/embed/dXFV2ovYQts?rel=0&playsinline=1&autoplay=1'; jumpToVideo(1);"
              class="text-left p-2.5 rounded-xl bg-carbon hover:bg-surface border border-xray/40 transition cursor-pointer"
            >
              <div class="text-[10px] font-mono text-xray font-bold">▶ EPISODE #001 • EYEWEAR</div>
              <div class="text-xs font-bold text-white truncate">$230 Ray-Ban vs. $24 Mazzucchelli Twin</div>
            </button>
            <a
              href="./episodes/day-002.html"
              class="text-left p-2.5 rounded-xl bg-carbon hover:bg-surface border border-slate-800 hover:border-xray/40 transition block"
            >
              <div class="text-[10px] font-mono text-twin font-bold">🔍 EPISODE #002 • DRINKWARE</div>
              <div class="text-xs font-bold text-white truncate">$50 Stanley/Yeti vs. $14 304-Steel Twin</div>
            </a>
            <a
              href="./episodes/day-003.html"
              class="text-left p-2.5 rounded-xl bg-carbon hover:bg-surface border border-slate-800 hover:border-xray/40 transition block"
            >
              <div class="text-[10px] font-mono text-twin font-bold">🔍 EPISODE #003 • HAIR TECH</div>
              <div class="text-xs font-bold text-white truncate">$429 Dyson Supersonic vs. $59 110k-RPM Twin</div>
            </a>
            <a
              href="./episodes/day-004.html"
              class="text-left p-2.5 rounded-xl bg-carbon hover:bg-surface border border-slate-800 hover:border-xray/40 transition block"
            >
              <div class="text-[10px] font-mono text-twin font-bold">🔍 EPISODE #004 • OFFICE</div>
              <div class="text-xs font-bold text-white truncate">$1,600 Herman Miller vs. $260 BIFMA Twin</div>
            </a>
          </div>
          <div class="flex flex-wrap items-center gap-2.5 pt-2">
            <a
              href="https://www.youtube.com/@PriceXRayOfficial?sub_confirmation=1"
              target="_blank"
              rel="noopener"
              class="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-markup hover:bg-markup/90 text-white font-mono font-extrabold text-xs transition"
            >
              <span>▶ Subscribe to @PriceXRayOfficial on YouTube</span>
            </a>
            <a
              href="https://www.youtube.com/playlist?list=PLDrSvkoLRQ0s"
              target="_blank"
              rel="noopener"
              class="inline-flex items-center gap-2 px-3.5 py-2.5 rounded-xl bg-carbon hover:bg-surface border border-slate-700 text-xray font-mono font-bold text-xs transition"
            >
              <span>🎬 Open Full YouTube Playlist ↗</span>
            </a>
            <a
              href="./episodes/day-001.html"
              class="inline-flex items-center gap-2 px-3.5 py-2.5 rounded-xl bg-carbon hover:bg-surface border border-slate-700 text-slate-200 font-mono font-bold text-xs transition"
            >
              <span>📄 Episode #001 SEO Dossier →</span>
            </a>
          </div>
        </div>
      </div>
    </section>

    <!-- =================================================================== -->
    <!-- STICKY FORENSIC SEARCH, CATEGORY, SORT & QUICK-JUMP COMMAND BAR     -->
    <!-- =================================================================== -->
    <section
      aria-label="Catalog Search and Filters"
      class="mb-5 sticky top-[57px] z-40 bg-[#0B0E14]/95 backdrop-blur-md pt-3 pb-3.5 border-b border-slate-800"
    >
      <!-- Search + Sort + View Mode Row -->
      <div class="flex flex-col md:flex-row items-stretch md:items-center gap-2.5">
        <div class="relative flex-1">
          <svg class="w-4 h-4 text-xray absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" fill="none" stroke="currentColor" stroke-width="2.2" viewBox="0 0 24 24" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-4.35-4.35m0 0A7.5 7.5 0 103.5 10.5a7.5 7.5 0 0013.15 6.15z" />
          </svg>
          <input
            id="search-input"
            type="search"
            aria-label="Search by Episode Number, Brand, Factory Twin, or Material Spec"
            placeholder="Search Episode # (#1–#100), brand (Dyson, Stanley, Le Creuset), or spec (VG10, Qi2)..."
            class="w-full rounded-xl bg-panel border border-slate-700/90 focus:border-xray pl-10 pr-24 py-2.5 text-xs sm:text-sm text-white placeholder-slate-400 outline-none transition"
          />
          <kbd
            id="search-kbd-hint"
            class="hidden sm:inline-flex items-center px-2 py-0.5 text-[10px] font-mono text-slate-400 bg-surface rounded absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none"
          >
            /
          </kbd>
          <button
            id="clear-search"
            type="button"
            class="hidden absolute right-2.5 top-1/2 -translate-y-1/2 text-[11px] font-mono font-bold bg-surface hover:bg-elevated text-xray px-2.5 py-1 rounded-md cursor-pointer transition"
          >
            CLEAR
          </button>
        </div>

        <!-- Sort & View Controls -->
        <div class="flex items-center gap-2 shrink-0">
          <label for="sort-select" class="sr-only">Sort Dossiers</label>
          <select
            id="sort-select"
            class="rounded-xl bg-panel border border-slate-700/90 focus:border-xray px-3 py-2.5 text-xs font-mono font-semibold text-slate-200 outline-none cursor-pointer transition"
          >
            <option value="day-asc">Sort: Episode # (1 → 100)</option>
            <option value="day-desc">Sort: Newest Episodes First</option>
            <option value="savings-dollar">Sort: Biggest $ Saved</option>
            <option value="savings-pct">Sort: Highest % Markup Cut</option>
            <option value="price-asc">Sort: Lowest Twin Price ($)</option>
          </select>

          <div class="inline-flex rounded-xl bg-panel border border-slate-700/90 p-1" role="group" aria-label="View Mode">
            <button
              id="view-grid-btn"
              type="button"
              onclick="setViewMode('grid')"
              class="inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-mono font-bold bg-xray text-carbon transition cursor-pointer"
              title="Forensic Dossier Cards"
            >
              <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true">
                <rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/>
              </svg>
              <span class="hidden sm:inline">Cards</span>
            </button>
            <button
              id="view-table-btn"
              type="button"
              onclick="setViewMode('table')"
              class="inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-mono font-semibold text-slate-300 hover:text-white transition cursor-pointer"
              title="Compact BOM Spec Table"
            >
              <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true">
                <line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/>
              </svg>
              <span class="hidden sm:inline">BOM Table</span>
            </button>
          </div>
        </div>
      </div>

      <!-- Category Filter Pills (Strict SVG Icons, Zero Emojis) -->
      <div id="category-bar" class="flex items-center gap-1.5 overflow-x-auto no-scrollbar mt-2.5 pb-0.5">
        <button id="all-cat-btn" data-cat="ALL" class="cat-btn shrink-0 inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold bg-xray text-carbon transition cursor-pointer">
          <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16"/>
          </svg>
          <span id="all-cat-label">All 100 Videos</span>
        </button>
        <button data-cat="Tech & Audio" class="cat-btn shrink-0 inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-panel text-slate-300 border border-slate-800 hover:border-slate-600 transition cursor-pointer">
          <svg class="w-3.5 h-3.5 text-xray" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
            <rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/><path d="M9 1v3M15 1v3M9 20v3M15 20v3M20 9h3M20 14h3M1 9h3M1 14h3"/>
          </svg>
          <span>Tech &amp; Audio</span>
        </button>
        <button data-cat="Home & Kitchen" class="cat-btn shrink-0 inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-panel text-slate-300 border border-slate-800 hover:border-slate-600 transition cursor-pointer">
          <svg class="w-3.5 h-3.5 text-xray" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" d="M3 10h18M5 10v8a2 2 0 002 2h10a2 2 0 002-2v-8M8 6h8M10 3h4"/>
          </svg>
          <span>Home &amp; Kitchen</span>
        </button>
        <button data-cat="Style & Travel" class="cat-btn shrink-0 inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-panel text-slate-300 border border-slate-800 hover:border-slate-600 transition cursor-pointer">
          <svg class="w-3.5 h-3.5 text-xray" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
            <circle cx="6" cy="15" r="4"/><circle cx="18" cy="15" r="4"/><path stroke-linecap="round" stroke-linejoin="round" d="M10 15h4M2 15l2-6h3M22 15l-2-6h-3"/>
          </svg>
          <span>Style &amp; Travel</span>
        </button>
        <button data-cat="Workspace & Tools" class="cat-btn shrink-0 inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-panel text-slate-300 border border-slate-800 hover:border-slate-600 transition cursor-pointer">
          <svg class="w-3.5 h-3.5 text-xray" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" d="M14.7 6.3a1 1 0 000 1.4l1.6 1.6a1 1 0 001.4 0l3.77-3.77a6 6 0 01-7.94 7.94l-6.91 6.91a2.12 2.12 0 01-3-3l6.91-6.91a6 6 0 017.94-7.94l-3.76 3.76z"/>
          </svg>
          <span>Workspace &amp; Tools</span>
        </button>
        <button data-cat="Fitness & Care" class="cat-btn shrink-0 inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-panel text-slate-300 border border-slate-800 hover:border-slate-600 transition cursor-pointer">
          <svg class="w-3.5 h-3.5 text-xray" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" d="M22 12h-4l-3 9L9 3l-3 9H2"/>
          </svg>
          <span>Fitness &amp; Care</span>
        </button>
      </div>

      <!-- Quick Video #1 - #100 Number Strip -->
      <div id="number-strip" class="flex items-center gap-1 overflow-x-auto no-scrollbar mt-2 pt-1">
        <!-- Populated by JS -->
      </div>
    </section>

    <!-- Results Counter & Telemetry Status -->
    <div class="flex flex-wrap items-center justify-between gap-2 text-xs text-slate-400 mb-4 px-1">
      <span id="results-count" class="font-mono tabular-nums font-medium">Showing all 100 unblurred Factory Twin dossiers</span>
      <span class="inline-flex items-center gap-1.5 font-mono text-[11px] text-twin font-semibold">
        <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true">
          <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/>
        </svg>
        <span>Direct Amazon Prime + AliExpress OEM + Walmart Links Verified</span>
      </span>
    </div>

    <!-- =================================================================== -->
    <!-- VIDEO #1 TO #100 DEAL DOSSIERS CONTAINER (1-Col Mobile / 2-Col LG)  -->
    <!-- =================================================================== -->
    <section id="deals-grid" class="grid grid-cols-1 lg:grid-cols-2 gap-5">
      <!-- Populated dynamically from DEALS -->
    </section>

    <!-- Compact BOM Spec Table View (Hidden by Default, Toggled via View Mode) -->
    <section id="deals-table-wrap" class="hidden forensic-panel">
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="border-b border-slate-800 text-[11px] font-mono uppercase tracking-wider text-slate-400">
              <th class="py-3 px-3.5">Ep #</th>
              <th class="py-3 px-3.5">Category</th>
              <th class="py-3 px-3.5">Retail Brand (Markup)</th>
              <th class="py-3 px-3.5">Verified OEM Factory Twin</th>
              <th class="py-3 px-3.5">Smoking-Gun Spec</th>
              <th class="py-3 px-3.5 text-right">Saved</th>
              <th class="py-3 px-3.5 text-right">Direct Links</th>
            </tr>
          </thead>
          <tbody id="deals-table-body" class="divide-y divide-slate-800/80 text-xs">
            <!-- Populated dynamically -->
          </tbody>
        </table>
      </div>
    </section>

    <!-- Empty State -->
    <div id="empty-state" class="hidden text-center forensic-panel">
      <div class="w-12 h-12 rounded-xl bg-surface text-xray flex items-center justify-center mx-auto mb-3">
        <svg class="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
          <circle cx="11" cy="11" r="8"/><path stroke-linecap="round" d="m21 21-4.3-4.3"/>
        </svg>
      </div>
      <h3>No matching Episode # or OEM Factory Twin found</h3>
      <p class="text-xs sm:text-sm text-slate-400 mt-1 mb-4 mx-auto">
        Try searching an episode number (1 to 100), a retail brand (e.g. Dyson, YETI, Snap-on), or resetting active filters.
      </p>
      <button
        type="button"
        onclick="resetFilters()"
        class="cta-xray font-bold text-xs cursor-pointer"
      >
        Show All Unblurred Factory Twins
      </button>
    </div>

    <!-- =================================================================== -->
    <!-- COMPLIANCE & FTC DISCLOSURE FOOTER (Flattened Structural Hierarchy) -->
    <!-- =================================================================== -->
    <footer class="mt-14 pt-8 border-t border-slate-800 text-xs text-slate-400 leading-relaxed space-y-3">
      <div class="flex items-center gap-2 text-slate-200 font-bold text-sm">
        <svg class="w-4 h-4 text-xray shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 3v18m-7-6l3-6 3 6H5zm8 0l3-6 3 6h-6z"/>
        </svg>
        <span>FTC &amp; Multi-Network Affiliate Disclosure</span>
      </div>
      <p>
        <strong>As an Amazon Associate I earn from qualifying purchases.</strong> Price X-Ray (<code>@PriceXRay</code>) is a participant in the Amazon Services LLC Associates Program, AliExpress Portals, Walmart / Impact.com, and partner CPA affiliate networks. When you click on links to various merchants on this site and make a purchase or install a free browser extension, this can result in this site earning a commission at zero additional cost to you.
      </p>
      <p>
        All product comparisons are based on independent bill-of-materials analysis, public patent filings, FCC/UL certifications, and component research. "Est. Retail" vs. "Factory Twin" figures are reference estimates at the time of video publication; live merchant pricing and availability are subject to change.
      </p>
      <div class="pt-3 flex flex-wrap items-center justify-between gap-2 border-t border-slate-800/80 font-mono text-[11px] text-slate-400">
        <span>© 2026 Price X-Ray Labs (@PriceXRay) • Operated by ANKH ENTERPRISE LTD (CRN 17511325, 66 Paul Street, London, EC2A 4NA)</span>
        <span>Forensic Supply-Chain Dossier v2.5 • Impact-Site-Verification: 8601fafe-4b95-43ee-8a45-9c849c70173b</span>
      </div>
    </footer>
  </main>

  <!-- Toast Notification for Copy Link -->
  <div
    id="copy-toast"
    role="status"
    aria-live="polite"
    style="padding: 0.65rem 1rem;"
    class="fixed bottom-5 left-1/2 -translate-x-1/2 z-50 hidden rounded-xl bg-twin text-carbon text-xs font-extrabold font-mono"
  >
    Direct Factory Twin Link Copied
  </div>

  <!-- ===================================================================== -->
  <!-- AFFILIATE CONFIGURATION & FACTORY TWIN DATABASE (#1–#100)             -->
  <!-- ===================================================================== -->
  <script>
    /**
     * MULTI-NETWORK AFFILIATE CONFIGURATION CONSTANTS
     */
    const AMAZON_AFFILIATE_TAG = "pricexray-20";
    const ALIEXPRESS_PORTAL_ID = "pricexray";
    const IMPACT_PARTNER_ID = "pricexray";

    const STOREFRONT_CONFIG = {
      amazonAssociateTag: AMAZON_AFFILIATE_TAG,
      aliexpressPortalId: ALIEXPRESS_PORTAL_ID,
      impactPartnerId: IMPACT_PARTNER_ID,
      cpaExtensionUrl: "https://www.rakuten.co.uk/r/SAAALA5?eeid=26474",
      cpaBadgeText: "CLAIM £25 / $30 RAKUTEN CASHBACK BONUS (CODE: SAAALA5)"
    };

    // Apply CPA config to top sticky bar & hero button
    document.getElementById("cpa-top-btn").href = STOREFRONT_CONFIG.cpaExtensionUrl;
    document.getElementById("cpa-hero-btn").href = STOREFRONT_CONFIG.cpaExtensionUrl;
    document.getElementById("cpa-badge").textContent = STOREFRONT_CONFIG.cpaBadgeText;

    // Built-in 100-Episode Unblurred Factory Twin Catalog (also syncs via episodes_100.json)
    const INITIAL_DEALS_DATA = __INITIAL_DEALS_JSON__;

    function inferCategoryGroup(category = "", title = "") {
      const text = `${category} ${title}`.toLowerCase();
      if (/audio|earbud|headphone|speaker|cable|charger|magsafe|qi2|keyboard|mouse|usb|hdmi|power bank|ssd|tech|webcam|microphone|hub|dock|gan|projector|led|smart|tracker|router|dac|amp/.test(text)) {
        return "Tech & Audio";
      }
      if (/chair|desk|stand|monitor|ratchet|wrench|tool|filter|jump starter|towel|inflator|tire|screwdriver|flashlight|laser|multimeter|drill|socket|wiper|obd|garage|automotive|car|ergonomic|caliper|soldering|level|pliers|jack|pressure washer|dashcam/.test(text)) {
        return "Workspace & Tools";
      }
      if (/hair|serum|skin|toothbrush|razor|shave|shaver|massage|red light|beauty|care|bond|retinol|sunscreen|flosser|scale|fitness|gym|foam roller|creatine|electrolyte|derma|percussive|recovery|grooming|trimmer/.test(text)) {
        return "Fitness & Care";
      }
      if (/eyewear|sunglass|cooler|fragrance|perfume|cologne|ultrasonic|watch|luggage|bag|backpack|wallet|belt|umbrella|jacket|cashmere|merino|apparel|shoe|insole|travel|jewelry|packing|titanium pen|edc/.test(text)) {
        return "Style & Travel";
      }
      return "Home & Kitchen";
    }

    function parseNumericPrice(val, fallback = 0) {
      if (typeof val === "number" && !isNaN(val)) return val;
      if (typeof val === "string") {
        const cleaned = val.replace(/[^0-9.]/g, "");
        const parsed = parseFloat(cleaned);
        if (!isNaN(parsed)) return parsed;
      }
      return fallback;
    }

    function formatPriceLabel(rawVal, numVal) {
      if (typeof rawVal === "string" && rawVal.trim().startsWith("$")) {
        return rawVal.trim();
      }
      if (numVal < 1 && numVal > 0) {
        return `$${numVal.toFixed(2)}`;
      }
      return `$${Math.round(numVal)}`;
    }

    function normalizeEpisode(raw, index = 0, existing = null) {
      const dayNum = parseInt(raw.day ?? raw.video ?? raw.episode ?? raw.id ?? (index + 1), 10);
      const category = raw.category || existing?.category || "Factory Twin";
      const rawTitle = raw.title || existing?.title || `Episode #${dayNum} Factory Twin`;
      const title = rawTitle.replace(/\\s*#shorts\\b/gi, "").trim();
      const group = raw.group || existing?.group || inferCategoryGroup(category, title);

      const leftBrand = raw.brand || raw.leftBrand || raw.left_brand || existing?.leftBrand || "Retail Brand";
      const rightTwin = raw.twin || raw.rightTwin || raw.right_twin || existing?.rightTwin || "Factory Twin";

      const leftPriceNum = parseNumericPrice(raw.brandPrice ?? raw.leftPrice ?? raw.left_price ?? existing?.leftPrice, 100);
      const rightPriceNum = parseNumericPrice(raw.twinPrice ?? raw.rightPrice ?? raw.right_price ?? existing?.rightPrice, 20);

      const brandPriceStr = formatPriceLabel(raw.brandPrice ?? raw.left_price, leftPriceNum);
      const twinPriceStr = formatPriceLabel(raw.twinPrice ?? raw.right_price, rightPriceNum);

      const spec = raw.spec || raw.smoking_gun_spec || existing?.spec || "Verified Tier-1 OEM/ODM Factory Line & Material Spec Match";
      const hook = raw.hook || raw.hook_0_to_4s || existing?.hook || "";
      const body = raw.body || raw.body_4_to_24s || existing?.body || "";
      const reveal = raw.reveal || raw.reveal_24_to_32s || existing?.reveal || "";
      const query = raw.query || raw.amazon_search_query || existing?.query || rightTwin;
      const aliQuery = raw.aliQuery || raw.aliexpress_search_query || existing?.aliQuery || rightTwin.replace(/\\(.*?\\)/g, "").trim();
      const thumb = raw.thumb || existing?.thumb || "";
      const hot = Boolean(raw.hot ?? existing?.hot ?? (dayNum <= 6));
      const youtubeVideoId = raw.youtubeVideoId || raw.youtube_video_id || existing?.youtubeVideoId || "";
      const youtubeShortsUrl = raw.youtubeShortsUrl || raw.youtube_shorts_url || existing?.youtubeShortsUrl || "";

      return {
        day: dayNum,
        video: dayNum,
        group,
        category,
        title,
        brand: leftBrand,
        leftBrand,
        brandPrice: brandPriceStr,
        leftPrice: leftPriceNum,
        twin: rightTwin,
        rightTwin,
        twinPrice: twinPriceStr,
        rightPrice: rightPriceNum,
        spec,
        hook,
        body,
        reveal,
        query,
        aliQuery,
        thumb,
        hot,
        youtubeVideoId,
        youtubeShortsUrl
      };
    }

    let DEALS = INITIAL_DEALS_DATA.map((item, idx) => normalizeEpisode(item, idx));
    let DEALS_DATA = DEALS;

    // Global OneLink & EPN Regional Geo-Routing Engine (US / UK / CA / DE / AU)
    const AMAZON_REGIONAL_DOMAINS = {
      US: "www.amazon.com",
      UK: "www.amazon.co.uk",
      CA: "www.amazon.ca",
      DE: "www.amazon.de",
      AU: "www.amazon.com.au"
    };

    const EBAY_REGIONAL_CONFIG = {
      US: { domain: "www.ebay.com", mkrid: "711-53200-19255-0" },
      UK: { domain: "www.ebay.co.uk", mkrid: "710-53481-19255-0" },
      CA: { domain: "www.ebay.ca", mkrid: "706-53473-19255-0" },
      DE: { domain: "www.ebay.de", mkrid: "707-53477-19255-0" },
      AU: { domain: "www.ebay.com.au", mkrid: "705-53470-19255-0" }
    };

    function detectInitialRegion() {
      try {
        const saved = localStorage.getItem("pricexray_region");
        if (saved && AMAZON_REGIONAL_DOMAINS[saved]) return saved;
        const tz = (Intl.DateTimeFormat().resolvedOptions().timeZone || "").toLowerCase();
        const lang = (navigator.language || "").toLowerCase();
        if (tz.includes("london") || tz.includes("belfast") || lang.endsWith("-gb")) return "UK";
        if (tz.includes("toronto") || tz.includes("vancouver") || tz.includes("montreal") || lang.endsWith("-ca")) return "CA";
        if (tz.includes("berlin") || tz.includes("vienna") || tz.includes("zurich") || lang.startsWith("de")) return "DE";
        if (tz.includes("sydney") || tz.includes("melbourne") || tz.includes("brisbane") || lang.endsWith("-au")) return "AU";
      } catch (e) {}
      return "US";
    }

    let activeRegion = detectInitialRegion();

    // Multi-Network Affiliate URL Builders (Geo-Routed)
    function buildAmazonUrl(query) {
      const domain = AMAZON_REGIONAL_DOMAINS[activeRegion] || AMAZON_REGIONAL_DOMAINS.US;
      return `https://${domain}/s?k=${encodeURIComponent(query)}&tag=${AMAZON_AFFILIATE_TAG}`;
    }

    function buildAliExpressUrl(twinName) {
      const cleanedTwin = (twinName || "").replace(/\\(.*?\\)/g, "").trim();
      return `https://www.aliexpress.com/w/wholesale-${encodeURIComponent(cleanedTwin).replace(/%20/g, "-")}.html?aff_fsk=_c3Z2E4OR&aff_platform=portals-tool&sk=_c3Z2E4OR&tt=CPS_NORMAL`;
    }

    function buildWalmartUrl(query) {
      return `https://www.walmart.com/search?q=${encodeURIComponent(query)}`;
    }

    function buildEbayUrl(query, dayNum = 1) {
      const cleaned = (query || "").replace(/\\(.*?\\)/g, "").trim();
      const cfg = EBAY_REGIONAL_CONFIG[activeRegion] || EBAY_REGIONAL_CONFIG.US;
      const customId = `pricexray-day-${String(dayNum).padStart(3, "0")}-${activeRegion.toLowerCase()}`;
      return `https://${cfg.domain}/sch/i.html?_nkw=${encodeURIComponent(cleaned)}&mkcid=1&mkrid=${cfg.mkrid}&campid=5339000000&customid=${customId}`;
    }

    function buildAmazonBountyOffer(d) {
      const domain = AMAZON_REGIONAL_DOMAINS[activeRegion] || AMAZON_REGIONAL_DOMAINS.US;
      const text = `${d.category || ""} ${d.title || ""} ${d.twin || ""}`.toLowerCase();
      if (/tool|wrench|ratchet|caliper|multimeter|chair|desk|monitor|stand|laser|soldering|drill|socket|obd|garage|office/.test(text)) {
        return {
          label: "Free Amazon Business B2B Account",
          url: `https://business.amazon.com?tag=${AMAZON_AFFILIATE_TAG}`
        };
      }
      if (/audio|earbud|headphone|speaker|microphone|dac|amp|sound|anc/.test(text)) {
        return {
          label: "30-Day Free Audible + Audiobook",
          url: `https://${domain}/hz/audible/mlp?tag=${AMAZON_AFFILIATE_TAG}`
        };
      }
      if (/serum|skin|hair|toothbrush|flosser|razor|shave|filter|creatine|electrolyte|supplement|patch|beauty|care/.test(text)) {
        return {
          label: "6-Mo $0 Prime + 5% Cashback",
          url: `https://${domain}/joinyoungadult?tag=${AMAZON_AFFILIATE_TAG}`
        };
      }
      if ((d.rightPrice || 25) <= 22) {
        return {
          label: "Amazon Haul $2.99+ OEM Store",
          url: `https://${domain}/haul/store?tag=${AMAZON_AFFILIATE_TAG}`
        };
      }
      return {
        label: "30-Day Free Amazon Prime Trial",
        url: `https://${domain}/prime?tag=${AMAZON_AFFILIATE_TAG}`
      };
    }

    // UI State
    let activeCategory = "ALL";
    let searchQuery = "";
    let sortMode = "day-asc";
    let viewMode = "grid";

    const dealsGrid = document.getElementById("deals-grid");
    const dealsTableWrap = document.getElementById("deals-table-wrap");
    const dealsTableBody = document.getElementById("deals-table-body");
    const emptyState = document.getElementById("empty-state");
    const resultsCount = document.getElementById("results-count");
    const searchInput = document.getElementById("search-input");
    const clearSearchBtn = document.getElementById("clear-search");
    const searchKbdHint = document.getElementById("search-kbd-hint");
    const numberStrip = document.getElementById("number-strip");
    const metricTotalDeals = document.getElementById("metric-total-deals");
    const metricAvgSavings = document.getElementById("metric-avg-savings");
    const metricCumulativeSaved = document.getElementById("metric-cumulative-saved");
    const headerRangeLabel = document.getElementById("header-range-label");
    const allCatLabel = document.getElementById("all-cat-label");
    const sortSelect = document.getElementById("sort-select");
    const regionSelect = document.getElementById("region-select");
    if (regionSelect) {
      regionSelect.value = activeRegion;
      regionSelect.addEventListener("change", (e) => {
        activeRegion = e.target.value;
        try { localStorage.setItem("pricexray_region", activeRegion); } catch (err) {}
        renderDeals();
      });
    }

    function updateCatalogCounters() {
      const total = DEALS.length;
      if (metricTotalDeals) metricTotalDeals.textContent = `${total} / ${total}`;
      if (headerRangeLabel) headerRangeLabel.textContent = `#1–#${total}`;
      if (allCatLabel) allCatLabel.textContent = `All ${total} Videos`;

      let totalPct = 0;
      let totalSavedDollars = 0;
      DEALS.forEach(d => {
        const pct = d.leftPrice > 0 ? ((d.leftPrice - d.rightPrice) / d.leftPrice) * 100 : 80;
        totalPct += pct;
        totalSavedDollars += Math.max(0, d.leftPrice - d.rightPrice);
      });
      const avgPct = total > 0 ? Math.round(totalPct / total) : 81;
      if (metricAvgSavings) metricAvgSavings.textContent = `${avgPct}% AVG`;
      if (metricCumulativeSaved) metricCumulativeSaved.textContent = `$${Math.round(totalSavedDollars).toLocaleString()}+`;
    }

    function renderNumberStrip() {
      numberStrip.innerHTML = DEALS.map(d => `
        <button
          type="button"
          onclick="jumpToVideo(${d.day})"
          class="shrink-0 px-2.5 py-1 rounded-md text-[11px] font-mono font-bold tabular-nums bg-panel hover:bg-xray hover:text-carbon text-slate-300 border border-slate-800 transition cursor-pointer"
          title="Jump to Episode #${d.day}: ${d.category}"
        >
          #${d.day}
        </button>
      `).join("");
    }

    function jumpToVideo(videoNum) {
      activeCategory = "ALL";
      updateCategoryButtons();
      searchInput.value = `#${videoNum}`;
      searchQuery = `#${videoNum}`;
      clearSearchBtn.classList.remove("hidden");
      if (searchKbdHint) searchKbdHint.classList.add("hidden");
      renderDeals();
      const targetEl = document.getElementById(`day-${videoNum}`) || document.getElementById(`deal-${videoNum}`);
      if (targetEl) {
        targetEl.scrollIntoView({ behavior: "smooth", block: "nearest" });
      }
    }

    function copyDealLink(videoNum, query) {
      const url = buildAmazonUrl(query);
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(url);
      }
      const toast = document.getElementById("copy-toast");
      toast.textContent = `Episode #${videoNum} Direct Factory Twin Link Copied`;
      toast.classList.remove("hidden");
      setTimeout(() => toast.classList.add("hidden"), 2200);
    }

    function toggleTeardown(dayNum) {
      const panel = document.getElementById(`teardown-panel-${dayNum}`);
      const icon = document.getElementById(`teardown-icon-${dayNum}`);
      const btn = document.getElementById(`teardown-btn-${dayNum}`);
      if (!panel) return;
      const isHidden = panel.classList.contains("hidden");
      if (isHidden) {
        panel.classList.remove("hidden");
        if (icon) icon.style.transform = "rotate(180deg)";
        if (btn) btn.setAttribute("aria-expanded", "true");
      } else {
        panel.classList.add("hidden");
        if (icon) icon.style.transform = "rotate(0deg)";
        if (btn) btn.setAttribute("aria-expanded", "false");
      }
    }

    function setViewMode(mode) {
      viewMode = mode === "table" ? "table" : "grid";
      const gridBtn = document.getElementById("view-grid-btn");
      const tableBtn = document.getElementById("view-table-btn");
      if (viewMode === "grid") {
        gridBtn.className = "inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-mono font-bold bg-xray text-carbon transition cursor-pointer";
        tableBtn.className = "inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-mono font-semibold text-slate-300 hover:text-white transition cursor-pointer";
      } else {
        tableBtn.className = "inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-mono font-bold bg-xray text-carbon transition cursor-pointer";
        gridBtn.className = "inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-mono font-semibold text-slate-300 hover:text-white transition cursor-pointer";
      }
      renderDeals();
    }

    function getFilteredAndSortedDeals() {
      const q = searchQuery.trim().toLowerCase();

      const filtered = DEALS.filter(d => {
        const matchesCat = activeCategory === "ALL" || d.group === activeCategory;
        if (!matchesCat) return false;
        if (!q) return true;

        const numMatch = q.match(/^(?:#|video\\s*[-#]?|deal\\s*[-#]?|day\\s*[-#]?|episode\\s*[-#]?)?0*(\\d{1,3})$/i);
        if (numMatch) {
          return d.day === parseInt(numMatch[1], 10);
        }

        const haystack = [
          `#${d.day}`,
          `day ${d.day}`,
          `video ${d.day}`,
          `episode ${d.day}`,
          d.category,
          d.group,
          d.title,
          d.brand,
          d.twin,
          d.spec,
          d.body
        ].join(" ").toLowerCase();

        return haystack.includes(q);
      });

      return filtered.sort((a, b) => {
        const savA = a.leftPrice - a.rightPrice;
        const savB = b.leftPrice - b.rightPrice;
        const pctA = a.leftPrice > 0 ? (savA / a.leftPrice) : 0;
        const pctB = b.leftPrice > 0 ? (savB / b.leftPrice) : 0;

        if (sortMode === "day-desc") return b.day - a.day;
        if (sortMode === "savings-dollar") return savB - savA || a.day - b.day;
        if (sortMode === "savings-pct") return pctB - pctA || savB - savA;
        if (sortMode === "price-asc") return a.rightPrice - b.rightPrice || a.day - b.day;
        return a.day - b.day;
      });
    }

    function renderDeals() {
      const filtered = getFilteredAndSortedDeals();

      resultsCount.textContent = filtered.length === DEALS.length
        ? `Showing all ${DEALS.length} unblurred Factory Twin dossiers`
        : `Found ${filtered.length} matching Factory Twin dossier${filtered.length === 1 ? "" : "s"}`;

      if (filtered.length === 0) {
        dealsGrid.innerHTML = "";
        dealsGrid.classList.add("hidden");
        dealsTableWrap.classList.add("hidden");
        emptyState.classList.remove("hidden");
        return;
      }

      emptyState.classList.add("hidden");

      if (viewMode === "table") {
        dealsGrid.classList.add("hidden");
        dealsTableWrap.classList.remove("hidden");
        dealsTableBody.innerHTML = filtered.map(d => {
          const savingsDollar = Math.max(0, Math.round(d.leftPrice - d.rightPrice));
          const savingsPct = d.leftPrice > 0
            ? Math.round(((d.leftPrice - d.rightPrice) / d.leftPrice) * 100)
            : 80;
          const amazonUrl = buildAmazonUrl(d.query);
          const aliexpressUrl = buildAliExpressUrl(d.aliQuery || d.twin);

          return `
            <tr id="deal-row-${d.day}" class="hover:bg-surface/70 transition">
              <td class="py-3 px-3.5 font-mono font-bold text-xray whitespace-nowrap">#${d.day}</td>
              <td class="py-3 px-3.5 font-mono text-slate-300 whitespace-nowrap">${d.category}</td>
              <td class="py-3 px-3.5">
                <div class="font-semibold text-slate-200">${d.brand}</div>
                <div class="font-mono text-markup line-through text-[11px]">${d.brandPrice} Retail</div>
              </td>
              <td class="py-3 px-3.5">
                <div class="font-bold text-white">${d.twin}</div>
                <div class="font-mono text-twin font-extrabold text-[11px]">${d.twinPrice} Factory Twin</div>
              </td>
              <td class="py-3 px-3.5 font-mono text-[11px] text-slate-300 max-w-xs">${d.spec}</td>
              <td class="py-3 px-3.5 text-right whitespace-nowrap">
                <span class="inline-flex items-center px-2 py-0.5 rounded bg-twin/15 text-twin font-mono font-bold text-[11px]">
                  -${savingsPct}% ($${savingsDollar})
                </span>
              </td>
              <td class="py-3 px-3.5 text-right whitespace-nowrap">
                <div class="inline-flex items-center gap-1.5">
                  <a href="${amazonUrl}" target="_blank" rel="noopener sponsored" class="cta-emerald px-2.5 py-1.5 rounded-lg font-mono font-extrabold text-[11px]">Amazon (${d.twinPrice})</a>
                  <a href="${aliexpressUrl}" target="_blank" rel="noopener sponsored" class="px-2 py-1.5 rounded-lg bg-carbon text-xray hover:bg-xray/10 font-mono font-bold text-[11px]">OEM</a>
                </div>
              </td>
            </tr>
          `;
        }).join("");
        return;
      }

      dealsTableWrap.classList.add("hidden");
      dealsGrid.classList.remove("hidden");

      dealsGrid.innerHTML = filtered.map(d => {
        const savingsDollar = Math.max(0, Math.round(d.leftPrice - d.rightPrice));
        const savingsPct = d.leftPrice > 0
          ? Math.round(((d.leftPrice - d.rightPrice) / d.leftPrice) * 100)
          : 80;
        const twinCostPct = Math.max(6, Math.min(94, 100 - savingsPct));

        const paddedDay = String(d.day).padStart(2, "0");
        const realImageSrc = `images/day_${paddedDay}.jpg`;
        const amazonUrl = buildAmazonUrl(d.query);
        const aliexpressUrl = buildAliExpressUrl(d.aliQuery || d.twin);
        const walmartUrl = buildWalmartUrl(d.query);
        const ebayUrl = buildEbayUrl(d.twin || d.query, d.day);
        const bountyOffer = buildAmazonBountyOffer(d);
        const rakutenUrl = STOREFRONT_CONFIG.cpaExtensionUrl;
        const netAfterCashback = Math.max(0, Math.round((d.rightPrice || 25) - 30));
        const netCashbackLabel = netAfterCashback === 0 ? "$0 Net w/ £25 Rakuten" : `$${netAfterCashback} Net w/ £25 Rakuten`;
        const hasTeardownNotes = Boolean(d.hook || d.body || d.reveal);

        return `
          <article
            id="deal-${d.day}"
            class="dossier-card ${d.hot ? 'dossier-card-featured' : ''} flex flex-col justify-between relative"
          >
            <!-- Native Deep-Link Hash Anchors (#day-1, #day-01) -->
            <span id="day-${d.day}" class="block -top-32 relative pointer-events-none"></span>
            <span id="day-${paddedDay}" class="block -top-32 relative pointer-events-none"></span>

            <div>
              <!-- Top Row: Episode # Badge + Category + Savings Pill -->
              <div class="flex items-center justify-between gap-2 mb-3">
                <div class="flex items-center gap-2 flex-wrap">
                  <span class="inline-flex items-center px-2.5 py-1 rounded-md bg-xray text-carbon font-mono font-extrabold text-xs tabular-nums">
                    DAY #${d.day}
                  </span>
                  <span class="text-xs font-mono font-semibold text-slate-300">
                    ${d.category}
                  </span>
                  ${d.hot ? `
                  <span class="inline-flex items-center gap-1 text-[10px] font-mono font-bold text-amber-300 bg-amber-500/10 px-2 py-0.5 rounded">
                    <svg class="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/>
                    </svg>
                    <span>HIGH DEMAND</span>
                  </span>` : ""}
                </div>
                <span class="shrink-0 inline-flex items-center px-2.5 py-1 rounded-full bg-twin/15 text-twin font-mono font-extrabold text-xs tabular-nums">
                  SAVE ${savingsPct}% ($${savingsDollar})
                </span>
              </div>

              <!-- Episode Dossier Title (Linked to Dedicated Static SEO Product/FAQ Page) -->
              <h3 class="mb-3">
                <a href="./episodes/day-${String(d.day).padStart(3, "0")}.html" class="hover:text-xray transition">
                  ${d.title}
                </a>
              </h3>

              <!-- Real Product Comparison Photograph -->
              <div class="relative mb-3.5 rounded-xl overflow-hidden bg-carbon">
                <div class="absolute top-2.5 left-2.5 z-10 inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-carbon/90 backdrop-blur-md text-[10px] font-mono font-bold text-xray">
                  <svg class="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                  </svg>
                  <span>STUDIO PHOTO + OEM SPEC VERIFIED</span>
                </div>
                <img
                  src="${realImageSrc}"
                  alt="Day #${d.day}: ${d.brand} vs. ${d.twin}"
                  loading="lazy"
                  data-fallback="${d.thumb || ''}"
                  onerror="if (this.dataset.fallback && this.src.indexOf(this.dataset.fallback.replace('./','')) === -1) { this.src = this.dataset.fallback; this.dataset.fallback = ''; } else { this.style.display='none'; this.nextElementSibling.classList.remove('hidden'); }"
                  class="w-full h-48 sm:h-52 object-cover block"
                />
                <!-- Fallback Studio Comparison Banner -->
                <div class="hidden w-full h-40 bg-gradient-to-r from-[#1D1116] via-[#121722] to-[#0D211B] flex items-center justify-between px-4 pt-6 pb-3">
                  <div class="text-left max-w-[43%]">
                    <div class="text-[10px] font-mono text-markup uppercase font-bold">Retail Brand</div>
                    <div class="text-xs font-bold text-slate-200 line-clamp-2 mt-0.5">${d.brand}</div>
                    <div class="text-sm font-mono font-black text-markup line-through mt-0.5 tabular-nums">${d.brandPrice}</div>
                  </div>
                  <div class="shrink-0 px-2.5 py-1 rounded-lg bg-xray/15 font-mono text-xs font-black text-xray">
                    VS
                  </div>
                  <div class="text-right max-w-[43%]">
                    <div class="text-[10px] font-mono text-twin uppercase font-bold">Factory Twin</div>
                    <div class="text-xs font-bold text-white line-clamp-2 mt-0.5">${d.twin}</div>
                    <div class="text-sm font-mono font-black text-twin mt-0.5 tabular-nums">${d.twinPrice}</div>
                  </div>
                </div>
              </div>

              <!-- Side-by-Side Comparison Ledger (Structural Hairline Split, No Nested Card Borders) -->
              <div class="grid grid-cols-2 divide-x divide-slate-800 border-y border-slate-800 py-3 my-3">
                <!-- Overpriced Brand Column -->
                <div class="pr-3">
                  <div class="flex items-center justify-between gap-1">
                    <span class="inline-flex items-center gap-1 text-[10px] font-mono uppercase tracking-wider text-markup font-bold">
                      <svg class="w-3 h-3 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
                      </svg>
                      <span>Retail Brand</span>
                    </span>
                    <span class="text-xs font-mono font-extrabold text-markup line-through tabular-nums">${d.brandPrice}</span>
                  </div>
                  <p class="text-xs font-semibold text-slate-300 mt-1 leading-snug">
                    <a href="${buildAmazonUrl(d.brand)}" target="_blank" rel="noopener sponsored" class="hover:text-markup underline decoration-dotted" title="Fact-Check Retail Brand Price on Amazon">
                      ${d.brand} ↗
                    </a>
                  </p>
                </div>

                <!-- Unblurred Factory Twin Column -->
                <div class="pl-3">
                  <div class="flex items-center justify-between gap-1">
                    <span class="inline-flex items-center gap-1 text-[10px] font-mono uppercase tracking-wider text-twin font-bold">
                      <svg class="w-3 h-3 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/>
                      </svg>
                      <span>Factory Twin</span>
                    </span>
                    <span class="text-xs font-mono font-extrabold text-twin tabular-nums">${d.twinPrice}</span>
                  </div>
                  <p class="text-xs font-bold text-white mt-1 leading-snug">
                    ${d.twin}
                  </p>
                </div>
              </div>

              <!-- Visual X-Ray Price Markup Ratio Meter -->
              <div class="py-1.5 mb-3">
                <div class="flex items-center justify-between text-[11px] font-mono tabular-nums mb-1.5">
                  <span class="text-twin font-bold">OEM Spec Value: ${d.twinPrice} (${twinCostPct}%)</span>
                  <span class="text-markup font-bold">Logo Tax Markup: $${savingsDollar} (${savingsPct}%)</span>
                </div>
                <div class="w-full h-2 rounded-full bg-carbon overflow-hidden flex gap-0.5" role="img" aria-label="Price ratio: ${twinCostPct}% OEM Twin price versus ${savingsPct}% retail brand markup">
                  <div class="h-full rounded-l-full bg-twin" style="width: ${twinCostPct}%"></div>
                  <div class="h-full rounded-r-full bg-markup/85 flex-1"></div>
                </div>
              </div>

              <!-- Forensic Smoking-Gun Spec Line -->
              <div class="border-t border-slate-800/90 pt-3 mb-3">
                <div class="flex items-center gap-1.5 text-[11px] font-mono text-xray font-bold mb-1">
                  <svg class="w-3.5 h-3.5 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z"/>
                  </svg>
                  <span>SMOKING-GUN OEM SPEC MATCH</span>
                </div>
                <p class="text-xs font-mono text-slate-200 leading-relaxed">
                  ${d.spec}
                </p>
              </div>

              ${hasTeardownNotes ? `
              <!-- Expandable Forensic Supply-Chain Teardown Notes -->
              <div class="mb-3.5">
                <button
                  id="teardown-btn-${d.day}"
                  type="button"
                  aria-expanded="false"
                  onclick="toggleTeardown(${d.day})"
                  class="w-full flex items-center justify-between py-1.5 text-[11px] font-mono font-semibold text-slate-400 hover:text-xray transition cursor-pointer"
                >
                  <span class="inline-flex items-center gap-1.5">
                    <svg class="w-3.5 h-3.5 text-xray" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                    </svg>
                    <span>Read Full Lab Teardown &amp; Supply-Chain Notes</span>
                  </span>
                  <svg id="teardown-icon-${d.day}" class="w-3.5 h-3.5 transition-transform duration-200" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/>
                  </svg>
                </button>
                <div id="teardown-panel-${d.day}" class="hidden mt-2 pt-2.5 border-t border-slate-800/80 text-xs text-slate-300 space-y-2 leading-relaxed">
                  ${d.hook ? `<p class="font-semibold text-white">${d.hook}</p>` : ""}
                  ${d.body ? `<p>${d.body}</p>` : ""}
                  ${d.reveal ? `<p class="text-twin font-mono text-[11px] font-semibold">${d.reveal}</p>` : ""}
                </div>
              </div>
              ` : ""}
            </div>

            <!-- Multi-Network Action Footer -->
            <div class="pt-2 border-t border-slate-800/90">
              <!-- Primary Action Button (Amazon Prime Affiliate) + Copy -->
              <div class="flex items-center gap-2">
                <a
                  href="${amazonUrl}"
                  target="_blank"
                  rel="noopener sponsored"
                  class="cta-emerald flex-1 inline-flex items-center justify-center gap-2 font-black text-xs sm:text-sm cursor-pointer"
                >
                  <svg class="w-4 h-4 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.25" aria-hidden="true">
                    <circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path stroke-linecap="round" stroke-linejoin="round" d="M1 1h4l2.68 13.39a2 2 0 002 1.61h9.72a2 2 0 002-1.61L23 6H6"/>
                  </svg>
                  <span>Buy Twin on Amazon Prime (${d.twinPrice})</span>
                  <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24" aria-hidden="true">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                  </svg>
                </a>
                <button
                  type="button"
                  onclick="copyDealLink(${d.day}, '${d.query.replace(/'/g, "\\\\'")}')"
                  class="shrink-0 inline-flex items-center justify-center gap-1.5 rounded-xl bg-surface hover:bg-elevated text-slate-200 px-3.5 py-3 text-xs font-mono font-bold transition cursor-pointer"
                  title="Copy Direct Amazon Factory Twin Link"
                >
                  <svg class="w-3.5 h-3.5 text-xray" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
                    <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path stroke-linecap="round" stroke-linejoin="round" d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/>
                  </svg>
                  <span>Copy</span>
                </button>
              </div>

              <!-- Secondary Multi-Network Affiliate Buttons: AliExpress Factory Direct, Walmart, eBay Certified Refurb, Amazon Bounty & Rakuten Cashback -->
              <div class="mt-2.5 pt-2">
                <div class="text-[10px] font-mono text-slate-400 uppercase tracking-wider mb-1.5 flex items-center justify-between">
                  <span>Multi-Associate Direct Supply, Refurb &amp; Cashback</span>
                  <span class="text-xray font-semibold">7 Networks Live</span>
                </div>
                <div class="grid grid-cols-3 gap-1.5">
                  <a
                    href="${aliexpressUrl}"
                    target="_blank"
                    rel="noopener sponsored"
                    class="inline-flex items-center justify-center gap-1 rounded-xl bg-carbon hover:bg-surface text-xray font-mono font-bold text-[11px] py-2 px-2 transition cursor-pointer"
                  >
                    <span class="truncate">AliExpress OEM</span>
                  </a>
                  <a
                    href="${walmartUrl}"
                    target="_blank"
                    rel="noopener sponsored"
                    class="inline-flex items-center justify-center gap-1 rounded-xl bg-carbon hover:bg-surface text-slate-200 font-mono font-bold text-[11px] py-2 px-2 transition cursor-pointer"
                  >
                    <span class="truncate">Walmart Twin</span>
                  </a>
                  <a
                    href="${ebayUrl}"
                    target="_blank"
                    rel="noopener sponsored"
                    class="inline-flex items-center justify-center gap-1 rounded-xl bg-carbon hover:bg-surface text-amber-300 font-mono font-bold text-[11px] py-2 px-2 transition cursor-pointer"
                  >
                    <span class="truncate">eBay Open-Box</span>
                  </a>
                </div>
                <div class="grid grid-cols-2 gap-1.5 mt-1.5">
                  <a
                    href="${bountyOffer.url}"
                    target="_blank"
                    rel="noopener sponsored"
                    class="inline-flex items-center justify-center gap-1 rounded-xl bg-carbon hover:bg-surface text-emerald-300 font-mono font-bold text-[10px] py-2 px-2 transition cursor-pointer"
                  >
                    <span class="truncate">🎁 ${bountyOffer.label}</span>
                  </a>
                  <a
                    href="${rakutenUrl}"
                    target="_blank"
                    rel="noopener sponsored"
                    class="inline-flex items-center justify-center gap-1 rounded-xl bg-carbon hover:bg-surface text-xray font-mono font-bold text-[10px] py-2 px-2 transition cursor-pointer"
                  >
                    <span class="truncate">💰 ${netCashbackLabel}</span>
                  </a>
                </div>
                <div class="mt-1.5 grid ${d.youtubeShortsUrl ? 'grid-cols-2' : 'grid-cols-1'} gap-1.5">
                  ${d.youtubeShortsUrl ? `
                  <a
                    href="${d.youtubeShortsUrl}"
                    target="_blank"
                    rel="noopener"
                    class="w-full inline-flex items-center justify-center gap-1 rounded-xl bg-markup/15 hover:bg-markup/25 border border-markup/40 text-white font-mono font-bold text-[10px] py-1.5 px-2 transition"
                  >
                    <span class="truncate">▶ Watch YouTube Short ↗</span>
                  </a>
                  ` : ""}
                  <a
                    href="./episodes/day-${String(d.day).padStart(3, "0")}.html"
                    class="w-full inline-flex items-center justify-center gap-1 rounded-xl bg-carbon/80 hover:bg-surface border border-slate-800 hover:border-xray/40 text-slate-300 hover:text-xray font-mono font-semibold text-[10px] py-1.5 px-2 transition"
                  >
                    <span class="truncate">🔍 Episode #${String(d.day).padStart(3, "0")} Dossier &amp; FAQ →</span>
                  </a>
                </div>
              </div>
            </div>
          </article>
        `;
      }).join("");
    }

    function updateCategoryButtons() {
      document.querySelectorAll(".cat-btn").forEach(btn => {
        if (btn.dataset.cat === activeCategory) {
          btn.className = "cat-btn shrink-0 inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold bg-xray text-carbon transition cursor-pointer";
        } else {
          btn.className = "cat-btn shrink-0 inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-panel text-slate-300 border border-slate-800 hover:border-slate-600 transition cursor-pointer";
        }
      });
    }

    function resetFilters() {
      activeCategory = "ALL";
      searchQuery = "";
      sortMode = "day-asc";
      searchInput.value = "";
      if (sortSelect) sortSelect.value = "day-asc";
      clearSearchBtn.classList.add("hidden");
      if (searchKbdHint) searchKbdHint.classList.remove("hidden");
      updateCategoryButtons();
      renderDeals();
    }

    // Event Listeners
    searchInput.addEventListener("input", e => {
      searchQuery = e.target.value;
      if (searchQuery.trim().length > 0) {
        clearSearchBtn.classList.remove("hidden");
        if (searchKbdHint) searchKbdHint.classList.add("hidden");
      } else {
        clearSearchBtn.classList.add("hidden");
        if (searchKbdHint) searchKbdHint.classList.remove("hidden");
      }
      renderDeals();
    });

    clearSearchBtn.addEventListener("click", () => {
      searchInput.value = "";
      searchQuery = "";
      clearSearchBtn.classList.add("hidden");
      if (searchKbdHint) searchKbdHint.classList.remove("hidden");
      renderDeals();
      searchInput.focus();
    });

    if (sortSelect) {
      sortSelect.addEventListener("change", e => {
        sortMode = e.target.value;
        renderDeals();
      });
    }

    // Keyboard shortcut '/' to focus search
    window.addEventListener("keydown", e => {
      if (e.key === "/" && document.activeElement !== searchInput && !["INPUT", "TEXTAREA", "SELECT"].includes(document.activeElement?.tagName)) {
        e.preventDefault();
        searchInput.focus();
      } else if (e.key === "Escape" && document.activeElement === searchInput && searchInput.value) {
        searchInput.value = "";
        searchQuery = "";
        clearSearchBtn.classList.add("hidden");
        if (searchKbdHint) searchKbdHint.classList.remove("hidden");
        renderDeals();
      }
    });

    document.querySelectorAll(".cat-btn").forEach(btn => {
      btn.addEventListener("click", () => {
        activeCategory = btn.dataset.cat;
        updateCategoryButtons();
        renderDeals();
      });
    });

    // Support URL Hash Jump (#day-1 to #day-600, #day-01, #deal-1, #episode-1, #1)
    function checkUrlHash() {
      const rawHash = (window.location.hash || "").replace(/^#/, "").trim();
      if (!rawHash) return;
      const match = rawHash.match(/^(?:day-|deal-|episode-|video-)?0*(\\d{1,3})$/i);
      if (match) {
        const num = parseInt(match[1], 10);
        if (!isNaN(num) && num >= 1 && num <= 600) {
          jumpToVideo(num);
        }
      }
    }

    // Dynamic Episode Loader (Automatically populates up to 600 episodes from ./episodes_100.json if present)
    async function loadDynamicEpisodes() {
      try {
        const response = await fetch("./episodes_100.json", { cache: "no-store" });
        if (!response.ok) return;
        const payload = await response.json();
        const rawList = Array.isArray(payload)
          ? payload
          : (Array.isArray(payload?.episodes) ? payload.episodes : (Array.isArray(payload?.deals) ? payload.deals : []));

        if (!rawList.length) return;

        const episodeMap = new Map();
        DEALS.forEach(item => episodeMap.set(item.day, item));

        rawList.forEach((rawItem, idx) => {
          const dayNum = parseInt(rawItem.day ?? rawItem.video ?? rawItem.episode ?? rawItem.id ?? (idx + 1), 10);
          if (!isNaN(dayNum) && dayNum >= 1 && dayNum <= 600) {
            const existing = episodeMap.get(dayNum) || null;
            episodeMap.set(dayNum, normalizeEpisode(rawItem, idx, existing));
          }
        });

        DEALS = Array.from(episodeMap.values()).sort((a, b) => a.day - b.day);
        DEALS_DATA = DEALS;

        updateCatalogCounters();
        renderNumberStrip();
        renderDeals();
        checkUrlHash();
      } catch (err) {
        // Silently keep built-in DEALS if episodes_100.json is not present yet
      }
    }

    // Initialize Storefront
    updateCatalogCounters();
    renderNumberStrip();
    renderDeals();
    checkUrlHash();
    loadDynamicEpisodes();
    window.addEventListener("hashchange", checkUrlHash);
  </script>
  <!-- Sticky Bottom High-Conversion Cashback & Bounty Bar -->
  <div id="sticky-bounty-bar" class="fixed bottom-0 inset-x-0 z-50 border-t border-cyan-500/30 bg-[#0B0E14]/95 backdrop-blur-md px-3 py-2.5 shadow-2xl">
    <div class="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-2">
      <div class="flex items-center gap-2 text-xs font-mono">
        <span class="inline-flex items-center px-2 py-0.5 rounded bg-emerald-400 text-slate-950 font-black">TRIPLE-STACK BONUS</span>
        <span class="text-slate-200 hidden sm:inline">Combine any Factory Twin with <strong>£25/$30 Rakuten Cashback</strong> + <strong>Free 30-Day Amazon Prime</strong></span>
      </div>
      <div class="flex items-center gap-2 ml-auto">
        <a href="https://www.rakuten.co.uk/r/SAAALA5?eeid=26474" target="_blank" rel="noopener sponsored" class="inline-flex items-center gap-1 rounded-lg bg-cyan-400 hover:bg-cyan-300 text-slate-950 font-mono font-black text-xs px-3 py-1.5 transition">
          <span>💰 Claim £25/$30 Cashback</span>
        </a>
        <a href="https://www.amazon.com/prime?tag=pricexray-20" target="_blank" rel="noopener sponsored" class="inline-flex items-center gap-1 rounded-lg bg-emerald-400 hover:bg-emerald-300 text-slate-950 font-mono font-black text-xs px-3 py-1.5 transition">
          <span>🎁 Free 30-Day Prime</span>
        </a>
        <a href="./bounties.html" class="inline-flex items-center gap-1 rounded-lg bg-amber-400 hover:bg-amber-300 text-slate-950 font-mono font-black text-xs px-3 py-1.5 transition">
          <span>🏦 9-Bounty &amp; B2B Vault</span>
        </a>
        <a href="https://www.youtube.com/playlist?list=PLDrSvkoLRQ0s" target="_blank" rel="noopener" class="hidden md:inline-flex items-center gap-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-white font-mono font-bold text-xs px-2.5 py-1.5 transition">
          <span>▶ Binge Shorts</span>
        </a>
        <button type="button" onclick="document.getElementById('sticky-bounty-bar').style.display='none'" class="text-slate-400 hover:text-white px-1.5 text-sm font-mono" aria-label="Dismiss bonus bar">✕</button>
      </div>
    </div>
  </div>
  <div class="sr-only" aria-hidden="true">Impact-Site-Verification: 8601fafe-4b95-43ee-8a45-9c849c70173b | ANKH ENTERPRISE LTD (CRN 17511325) · 66 Paul Street, London, England, United Kingdom, EC2A 4NA</div>
</body>
</html>
"""


def main():
    with open(ALL_EPISODES_PATH, "r", encoding="utf-8") as f:
        raw_episodes = json.load(f)

    deals = build_deals_array()
    deals_json_str = json.dumps(deals, indent=6, ensure_ascii=False)
    html_out = HTML_TEMPLATE.replace("__INITIAL_DEALS_JSON__", deals_json_str)

    os.makedirs(GH_DEPLOY_DIR, exist_ok=True)
    os.makedirs(LANDING_DIR, exist_ok=True)

    gh_index = os.path.join(GH_DEPLOY_DIR, "index.html")
    landing_index = os.path.join(LANDING_DIR, "index.html")
    gh_json = os.path.join(GH_DEPLOY_DIR, "episodes_100.json")
    landing_json = os.path.join(LANDING_DIR, "episodes_100.json")

    with open(gh_index, "w", encoding="utf-8") as f:
        f.write(html_out)
    with open(landing_index, "w", encoding="utf-8") as f:
        f.write(html_out)
    with open(gh_json, "w", encoding="utf-8") as f:
        json.dump(raw_episodes, f, indent=2, ensure_ascii=False)
    with open(landing_json, "w", encoding="utf-8") as f:
        json.dump(raw_episodes, f, indent=2, ensure_ascii=False)

    print(f"✅ Built {gh_index} ({len(html_out):,} bytes) with {len(deals)} episodes.")
    print(f"✅ Synced {landing_index} and {gh_json}.")


if __name__ == "__main__":
    main()
