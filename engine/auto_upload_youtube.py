#!/usr/bin/env python3
"""
Price X-Ray (@PriceXRayOfficial) — Automated 100-Video YouTube Shorts Scheduler & Multi-Affiliate Updater (YouTube Data API v3)
Automatically sets up Channel Banner & Video Watermark, uploads and schedules Day_01 through Day_100 MP4 videos
(supporting 4x/day scheduling at 01:00, 07:00, 13:00, 19:00 UTC), re-uploads custom thumbnails, and populates
multi-network affiliate descriptions & top-level comments (Amazon Associates + AliExpress Factory Direct + 100-Item Storefront).

Usage:
  .venv/bin/python engine/auto_upload_youtube.py --update-existing-links
  .venv/bin/python engine/auto_upload_youtube.py --schedule-4x-daily --max-uploads 6
  .venv/bin/python engine/auto_upload_youtube.py --reupload-thumbnails
  .venv/bin/python engine/auto_upload_youtube.py --next-batch
"""
import argparse
import datetime
import glob
import json
import os
import re
import sys
import urllib.parse

BASE_DIR = os.environ.get(
    "PRICEXRAY_BASE_DIR",
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
)
CALENDAR_CANDIDATES = [
    os.path.join(BASE_DIR, "calendar_30days", "all_100_episodes.json"),
    os.path.join(BASE_DIR, "calendar_100days", "all_100_days.json"),
    os.path.join(BASE_DIR, "calendar_30days", "all_100_days.json"),
    os.path.join(BASE_DIR, "calendar_30days", "all_30_days.json"),
]
PACKS_DIRS = [
    os.path.join(BASE_DIR, "upload_ready_100_days"),
    os.path.join(BASE_DIR, "upload_ready_30_days"),
]
VIDEOS_DIR = os.path.join(BASE_DIR, "videos")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
CLIENT_SECRETS = os.path.join(BASE_DIR, "client_secrets.json")
TOKEN_FILE = os.path.join(BASE_DIR, "youtube_token.json")
UPLOADED_LOG = os.path.join(BASE_DIR, "uploaded_videos.json")
LIVE_STOREFRONT_URL = "https://saaalahy93-a11y.github.io/price-xray-storefront/"
AMAZON_TAG = "pricexray-20"
AMAZON_UK_TAG = "pricexray-21"
GBP_FX_RATE = 0.79
LAUNCH_DATE_UTC = datetime.datetime(2026, 11, 9, 15, 0, 0, tzinfo=datetime.timezone.utc)
# 1x/Day Global Buyer-Overlap Window (UTC):
#   15:00 UTC = 10:00 AM EST / 7:00 AM PST / 3:00 PM GMT / 4:00 PM CET
#   Gives every Short a full 24-hour algorithmic wave and 100 consecutive days of authority.
BUYER_PEAK_3X_HOURS_UTC = [15]
DAILY_4X_HOURS_UTC = BUYER_PEAK_3X_HOURS_UTC


def load_all_calendar_days():
    """Loads up to 100 episodes across calendar_100days / calendar_30days JSON files."""
    all_days = {}
    for path in reversed(CALENDAR_CANDIDATES):
        if os.path.exists(path):
            with open(path) as f:
                data = json.load(f)
                for item in data:
                    if isinstance(item, dict) and "day" in item:
                        all_days[int(item["day"])] = item
    for folder in ["calendar_30days", "calendar_100days"]:
        folder_path = os.path.join(BASE_DIR, folder)
        if os.path.isdir(folder_path):
            for jf in sorted(glob.glob(os.path.join(folder_path, "days_*.json"))):
                try:
                    with open(jf) as f:
                        data = json.load(f)
                        for item in data:
                            if isinstance(item, dict) and "day" in item:
                                all_days[int(item["day"])] = item
                except Exception:
                    pass
    return all_days


def resolve_mp4_path(day_num):
    for pdir in PACKS_DIRS:
        for fmt in [f"Day_{day_num:02d}", f"Day_{day_num:03d}"]:
            candidate = os.path.join(pdir, fmt, f"{fmt}_PriceXRay_Short.mp4")
            if os.path.exists(candidate):
                return candidate
    for fmt in [f"Day_{day_num:02d}", f"Day_{day_num:03d}"]:
        candidate = os.path.join(VIDEOS_DIR, f"{fmt}_PriceXRay_Short.mp4")
        if os.path.exists(candidate):
            return candidate
    return os.path.join(BASE_DIR, "upload_ready_30_days", f"Day_{day_num:02d}", f"Day_{day_num:02d}_PriceXRay_Short.mp4")


def resolve_thumbnail_path(day_num):
    for pdir in PACKS_DIRS:
        for fmt in [f"Day_{day_num:02d}", f"Day_{day_num:03d}"]:
            candidate = os.path.join(pdir, fmt, f"{fmt}_Thumbnail.png")
            if os.path.exists(candidate):
                return candidate
    for fmt in [f"Day_{day_num:02d}", f"Day_{day_num:03d}"]:
        candidate = os.path.join(VIDEOS_DIR, f"{fmt}_Thumbnail.png")
        if os.path.exists(candidate):
            return candidate
    return os.path.join(BASE_DIR, "upload_ready_30_days", f"Day_{day_num:02d}", f"Day_{day_num:02d}_Thumbnail.png")


def build_amazon_affiliate_url(item):
    raw_query = item.get("amazon_search_query") or item.get("right_twin") or item.get("title", "Factory Twin")
    query = urllib.parse.quote_plus(raw_query)
    return f"https://www.amazon.com/s?k={query}&tag={AMAZON_TAG}"


def build_amazon_uk_affiliate_url(item):
    if item.get("amazon_uk_affiliate_url") and AMAZON_UK_TAG in str(item.get("amazon_uk_affiliate_url")):
        return item["amazon_uk_affiliate_url"]
    raw_query = item.get("amazon_search_query") or item.get("right_twin") or item.get("title", "Factory Twin")
    query = urllib.parse.quote_plus(raw_query)
    return f"https://www.amazon.co.uk/s?k={query}&tag={AMAZON_UK_TAG}"


def build_ebay_uk_epn_url(item):
    if item.get("ebay_uk_epn_url"):
        return item["ebay_uk_epn_url"]
    day_num = int(item.get("day", 1))
    raw_query = item.get("right_twin") or item.get("amazon_search_query") or item.get("title", "Factory Twin")
    cleaned = re.sub(r"\(.*?\)", "", raw_query).strip()
    query = urllib.parse.quote_plus(cleaned)
    return f"https://www.ebay.co.uk/sch/i.html?_nkw={query}&mkcid=1&mkrid=710-53481-19255-0&campid=5339000000&customid=pricexray-uk-day-{day_num:03d}"


def usd_to_gbp_text(text: str) -> str:
    """Converts $X or $X,XXX values in a string to £Y GBP equivalents (~0.79 FX rate)."""
    def _repl(m):
        raw_num = m.group(1).replace(",", "")
        try:
            val = float(raw_num)
            gbp = max(1, int(round(val * GBP_FX_RATE)))
            return f"£{gbp:,}"
        except Exception:
            return m.group(0)
    return re.sub(r"\$([0-9,]+(?:\.[0-9]+)?)", _repl, text or "")


def build_aliexpress_wholesale_url(item):
    if item.get("aliexpress_wholesale_url") and "_c3Z2E4OR" in str(item.get("aliexpress_wholesale_url")):
        return item["aliexpress_wholesale_url"]
    raw_query = (
        item.get("aliexpress_search_query")
        or item.get("amazon_search_query")
        or item.get("right_twin")
        or item.get("title", "Factory Twin")
    )
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", raw_query).strip("-")
    return f"https://www.aliexpress.com/w/wholesale-{slug}.html?aff_fsk=_c3Z2E4OR&aff_platform=portals-tool&sk=_c3Z2E4OR&tt=CPS_NORMAL"


def build_walmart_affiliate_url(item):
    raw_query = item.get("amazon_search_query") or item.get("right_twin") or item.get("title", "Factory Twin")
    query = urllib.parse.quote_plus(raw_query)
    return f"https://www.walmart.com/search?q={query}"


def build_ebay_epn_url(item):
    if item.get("ebay_epn_url"):
        return item["ebay_epn_url"]
    day_num = int(item.get("day", 1))
    raw_query = item.get("right_twin") or item.get("amazon_search_query") or item.get("title", "Factory Twin")
    cleaned = re.sub(r"\(.*?\)", "", raw_query).strip()
    query = urllib.parse.quote_plus(cleaned)
    return f"https://www.ebay.com/sch/i.html?_nkw={query}&mkcid=1&mkrid=711-53200-19255-0&campid=5339000000&customid=pricexray-day-{day_num:03d}"


FLAGSHIP_PLAYLIST_ID = "PLDrSvkoLRQ0s"
FLAGSHIP_PLAYLIST_URL = f"https://www.youtube.com/playlist?list={FLAGSHIP_PLAYLIST_ID}"

NAMED_BRAND_TITLES_1_TO_10 = {
    1: "$230 Ray-Ban Frames vs. $24 Mazzucchelli Acetate Factory Twin #Shorts #PriceXRay",
    2: "$50 Stanley/Yeti Tumbler vs. $19 304-Steel Vacuum Factory Twin #Shorts #PriceXRay",
    3: "$429 Dyson Supersonic vs. $69 Laifen 110K RPM Factory Twin #Shorts #PriceXRay",
    4: "$1,600 Herman Miller Chair vs. $149 BIFMA Class-4 Mesh Twin #Shorts #PriceXRay",
    5: "$70 Twelve South Stand vs. $16 6061-T6 Aluminum Factory Twin #Shorts #PriceXRay",
    6: "$140 Belkin MagSafe Stand vs. $22 WPC Qi2 15W Factory Twin #Shorts #PriceXRay",
    7: "$129 Apple Thunderbolt 4 Cable vs. $19 Intel-Certified Twin #Shorts #PriceXRay",
    8: "$299 Sony/Bose ANC Earbuds vs. $55 Qualcomm -50dB Hybrid Twin #Shorts #PriceXRay",
    9: "$230 Razer Gaming Keyboard vs. $49 AULA F75 Gasket Twin #Shorts #PriceXRay",
    10: "$189 BenQ ScreenBar vs. $34 Quntis Ra95+ Optical Light Twin #Shorts #PriceXRay",
}


def sanitize_yt_text(text: str) -> str:
    """YouTube Data API v3 rejects raw '<' and '>' characters in titles and descriptions."""
    return (text or "").replace("<", "≤").replace(">", "≥")


def parse_dollar_amount(val: str) -> float:
    cleaned = re.sub(r"[^0-9.]", "", str(val or ""))
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def compute_savings_display(item: dict) -> tuple[str, str, int]:
    """Returns (dollar_saved_str, pct_saved_str, pct_int) with zero empty strings."""
    lp = parse_dollar_amount(item.get("left_price", ""))
    rp = parse_dollar_amount(item.get("right_price", ""))
    if lp > rp > 0:
        diff = int(round(lp - rp))
        pct = int(round(((lp - rp) / lp) * 100))
        return f"${diff:,}", f"{pct}% OFF", pct
    raw_sav = str(item.get("savings") or "").strip()
    if raw_sav:
        return raw_sav, "80% OFF", 80
    return "$150+", "80% OFF", 80


def extract_clean_entities(raw_name: str) -> list[str]:
    """Splits compound brand/model strings ('Sony WF-1000XM5 / Bose QC Ultra (Black)') into atomic search entities."""
    if not raw_name:
        return []
    no_paren = re.sub(r"\(.*?\)", "", raw_name)
    parts = [p.strip() for p in re.split(r"\s*/\s*|\s+\+\s+", no_paren) if p.strip()]
    entities = []
    for p in parts:
        cleaned = re.sub(
            r"\s+(Acetate Frames|Frames|Hair Dryer|Mesh Chair|Designer.*|Retail.*|Big-Box.*|High-Speed.*|Full Elastomeric.*)$",
            "",
            p,
            flags=re.I,
        ).strip()
        if cleaned and cleaned not in entities:
            entities.append(cleaned)
        first_two = " ".join(cleaned.split()[:2]).strip()
        if first_two and len(first_two) >= 3 and first_two not in entities:
            entities.append(first_two)
    return entities


def build_algorithmic_title(item: dict, day_num: int = None) -> str:
    """
    Constructs a high-CTR, brand-entity-anchored title (<=100 chars) engineered for
    YouTube Search + Shorts Feed + Entity Co-Visitation Graph.
    """
    if day_num is None:
        day_num = int(item.get("day", 1))
    if day_num in NAMED_BRAND_TITLES_1_TO_10:
        return sanitize_yt_text(NAMED_BRAND_TITLES_1_TO_10[day_num])[:100]
    if item.get("youtube_title"):
        return sanitize_yt_text(str(item["youtube_title"]))[:100]

    base_title = re.sub(r"\s*#shorts\b", "", item.get("title", ""), flags=re.I).strip()
    base_title = re.sub(r"\s*#pricexray\b", "", base_title, flags=re.I).strip()
    brand_entities = extract_clean_entities(item.get("left_brand", ""))
    primary_brand = brand_entities[0] if brand_entities else ""

    if primary_brand and primary_brand.split()[0].lower() not in base_title.lower():
        candidate = f"{primary_brand}: {base_title}"
        if len(candidate) + 19 <= 100:
            base_title = candidate

    suffix = " #Shorts #PriceXRay"
    max_base = 100 - len(suffix)
    if len(base_title) > max_base:
        base_title = base_title[:max_base].rsplit(" ", 1)[0].rstrip(" ,;-+/(.")
    return sanitize_yt_text(f"{base_title}{suffix}")[:100]


def infer_niche_hashtags(item: dict) -> str:
    text = f"{item.get('category', '')} {item.get('title', '')} {item.get('left_brand', '')}".lower()
    if re.search(r"audio|earbud|headphone|speaker|cable|charger|magsafe|qi2|keyboard|mouse|usb|tech|monitor", text):
        return "#TechHacks #GadgetReview #DeskSetup"
    if re.search(r"chair|tool|wrench|ratchet|garage|car|stand|ergonomic|flashlight", text):
        return "#WorkspaceSetup #ToolTok #HomeOffice"
    if re.search(r"hair|skin|serum|shave|toothbrush|massage|beauty|grooming", text):
        return "#BeautyHacks #GroomingHacks #SelfCare"
    if re.search(r"sunglass|frames|watch|bag|luggage|cooler|jacket|edc|eyewear", text):
        return "#StyleHacks #MensFashion #EDC"
    return "#KitchenHacks #HomeEssentials #SmartShopping"


def build_buyer_seo_tags(item: dict) -> list[str]:
    """
    Generates a surgical 20-24 tag matrix (strictly <= 475 chars total) combining:
      1. Atomic Retail Brand & Model Entities (for YouTube Entity Co-Visitation)
      2. Atomic OEM Factory Twin Entities
      3. High-Intent Buyer Search Queries ('[Brand] vs [Twin]', '[Brand] alternative', 'is [Brand] worth it', '[Brand] dupe')
      4. Channel Cohort Anchors ('Price X-Ray', 'Factory Twin', 'Same Factory', 'Shorts')
    """
    left_entities = extract_clean_entities(sanitize_yt_text(item.get("left_brand", "")))
    right_entities = extract_clean_entities(sanitize_yt_text(item.get("right_twin", "")))
    primary_left = left_entities[0] if left_entities else "Designer Brand"
    primary_right = right_entities[0] if right_entities else "Factory Twin"

    candidate_tags = []
    # Tier 1: Atomic Brand & Twin Entities
    candidate_tags.extend(left_entities[:2])
    candidate_tags.extend(right_entities[:2])
    # Tier 2: High-Intent Comparison & Alternative Queries
    candidate_tags.extend([
        f"{primary_left} vs {primary_right}",
        f"{primary_left} alternative",
        f"{primary_left} dupe",
        f"is {primary_left} worth it",
        f"{primary_right} review",
        f"{primary_left} review",
        f"best {primary_left} alternative",
    ])
    # Tier 3: Episode-Specific Seed Tags (filtered to short, high-velocity phrases <= 32 chars)
    for t in item.get("youtube_tags", []):
        if len(str(t)) <= 32:
            candidate_tags.append(str(t))
    # Tier 4: Channel Algorithmic Cohort Anchors (Trains YouTube to cluster all Price X-Ray uploads)
    candidate_tags.extend([
        "Price X-Ray",
        "PriceXRay",
        "Factory Twin",
        "Same Factory",
        "OEM Products",
        "Amazon Finds",
        "Dupes vs Originals",
        "Smart Shopping",
        "Brand Markup",
        "Shorts",
    ])

    seen = set()
    final_tags = []
    total_chars = 0
    for t in candidate_tags:
        t_clean = re.sub(r"[^\w\s\-\+\&]", "", str(t)).strip()
        if not t_clean or len(t_clean) > 42 or t_clean.lower() in seen:
            continue
        if total_chars + len(t_clean) + 3 > 465:
            break
        seen.add(t_clean.lower())
        final_tags.append(t_clean)
        total_chars += len(t_clean) + 3
    return final_tags


def build_description(item, day_num=None):
    if day_num is None:
        day_num = int(item["day"])
    day_num = int(day_num)
    seo_episode_link = f"{LIVE_STOREFRONT_URL}episodes/day-{day_num:03d}.html"
    storefront_link = f"{LIVE_STOREFRONT_URL}#day-{day_num}"
    next_day = 1 if day_num >= 600 else day_num + 1
    prev_day = 600 if day_num <= 1 else day_num - 1
    next_episode_link = f"{LIVE_STOREFRONT_URL}episodes/day-{next_day:03d}.html"
    prev_episode_link = f"{LIVE_STOREFRONT_URL}episodes/day-{prev_day:03d}.html"
    amazon_link = build_amazon_affiliate_url(item)
    amazon_uk_link = build_amazon_uk_affiliate_url(item)
    aliexpress_link = build_aliexpress_wholesale_url(item)
    walmart_link = build_walmart_affiliate_url(item)
    ebay_link = build_ebay_epn_url(item)
    ebay_uk_link = build_ebay_uk_epn_url(item)
    left_brand = item.get("left_brand", "Retail Brand")
    left_price = item.get("left_price", "$300")
    right_twin = item.get("right_twin", "Factory Twin")
    right_price = item.get("right_price", "$20")
    left_price_gbp = usd_to_gbp_text(str(left_price))
    right_price_gbp = usd_to_gbp_text(str(right_price))
    dollar_saved, pct_saved, _ = compute_savings_display(item)
    gbp_saved = usd_to_gbp_text(str(dollar_saved))
    niche_tags = infer_niche_hashtags(item)
    bounty_obj = item.get("amazon_bounty") or {}
    bounty_url = bounty_obj.get("bounty_url") or f"https://www.amazon.com/prime?tag={AMAZON_TAG}"
    bounty_uk_url = bounty_obj.get("bounty_uk_url") or f"https://www.amazon.co.uk/prime?tag={AMAZON_UK_TAG}"
    bounty_cta = bounty_obj.get("buyer_cta") or "30-Day Free Amazon Prime Trial (Free Same-Day Shipping)"
    net_cashback = item.get("net_price_after_cashback") or "Stack £25 / $30 Rakuten Cashback Bonus"

    raw = (
        f"👇 UNLOCK THE {right_price} / {right_price_gbp} TWIN (SAVE {dollar_saved} / {gbp_saved} • {pct_saved}): {seo_episode_link}\n"
        f"🇺🇸 US Amazon Prime ({right_twin}): {amazon_link}\n"
        f"🇬🇧 UK Amazon.co.uk Prime ({right_twin}): {amazon_uk_link}\n\n"
        f"{left_brand} ({left_price} / {left_price_gbp}) vs. {right_twin} ({right_price} / {right_price_gbp}) — Save {dollar_saved} / {gbp_saved} ({pct_saved})! "
        f"{item.get('hook_0_to_4s', '')}\n\n"
        f"⚡ UNLOCK THE UNBLURRED FACTORY TWIN ({right_twin} — {right_price} / {right_price_gbp} | {net_cashback}):\n"
        f"🌐 Dedicated Episode Dossier (US/UK/CA/DE/AU Geo-Router): {seo_episode_link}\n"
        f"🇺🇸 Amazon.com Prime (US Next-Day): {amazon_link}\n"
        f"🇬🇧 Amazon.co.uk Prime (UK Next-Day Delivery): {amazon_uk_link}\n"
        f"🎁 US Free Trial / Buyer Bonus ({bounty_cta}): {bounty_url}\n"
        f"🎁 UK Free 30-Day Amazon.co.uk Prime Trial: {bounty_uk_url}\n"
        f"🏭 AliExpress / Factory-Direct OEM Wholesale (US & UK Direct): {aliexpress_link}\n"
        f"🏬 Walmart Price-Match & Retail Twin: {walmart_link}\n"
        f"📦 eBay US Open-Box: {ebay_link} | 🇬🇧 eBay.co.uk Open-Box: {ebay_uk_link}\n"
        f"💰 £25 UK / $30 US Rakuten Cashback Bonus (Code SAAALA5): https://www.rakuten.co.uk/r/SAAALA5?eeid=26474\n"
        f"📂 Full 600-Item Factory Twin Dossier (Episode #{day_num:03d}): {storefront_link}\n\n"
        f"🔬 FORENSIC SUPPLY-CHAIN BREAKDOWN ({left_brand} vs. {right_twin}):\n"
        f"• Smoking Gun Spec: {item.get('smoking_gun_spec', '')}\n"
        f"• Retail Brand Price: {left_brand} — {left_price} ({left_price_gbp} RRP)\n"
        f"• Same-Factory OEM Twin: {right_twin} — {right_price} ({right_price_gbp}) (You Save {dollar_saved} / {gbp_saved} • {pct_saved})\n\n"
        f"⏱️ VIDEO CHAPTERS & FORENSIC TIMELINE:\n"
        f"0:00 {left_brand} ({left_price} / {left_price_gbp}) vs. {right_twin} ({right_price} / {right_price_gbp}) Price Hook\n"
        f"0:05 OEM Supply-Chain & Internal Spec Teardown\n"
        f"0:24 Unblurred Factory Twin Price Reveal ({right_price} / {right_price_gbp})\n"
        f"0:33 Where to Get the Verified Factory Twin (US & UK Links)\n\n"
        f"▶️ BINGE THE NEXT PRICE X-RAY TEARDOWNS (OFFICIAL SERIES):\n"
        f"⏭️ Next Teardown (Episode #{next_day:03d}): {next_episode_link}\n"
        f"⏮️ Previous Teardown (Episode #{prev_day:03d}): {prev_episode_link}\n"
        f"📺 Full Series Playlist: {FLAGSHIP_PLAYLIST_URL}\n"
        f"🔥 Episode #01 ($230 / £180 Ray-Ban vs $24 / £19 Mazzucchelli Twin): https://youtube.com/shorts/dXFV2ovYQts\n\n"
        f"🔎 High-Intent Buyer Topics: {left_brand} vs {right_twin}, is {left_brand} worth it, "
        f"best {left_brand} alternative 2026 UK & US, {right_twin} review, {left_brand} dupe, same factory OEM products.\n\n"
        f"#Shorts #PriceXRay #FactoryTwin #AmazonFinds #UKDeals #SmartShopping {niche_tags}\n\n"
        f"FTC & UK ASA Disclosure: Operated by ANKH ENTERPRISE LTD (CRN 17511325, 66 Paul Street, London, EC2A 4NA). As an Amazon Associate (US Store ID: {AMAZON_TAG} | UK Store ID: {AMAZON_UK_TAG}), eBay Partner (8158522), Walmart/Impact & AliExpress (_c3Z2E4OR) affiliate partner, Price X-Ray earns from qualifying purchases at zero additional cost to you."
    )
    return sanitize_yt_text(raw)[:4950]


def build_pinned_comment(item, day_num=None):
    if day_num is None:
        day_num = int(item["day"])
    day_num = int(day_num)
    seo_episode_link = f"{LIVE_STOREFRONT_URL}episodes/day-{day_num:03d}.html"
    storefront_link = f"{LIVE_STOREFRONT_URL}#day-{day_num}"
    next_day = 1 if day_num >= 600 else day_num + 1
    next_episode_link = f"{LIVE_STOREFRONT_URL}episodes/day-{next_day:03d}.html"
    amazon_link = build_amazon_affiliate_url(item)
    amazon_uk_link = build_amazon_uk_affiliate_url(item)
    aliexpress_link = build_aliexpress_wholesale_url(item)
    walmart_link = build_walmart_affiliate_url(item)
    ebay_link = build_ebay_epn_url(item)
    ebay_uk_link = build_ebay_uk_epn_url(item)
    left_entities = extract_clean_entities(item.get("left_brand", "Retail Brand"))
    short_left = left_entities[0] if left_entities else item.get("left_brand", "Retail Brand")
    left_price = item.get("left_price", "$300")
    right_twin = item.get("right_twin", "Factory Twin")
    right_price = item.get("right_price", "$20")
    left_price_gbp = usd_to_gbp_text(str(left_price))
    right_price_gbp = usd_to_gbp_text(str(right_price))
    dollar_saved, pct_saved, _ = compute_savings_display(item)
    gbp_saved = usd_to_gbp_text(str(dollar_saved))
    bounty_obj = item.get("amazon_bounty") or {}
    bounty_url = bounty_obj.get("bounty_url") or f"https://www.amazon.com/prime?tag={AMAZON_TAG}"
    bounty_uk_url = bounty_obj.get("bounty_uk_url") or f"https://www.amazon.co.uk/prime?tag={AMAZON_UK_TAG}"
    bounty_cta = bounty_obj.get("buyer_cta") or "30-Day Free Amazon Prime Trial"

    return (
        f"🔓 UNBLURRED EPISODE #{day_num:03d} LINK ({right_twin} — {right_price} / {right_price_gbp} | Save {dollar_saved} / {gbp_saved} • {pct_saved}):\n"
        f"👉 Instant Region-Matched Deal Page (US/UK/CA/DE/AU): {seo_episode_link}\n"
        f"🇺🇸 US Amazon Prime Direct Link: {amazon_link}\n"
        f"🇬🇧 UK Amazon.co.uk Prime Direct Link: {amazon_uk_link}\n"
        f"🎁 Free Prime Trial (🇺🇸 US: {bounty_url} | 🇬🇧 UK: {bounty_uk_url})\n"
        f"🏭 Factory-Direct / AliExpress Wholesale: {aliexpress_link}\n"
        f"🏬 Walmart Price-Match Link: {walmart_link}\n"
        f"📦 eBay Open-Box (🇺🇸 US: {ebay_link} | 🇬🇧 UK: {ebay_uk_link})\n"
        f"💰 £25 UK / $30 US Rakuten Cashback Bonus (Code SAAALA5): https://www.rakuten.co.uk/r/SAAALA5?eeid=26474\n"
        f"⏭️ Next Teardown (Episode #{next_day:03d}): {next_episode_link}\n"
        f"📂 All 600 Unblurred Factory Twins Index: {storefront_link}\n"
        f"▶️ Watch Every Price X-Ray (Full Playlist): {FLAGSHIP_PLAYLIST_URL}\n\n"
        f"👀 QUICK POLL: Would you still pay {left_price} ({left_price_gbp}) for the {short_left} logo, or are you pocketing the {dollar_saved} ({gbp_saved} / {pct_saved}) with the {right_price} ({right_price_gbp}) Factory Twin? Reply 'TWIN' or 'BRAND' below! 👇 (#ad)"
    )


def generate_srt_caption(item: dict, day_num: int = None) -> str:
    """
    Generates a timed SubRip (.srt) closed-caption transcript for an episode and saves it to disk.
    Uploading verified captions sets contentDetails.caption='true' on YouTube and feeds exact
    brand/model/spec tokens directly into YouTube Search & Shorts NLP indexing.
    """
    if day_num is None:
        day_num = int(item.get("day", 1))
    left_brand = item.get("left_brand", "Retail Brand")
    left_price = item.get("left_price", "$300")
    right_twin = item.get("right_twin", "Factory Twin")
    right_price = item.get("right_price", "$20")
    dollar_saved, pct_saved, _ = compute_savings_display(item)
    hook = item.get("hook_0_to_4s", f"{left_brand} costs {left_price}, while the same-factory OEM twin costs {right_price}.")
    body = item.get("body_4_to_24s", f"Forensic spec check: {item.get('smoking_gun_spec', '')}.")
    reveal = item.get("reveal_24_to_32s", f"The unblurred Factory Twin is {right_twin} for {right_price}, saving you {dollar_saved} ({pct_saved}).")
    cta = item.get(
        "cta_32_to_42s",
        f"Grab the verified {right_twin} link in the description, pinned comment, or the Price X-Ray channel bio, and subscribe for daily Factory Twin teardowns.",
    )

    srt_content = (
        f"1\n00:00:00,000 --> 00:00:04,500\n{hook}\n\n"
        f"2\n00:00:04,500 --> 00:00:15,000\n{body}\n\n"
        f"3\n00:00:15,000 --> 00:00:24,000\nForensic Spec Match: {left_brand} ({left_price}) vs. {right_twin} ({right_price}) — {item.get('smoking_gun_spec', '')}.\n\n"
        f"4\n00:00:24,000 --> 00:00:33,000\n{reveal}\n\n"
        f"5\n00:00:33,000 --> 00:00:45,000\n{cta}\n"
    )
    out_dir = os.path.join(BASE_DIR, "upload_ready_30_days", f"Day_{day_num:02d}")
    os.makedirs(out_dir, exist_ok=True)
    srt_path = os.path.join(out_dir, f"Day_{day_num:02d}_Captions.srt")
    with open(srt_path, "w", encoding="utf-8") as f:
        f.write(srt_content)
    return srt_path


def upload_video_captions(youtube, video_id: str, item: dict, day_num: int = None):
    """Uploads or updates the verified English (en-US) SRT caption track on a YouTube video."""
    from googleapiclient.http import MediaFileUpload

    if day_num is None:
        day_num = int(item.get("day", 1))
    srt_path = generate_srt_caption(item, day_num)
    try:
        existing = youtube.captions().list(part="id,snippet", videoId=video_id).execute().get("items", [])
        en_caps = [
            c
            for c in existing
            if c["snippet"].get("language", "").lower().startswith("en")
            and c["snippet"].get("trackKind", "").lower() != "asr"
        ]
        media = MediaFileUpload(srt_path, mimetype="application/x-subrip", resumable=False)
        if en_caps:
            cap_id = en_caps[0]["id"]
            youtube.captions().update(
                part="snippet",
                body={"id": cap_id, "snippet": {"isDraft": False}},
                media_body=media,
            ).execute()
            print(f"✓ Updated verified en-US SRT Closed Captions on Day {day_num:02d} ({video_id})", flush=True)
        else:
            youtube.captions().insert(
                part="snippet",
                body={
                    "snippet": {
                        "videoId": video_id,
                        "language": "en-US",
                        "name": "English (Forensic Spec Transcript)",
                        "isDraft": False,
                    }
                },
                media_body=media,
            ).execute()
            print(f"✓ Uploaded verified en-US SRT Closed Captions on Day {day_num:02d} ({video_id})", flush=True)
    except Exception as e:
        print(f"⚠ Note on caption upload for Day {day_num:02d} ({video_id}): {e}", flush=True)


def build_tier1_localizations(title: str, description: str) -> dict:
    """Populates localized metadata across top Tier-1 English buyer markets (US, UK, CA, AU, Global).
    For en-GB (United Kingdom), converts $ prices to £ GBP in the title and surfaces amazon.co.uk (pricexray-21) first.
    """
    loc_entry = {"title": title, "description": description}
    gb_title = sanitize_yt_text(usd_to_gbp_text(title))[:100]
    gb_desc = description.replace(
        f"www.amazon.com/s?", f"www.amazon.co.uk/s?"
    ).replace(f"tag={AMAZON_TAG}", f"tag={AMAZON_UK_TAG}")
    return {
        "en": loc_entry,
        "en-US": loc_entry,
        "en-GB": {"title": gb_title, "description": gb_desc[:4950]},
        "en-CA": loc_entry,
        "en-AU": loc_entry,
    }


# Backwards-compatible aliases
def build_video_description(item):
    return build_description(item, item.get("day"))


def build_comment_text(item):
    return build_pinned_comment(item, item.get("day"))


def get_authenticated_service():
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

    scopes = [
        "https://www.googleapis.com/auth/youtube",
        "https://www.googleapis.com/auth/youtube.upload",
        "https://www.googleapis.com/auth/youtube.force-ssl",
    ]
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, scopes)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS, scopes)
            print("Opening browser for Google OAuth consent (select the 'Price X-Ray' channel when prompted)...", flush=True)
            creds = flow.run_local_server(port=8765, open_browser=True)
        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())
    return build("youtube", "v3", credentials=creds)


def setup_channel_branding(youtube, upload_banner=True):
    from googleapiclient.http import MediaFileUpload

    ch_resp = youtube.channels().list(part="id,snippet,brandingSettings", mine=True).execute()
    items = ch_resp.get("items", [])
    if not items:
        print("⚠ No YouTube channel found for the authenticated account.", flush=True)
        return None
    ch = items[0]
    channel_id = ch["id"]
    channel_title = ch["snippet"]["title"]
    print(f"✓ Authenticated as YouTube Channel: {channel_title} ({channel_id})", flush=True)

    banner_path = os.path.join(ASSETS_DIR, "channel_banner.png")
    if upload_banner and os.path.exists(banner_path):
        try:
            print("Uploading channel_banner.png via channelBanners.insert...", flush=True)
            media = MediaFileUpload(banner_path, mimetype="image/png", chunksize=-1, resumable=True)
            banner_resp = youtube.channelBanners().insert(media_body=media).execute()
            banner_url = banner_resp.get("url")
            if banner_url:
                branding = ch.get("brandingSettings", {})
                branding.setdefault("image", {})["bannerExternalUrl"] = banner_url
                ch_cfg = branding.setdefault("channel", {})
                ch_cfg["description"] = (
                    "Same Factory. Same Specs. 80% Less. We X-Ray $300+ retail brands to expose their $20 same-factory OEM twins.\n\n"
                    f"👇 UNLOCK ALL 100 UNBLURRED FACTORY TWIN LINKS (Amazon Prime + Factory-Direct Wholesale):\n{LIVE_STOREFRONT_URL}\n\n"
                    "Big brands rarely own factories. They hire Tier-1 Original Design Manufacturers (ODMs), stamp a $250 logo onto an existing chassis, and charge a 400%–850% retail markup.\n\n"
                    "At Price X-Ray (@PriceXRayOfficial), our forensic supply-chain lab verifies:\n"
                    "• FCC-ID, UL & WPC Qi2 Regulatory Filings\n"
                    "• Internal Teardowns (Brushless Motors, PCBs, 304/316 Steel, Mazzucchelli Acetate)\n"
                    "• Side-by-Side Bill-of-Materials & Price Breakdowns\n"
                    "• Direct Amazon Prime & Factory-Direct OEM Twin Links\n\n"
                    "📅 New 45-Second Price X-Rays Posted Daily!\n\n"
                    f"FTC & Amazon Associates Disclosure: As an Amazon Associate (Store ID: {AMAZON_TAG}) and affiliate partner, Price X-Ray earns from qualifying purchases at zero extra cost to you."
                )
                ch_cfg["keywords"] = (
                    "\"price xray\" \"factory twin\" \"OEM products\" \"same factory\" \"brand markup\" "
                    "\"amazon finds\" \"tech teardown\" \"smart shopping\" \"dupes vs originals\" "
                    "\"dyson alternative\" \"ray ban alternative\" \"herman miller alternative\" "
                    "\"apple alternative\" \"consumer advocacy\""
                )
                ch_cfg["defaultLanguage"] = "en-US"
                ch_cfg["country"] = "US"
                ch_cfg["unsubscribedTrailer"] = "dXFV2ovYQts"
                ch_cfg["showRelatedChannels"] = True
                ch_cfg["showBrowseView"] = True
                youtube.channels().update(
                    part="brandingSettings",
                    body={
                        "id": channel_id,
                        "brandingSettings": branding,
                    },
                ).execute()
                try:
                    ch_localizations = build_tier1_localizations(channel_title, ch_cfg["description"])
                    youtube.channels().update(
                        part="localizations",
                        body={
                            "id": channel_id,
                            "localizations": ch_localizations,
                        },
                    ).execute()
                except Exception:
                    pass
                print("✓ Channel Banner, SEO Description, Keywords, Localizations & Trailer updated live via YouTube Data API v3!", flush=True)
        except Exception as e:
            print(f"⚠ Note on Banner API update: {e}", flush=True)

    wm_path = os.path.join(ASSETS_DIR, "channel_watermark.png")
    if os.path.exists(wm_path):
        try:
            wm_media = MediaFileUpload(wm_path, mimetype="image/png", resumable=False)
            youtube.watermarks().set(
                channelId=channel_id,
                body={
                    "timing": {"type": "offsetFromStart", "offsetMs": 0},
                    "position": {"type": "corner", "cornerPosition": "bottomRight"},
                },
                media_body=wm_media,
            ).execute()
            print("✓ Channel In-Video Subscribe Watermark updated live!", flush=True)
        except ValueError:
            # httplib2 204 No Content response means watermark succeeded
            print("✓ Channel In-Video Subscribe Watermark updated live (204 OK)!", flush=True)
        except Exception as e:
            print(f"⚠ Note on Watermark API update: {e}", flush=True)

    return channel_id


def post_affiliate_comment(youtube, video_id, item):
    day_num = item["day"]
    comment_text = build_pinned_comment(item, day_num)
    try:
        youtube.commentThreads().insert(
            part="snippet",
            body={
                "snippet": {
                    "videoId": video_id,
                    "topLevelComment": {"snippet": {"textOriginal": comment_text}},
                }
            },
        ).execute()
        print(
            f"✓ Posted Multi-Affiliate Comment (Amazon + AliExpress Wholesale + 100-Item Storefront) on Day {day_num:02d} ({video_id})!",
            flush=True,
        )
    except Exception as e:
        print(f"⚠ Note on comment post for Day {day_num:02d}: {e}", flush=True)


def load_uploaded_log():
    if os.path.exists(UPLOADED_LOG):
        with open(UPLOADED_LOG) as f:
            return json.load(f)
    return {}


def save_uploaded_log(data):
    with open(UPLOADED_LOG, "w") as f:
        json.dump(data, f, indent=2)
    cal_path = os.path.join(BASE_DIR, "calendar_30days", "all_100_episodes.json")
    if os.path.exists(cal_path):
        try:
            with open(cal_path, "r", encoding="utf-8") as cf:
                eps = json.load(cf)
            updated_cal = False
            for ep in eps:
                d_str = str(ep.get("day", ""))
                if d_str in data and data[d_str].get("video_id"):
                    vid = data[d_str]["video_id"]
                    url = data[d_str].get("url", f"https://youtube.com/shorts/{vid}")
                    st = data[d_str].get("status", "SCHEDULED")
                    if ep.get("youtube_video_id") != vid or ep.get("youtube_publish_status") != st:
                        ep["youtube_video_id"] = vid
                        ep["youtube_shorts_url"] = url
                        ep["youtube_publish_status"] = st
                        updated_cal = True
            if updated_cal:
                with open(cal_path, "w", encoding="utf-8") as cf:
                    json.dump(eps, cf, indent=2, ensure_ascii=False)
        except Exception:
            pass


def sync_newly_published_comments(youtube, all_days):
    """
    Checks if any previously SCHEDULED videos have passed their publish_at UTC timestamp
    (meaning they are now PUBLIC LIVE on YouTube) and automatically posts their
    Interactive Poll + Multi-Affiliate Pinned Comment.
    """
    uploaded = load_uploaded_log()
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    changed = False
    for day_str, info in sorted(uploaded.items(), key=lambda kv: int(kv[0])):
        day_num = int(day_str)
        if info.get("comment_posted"):
            continue
        pub_str = info.get("publish_at")
        is_live = info.get("status") == "PUBLIC_LIVE"
        if pub_str and not is_live:
            try:
                pub_dt = datetime.datetime.fromisoformat(pub_str.replace("Z", "+00:00"))
                if pub_dt <= now_utc:
                    is_live = True
                    info["status"] = "PUBLIC_LIVE"
                    changed = True
            except Exception:
                pass
        if is_live and day_num in all_days:
            post_affiliate_comment(youtube, info["video_id"], all_days[day_num])
            info["comment_posted"] = True
            changed = True
    if changed:
        save_uploaded_log(uploaded)


def ensure_launch_cluster_and_above_fold_links(youtube, all_days):
    """
    Eliminates the Day-1 'Single-Video Dead-End' by ensuring the initial 4-Vertical Flagship
    Launch Cluster (Days 01..04: Ray-Ban Eyewear, Stanley/Yeti EDC, Dyson Hair/Beauty,
    Herman Miller Workspace) is PUBLIC_LIVE with Above-the-Fold Line-1 Click Magnet descriptions
    and Pinned Comments. Costs only 50 quota units per video updated once.
    """
    uploaded = load_uploaded_log()
    changed = False
    for day_num in [1, 2, 3, 4]:
        day_str = str(day_num)
        if day_str not in uploaded or day_num not in all_days:
            continue
        info = uploaded[day_str]
        if info.get("launch_cluster_v2_synced"):
            continue
        video_id = info["video_id"]
        item = all_days[day_num]
        title = build_algorithmic_title(item, day_num)
        description = build_description(item, day_num)
        tags = build_buyer_seo_tags(item)
        try:
            youtube.videos().update(
                part="snippet,status,localizations",
                body={
                    "id": video_id,
                    "snippet": {
                        "title": title,
                        "description": description,
                        "tags": tags,
                        "categoryId": "28",
                        "defaultLanguage": "en-US",
                        "defaultAudioLanguage": "en-US",
                    },
                    "status": {
                        "privacyStatus": "public",
                        "selfDeclaredMadeForKids": False,
                    },
                    "localizations": build_tier1_localizations(title, description),
                },
            ).execute()
            info["status"] = "PUBLIC_LIVE"
            info.pop("publish_at", None)
            info["title"] = title
            info["launch_cluster_v2_synced"] = True
            changed = True
            print(f"✓ Promoted Day {day_num:02d} ({video_id}) into 4-Vertical PUBLIC Launch Cluster + Line-1 Click Magnet!", flush=True)
            if not info.get("comment_posted"):
                post_affiliate_comment(youtube, video_id, item)
                info["comment_posted"] = True
        except Exception as e:
            if "quotaExceeded" in str(e):
                break
            print(f"⚠ Note on launch cluster sync for Day {day_num:02d}: {e}", flush=True)
    if changed:
        save_uploaded_log(uploaded)


def update_existing_video_links(youtube, all_days):
    uploaded = load_uploaded_log()
    for day_str, info in sorted(uploaded.items(), key=lambda kv: int(kv[0])):
        day_num = int(day_str)
        if day_num not in all_days:
            print(f"⚠ Day {day_num:02d} not found in calendar data, skipping.", flush=True)
            continue
        video_id = info["video_id"]
        item = all_days[day_num]
        title = build_algorithmic_title(item, day_num)
        description = build_description(item, day_num)
        tags = build_buyer_seo_tags(item)
        try:
            youtube.videos().update(
                part="snippet,localizations",
                body={
                    "id": video_id,
                    "snippet": {
                        "title": title,
                        "description": description,
                        "tags": tags,
                        "categoryId": "28",
                        "defaultLanguage": "en-US",
                        "defaultAudioLanguage": "en-US",
                    },
                    "localizations": build_tier1_localizations(title, description),
                },
            ).execute()
        except Exception as e:
            if "quotaExceeded" in str(e):
                print(f"⏸ Reached daily YouTube API quota at Day {day_num:02d}; saving progress.", flush=True)
                break
            raise
        info["title"] = title
        info["amazon_affiliate_link"] = build_amazon_affiliate_url(item)
        info["aliexpress_wholesale_link"] = build_aliexpress_wholesale_url(item)
        info["walmart_affiliate_link"] = build_walmart_affiliate_url(item)
        info["ebay_epn_link"] = build_ebay_epn_url(item)
        info["storefront_link"] = f"{LIVE_STOREFRONT_URL}#day-{day_num}"
        info["algorithmic_seo_synced"] = True
        print(
            f"✓ Algorithmically Optimized Day {day_num:02d} ({video_id}): '{title}' ({len(tags)} tags + 4-Network Associate Links)",
            flush=True,
        )
        if info.get("status") == "PUBLIC_LIVE":
            post_affiliate_comment(youtube, video_id, item)
    save_uploaded_log(uploaded)


def reupload_thumbnails(youtube, all_days):
    from googleapiclient.http import MediaFileUpload

    uploaded = load_uploaded_log()
    if not uploaded:
        print("⚠ No uploaded videos found in uploaded_videos.json.", flush=True)
        return

    for day_str, info in sorted(uploaded.items(), key=lambda kv: int(kv[0])):
        day_num = int(day_str)
        video_id = info["video_id"]
        thumb_path = resolve_thumbnail_path(day_num)
        if os.path.exists(thumb_path):
            try:
                media = MediaFileUpload(thumb_path, mimetype="image/png", chunksize=-1, resumable=False)
                youtube.thumbnails().set(videoId=video_id, media_body=media).execute()
                info["thumbnail_path"] = thumb_path
                info["thumbnail_synced"] = True
                print(f"✓ Uploaded custom thumbnail via thumbnails.set for Day {day_num:02d} ({video_id})", flush=True)
                continue
            except Exception as e:
                print(f"⚠ thumbnails.set note for Day {day_num:02d} ({video_id}): {e} — syncing snippet metadata instead...", flush=True)
        if day_num in all_days:
            item = all_days[day_num]
            title = build_algorithmic_title(item, day_num)
            description = build_description(item, day_num)
            youtube.videos().update(
                part="snippet,localizations",
                body={
                    "id": video_id,
                    "snippet": {
                        "title": title,
                        "description": description,
                        "tags": build_buyer_seo_tags(item),
                        "categoryId": "28",
                        "defaultLanguage": "en-US",
                        "defaultAudioLanguage": "en-US",
                    },
                    "localizations": build_tier1_localizations(title, description),
                },
            ).execute()
            info["title"] = title
            info["thumbnail_path"] = thumb_path
            info["metadata_synced"] = True
            print(f"✓ Synced snippet metadata for Day {day_num:02d} ({video_id})", flush=True)
    save_uploaded_log(uploaded)


def realign_existing_scheduled_videos(youtube, all_days):
    """
    Re-aligns all already-uploaded SCHEDULED videos (Days 02..N) into consecutive
    Buyer-Peak slots starting from the next upcoming slot, so there are zero schedule gaps.
    """
    uploaded = load_uploaded_log()
    scheduled_days = [
        int(k)
        for k, v in uploaded.items()
        if v.get("status") == "SCHEDULED" or v.get("publish_at")
    ]
    scheduled_days.sort()
    if not scheduled_days:
        print("⚠ No scheduled videos found to realign.", flush=True)
        return

    now_utc = datetime.datetime.now(datetime.timezone.utc)
    start_date = max(LAUNCH_DATE_UTC.date() + datetime.timedelta(days=1), now_utc.date() + datetime.timedelta(days=1))
    slots = []
    day_offset = 0
    while len(slots) < len(scheduled_days):
        cur_date = start_date + datetime.timedelta(days=day_offset)
        for hr in BUYER_PEAK_3X_HOURS_UTC:
            slot_dt = datetime.datetime(cur_date.year, cur_date.month, cur_date.day, hr, 0, 0, tzinfo=datetime.timezone.utc)
            if slot_dt <= now_utc:
                continue
            slots.append(slot_dt.isoformat().replace("+00:00", "Z"))
            if len(slots) >= len(scheduled_days):
                break
        day_offset += 1

    for day_num, slot_iso in zip(scheduled_days, slots):
        info = uploaded[str(day_num)]
        video_id = info["video_id"]
        item = all_days.get(day_num, {})
        title = build_algorithmic_title(item, day_num) if item else sanitize_yt_text(info.get("title", ""))[:100]
        description = build_description(item, day_num) if item else ""
        youtube.videos().update(
            part="snippet,status,localizations",
            body={
                "id": video_id,
                "snippet": {
                    "title": title,
                    "description": description,
                    "tags": build_buyer_seo_tags(item) if item else ["PriceXRay", "FactoryTwin", "Shorts"],
                    "categoryId": "28",
                    "defaultLanguage": "en-US",
                    "defaultAudioLanguage": "en-US",
                },
                "status": {
                    "privacyStatus": "private",
                    "publishAt": slot_iso,
                    "selfDeclaredMadeForKids": False,
                },
                "localizations": build_tier1_localizations(title, description),
            },
        ).execute()
        info["publish_at"] = slot_iso
        info["status"] = "SCHEDULED"
        info["title"] = title
        if item:
            info["amazon_affiliate_link"] = build_amazon_affiliate_url(item)
            info["aliexpress_wholesale_link"] = build_aliexpress_wholesale_url(item)
            info["storefront_link"] = f"{LIVE_STOREFRONT_URL}#day-{day_num}"
        print(f"✓ Realigned Day {day_num:02d} ({video_id}) -> Buyer-Peak Slot {slot_iso}", flush=True)

    save_uploaded_log(uploaded)


def generate_next_4x_daily_slots(uploaded, count):
    """
    Generates `count` chronological UTC publishAt ISO timestamps at the Global Buyer-Peak
    windows, picking up cleanly after the last scheduled slot.
    """
    used_slots = set()
    latest_dt = None
    for info in uploaded.values():
        pub = info.get("publish_at")
        if pub:
            used_slots.add(pub)
            try:
                dt = datetime.datetime.fromisoformat(pub.replace("Z", "+00:00"))
                if latest_dt is None or dt > latest_dt:
                    latest_dt = dt
            except Exception:
                pass

    now_utc = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=30)
    base_date = now_utc.date()
    if latest_dt is not None:
        base_date = max(base_date, latest_dt.date())

    slots = []
    day_offset = 0
    while len(slots) < count:
        cur_date = base_date + datetime.timedelta(days=day_offset)
        for hr in BUYER_PEAK_3X_HOURS_UTC:
            slot_dt = datetime.datetime(cur_date.year, cur_date.month, cur_date.day, hr, 0, 0, tzinfo=datetime.timezone.utc)
            if slot_dt <= now_utc:
                continue
            if latest_dt is not None and slot_dt <= latest_dt:
                continue
            iso_str = slot_dt.isoformat().replace("+00:00", "Z")
            if iso_str not in used_slots:
                slots.append(iso_str)
                used_slots.add(iso_str)
                if len(slots) >= count:
                    break
        day_offset += 1
    return slots


def upload_day(youtube, item, publish_at_iso=None, post_comment=False, set_thumbnail=False):
    from googleapiclient.http import MediaFileUpload

    day_num = item["day"]
    mp4_path = resolve_mp4_path(day_num)
    if not os.path.exists(mp4_path):
        print(f"⚠ MP4 file not found for Day {day_num:02d} at {mp4_path}, skipping upload.", flush=True)
        return None

    title = build_algorithmic_title(item, day_num)
    description = build_description(item, day_num)

    status_dict = {
        "selfDeclaredMadeForKids": False,
        "embeddable": True,
        "publicStatsViewable": True,
    }
    if publish_at_iso:
        status_dict["privacyStatus"] = "private"
        status_dict["publishAt"] = publish_at_iso
    else:
        status_dict["privacyStatus"] = "public"

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": build_buyer_seo_tags(item),
            "categoryId": "28",
            "defaultLanguage": "en-US",
            "defaultAudioLanguage": "en-US",
        },
        "status": status_dict,
        "localizations": build_tier1_localizations(title, description),
    }

    print(f"Uploading Day {day_num:02d}: {title}...", flush=True)
    media = MediaFileUpload(mp4_path, chunksize=-1, resumable=True, mimetype="video/mp4")
    req = youtube.videos().insert(part="snippet,status,localizations", body=body, media_body=media)
    resp = req.execute()
    video_id = resp["id"]
    status_label = f"SCHEDULED ({publish_at_iso})" if publish_at_iso else "PUBLIC LIVE"
    print(f"✓ Uploaded Day {day_num:02d} [{status_label}] -> https://youtube.com/shorts/{video_id}", flush=True)

    # Generate local SRT caption file (0 API quota units)
    generate_srt_caption(item, day_num)

    # Automatically link into the Flagship Series Playlist for session-chaining (50 quota units)
    try:
        youtube.playlistItems().insert(
            part="snippet",
            body={
                "snippet": {
                    "playlistId": FLAGSHIP_PLAYLIST_ID,
                    "resourceId": {"kind": "youtube#video", "videoId": video_id},
                }
            },
        ).execute()
        print(f"✓ Linked Day {day_num:02d} ({video_id}) into Flagship Playlist ({FLAGSHIP_PLAYLIST_ID})", flush=True)
    except Exception as e:
        print(f"⚠ Note on playlist link for Day {day_num:02d}: {e}", flush=True)

    if set_thumbnail:
        thumb_path = resolve_thumbnail_path(day_num)
        if os.path.exists(thumb_path):
            try:
                thumb_media = MediaFileUpload(thumb_path, mimetype="image/png", chunksize=-1, resumable=False)
                youtube.thumbnails().set(videoId=video_id, media_body=thumb_media).execute()
                print(f"✓ Custom thumbnail set for Day {day_num:02d} ({video_id})", flush=True)
            except Exception as e:
                print(f"⚠ Note on thumbnail upload for Day {day_num:02d}: {e}", flush=True)

    log_data = load_uploaded_log()
    entry = {
        "video_id": video_id,
        "url": f"https://youtube.com/shorts/{video_id}",
        "status": "SCHEDULED" if publish_at_iso else "PUBLIC_LIVE",
        "title": title,
        "amazon_affiliate_link": build_amazon_affiliate_url(item),
        "aliexpress_wholesale_link": build_aliexpress_wholesale_url(item),
        "storefront_link": f"{LIVE_STOREFRONT_URL}#day-{day_num}",
    }
    if publish_at_iso:
        entry["publish_at"] = publish_at_iso
    log_data[str(day_num)] = entry
    save_uploaded_log(log_data)

    if post_comment and not publish_at_iso:
        post_affiliate_comment(youtube, video_id, item)

    return video_id


def main():
    parser = argparse.ArgumentParser(
        description="Price X-Ray (@PriceXRayOfficial) 100-Video YouTube Auto-Scheduler & Multi-Affiliate Link Updater"
    )
    parser.add_argument("--days", type=int, nargs="*", default=[])
    parser.add_argument(
        "--schedule",
        action="store_true",
        help="Schedule each specified Day N on (launch_date + N - 1 days) at 15:00 UTC",
    )
    parser.add_argument(
        "--schedule-after-first",
        action="store_true",
        help="Publish the first specified video immediately as PUBLIC, and schedule the rest 1 per day at 15:00 UTC",
    )
    parser.add_argument(
        "--next-batch",
        action="store_true",
        help="Automatically upload & schedule the next batch of unuploaded days (1/day at 15:00 UTC)",
    )
    parser.add_argument(
        "--schedule-4x-daily",
        action="store_true",
        help="Schedule 4 videos per day (01:00, 07:00, 13:00, 19:00 UTC) across the 100-video library, picking up from the last uploaded episode",
    )
    parser.add_argument(
        "--max-uploads",
        type=int,
        default=6,
        help="Maximum number of videos to upload in a single run to respect daily YouTube API quota (default: 6)",
    )
    parser.add_argument("--setup-branding", action="store_true", help="Upload Channel Banner & Description via API")
    parser.add_argument(
        "--update-existing-links",
        action="store_true",
        help="Update all already-uploaded videos with Amazon Prime + AliExpress Factory-Direct + 100-Item Storefront links",
    )
    parser.add_argument(
        "--reupload-thumbnails",
        action="store_true",
        help="Upload custom thumbnails via thumbnails.set (or sync snippet metadata) for all uploaded videos in uploaded_videos.json",
    )
    parser.add_argument(
        "--realign-existing-schedule",
        action="store_true",
        help="Re-align all already-uploaded scheduled videos into consecutive 3x/Day Global Buyer-Peak slots (00:00, 13:00, 18:00 UTC)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview the 3x/day buyer-peak schedule and multi-affiliate metadata without calling the YouTube API",
    )
    args = parser.parse_args()

    all_days = load_all_calendar_days()
    if not all_days:
        print("⚠ No calendar days found!", flush=True)
        sys.exit(1)

    if args.dry_run:
        uploaded = load_uploaded_log()
        max_day = max(max(all_days.keys()), 600)
        remaining = [d for d in range(1, max_day + 1) if str(d) not in uploaded and d in all_days]
        batch = remaining[: args.max_uploads]
        slots = generate_next_4x_daily_slots(uploaded, len(batch))
        print(f"=== DRY RUN: 3x/Day Buyer-Peak Scheduler (Loaded {len(all_days)} episodes, {len(uploaded)} already uploaded) ===")
        for d, slot in zip(batch, slots):
            print(f"  Episode #{d:02d} -> {slot} | {all_days[d]['title']}")
        return

    if not os.path.exists(CLIENT_SECRETS):
        print("NOTE: To auto-upload via API, save your Google OAuth Desktop JSON to:")
        print(f"  {CLIENT_SECRETS}")
        sys.exit(0)

    yt = get_authenticated_service()

    # Always check if any scheduled videos have recently flipped to PUBLIC LIVE and post their engagement comment
    sync_newly_published_comments(yt, all_days)
    ensure_launch_cluster_and_above_fold_links(yt, all_days)

    if args.setup_branding:
        setup_channel_branding(yt, upload_banner=True)

    if args.realign_existing_schedule:
        realign_existing_scheduled_videos(yt, all_days)

    if args.update_existing_links:
        update_existing_video_links(yt, all_days)

    if args.reupload_thumbnails:
        reupload_thumbnails(yt, all_days)

    target_days = list(args.days)
    schedule_mode = args.schedule

    if args.schedule_4x_daily:
        uploaded = load_uploaded_log()
        max_day = max(max(all_days.keys()), 600)
        remaining = [d for d in range(1, max_day + 1) if str(d) not in uploaded and d in all_days]
        target_days = remaining[: args.max_uploads]
        if not target_days:
            print("🎉 All available episodes in the 100-video library are already uploaded and scheduled!", flush=True)
            return
        slots = generate_next_4x_daily_slots(uploaded, len(target_days))
        for d, pub_iso in zip(target_days, slots):
            try:
                upload_day(yt, all_days[d], publish_at_iso=pub_iso, post_comment=False)
            except Exception as e:
                err_str = str(e)
                if "uploadLimitExceeded" in err_str or "quotaExceeded" in err_str:
                    print(
                        f"⏸ Reached YouTube 24h rolling upload limit at Day {d:02d}. "
                        f"Progress saved in uploaded_videos.json; next scheduled run will resume from Day {d:02d}.",
                        flush=True,
                    )
                    break
                raise
        return

    if args.next_batch:
        uploaded = load_uploaded_log()
        max_day = max(max(all_days.keys()), 600)
        remaining = [d for d in range(1, max_day + 1) if str(d) not in uploaded and d in all_days]
        target_days = remaining[: args.max_uploads]
        schedule_mode = True
        if not target_days:
            print("🎉 All available episodes are already uploaded and scheduled!", flush=True)
            return

    for idx, d in enumerate(target_days):
        pub_iso = None
        if schedule_mode:
            pub_dt = LAUNCH_DATE_UTC + datetime.timedelta(days=max(1, d - 1))
            pub_iso = pub_dt.isoformat().replace("+00:00", "Z")
        elif args.schedule_after_first and idx > 0:
            pub_dt = LAUNCH_DATE_UTC + datetime.timedelta(days=idx)
            pub_iso = pub_dt.isoformat().replace("+00:00", "Z")

        upload_day(yt, all_days[d], pub_iso, post_comment=(pub_iso is None))


if __name__ == "__main__":
    main()
