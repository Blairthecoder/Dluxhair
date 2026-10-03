#!/usr/bin/env python3
"""Static site generator for the Dlux Beauty website.

Run:  python3 tools/build.py
Writes every page into public/ (Netlify's publish directory). Shared header,
footer, schema, sitemap and robots.txt all come from the settings below, so a
change here (phone, hours, booking link, domain) updates every page.
"""
import html
import json
import os
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUBLIC = os.path.join(ROOT, "public")

# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------
# Swap to the live domain once it is connected in Netlify (canonicals, sitemap,
# schema and Open Graph URLs all use this).
SITE_URL = "https://dlux-hair-salon.netlify.app"

# Keep False until the custom domain is live and placeholder content (About,
# Reviews, photos) is replaced. True removes the sitewide noindex.
INDEXABLE = False

# Acuity Scheduling link. Empty = Book pages fall back to call/text.
BOOKING_URL = ""

LASTMOD = date(2026, 10, 3).isoformat()

BIZ = {
    "name": "Dlux Beauty",
    "alt_name": "Dlux Hair",
    "tagline": "Hair Studio",
    "owner": "Denise",
    "phone": "512-810-4307",
    "phone_e164": "+15128104307",
    "email": "dluxbeauty@yahoo.com",
    "street": "Murphy Rd",
    "city": "Stafford",
    "region": "TX",
    "country": "US",
    "instagram": "Dlux Hair",
    "instagram_url": "",  # add the profile URL when confirmed
    "hours": [
        ("Monday – Friday", "9:00 AM – 9:00 PM", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], "09:00", "21:00"),
        ("Saturday", "7:00 AM – 5:00 PM", ["Saturday"], "07:00", "17:00"),
        ("Sunday", "7:00 AM – 5:00 PM", ["Sunday"], "07:00", "17:00"),
    ],
    "payments": ["Apple Pay", "Cash App", "Cash", "Card", "Zelle"],
}
LOCATION_TEXT = f"{BIZ['street']}, {BIZ['city']}, {BIZ['region']}"

# ---------------------------------------------------------------------------
# Photos (cropped from the Acuity booking page; replace with full-size originals)
# ---------------------------------------------------------------------------
PHOTOS = {
    "tape-ins-silk-press": ("Tape-in extensions with a silk press", (163, 318), "hair-extensions"),
    "traditional-sew-in": ("Traditional sew-in with loose curls", (189, 209), "hair-extensions"),
    "frontal-install": ("Lace frontal install, curled bob", (170, 258), "hair-extensions"),
    "closure-install": ("Closure sew-in install with body waves", (189, 210), "hair-extensions"),
    "360-frontal-install": ("360 lace frontal install, sleek straight", (188, 243), "hair-extensions"),
    "glueless-frontal-install": ("Glueless frontal install, red curls", (189, 247), "hair-extensions"),
    "glueless-closure-install": ("Glueless closure install, straight bob", (189, 243), "hair-extensions"),
    "frontal-ponytail": ("Frontal ponytail with bangs", (188, 243), "hair-extensions"),
    "wig-install": ("Curly wig install", (189, 212), "hair-extensions"),
    "partial-pixie-sew-in": ("Partial pixie sew-in", (189, 213), "hair-extensions"),
    "27-piece-pixie": ("27-piece pixie, glueless", (188, 225), "hair-extensions"),
    "refresh-styling": ("Refresh styling with curls", (189, 264), "hair-extensions"),
    "closure-frontal-touch-up": ("Closure install touch-up", (161, 270), "hair-extensions"),
    "silk-press": ("Silk press on natural hair", (233, 327), "silk-press"),
    "thermal-iron": ("Thermal iron style on short natural hair", (238, 234), "silk-press"),
    "color-application": ("Red color application with style", (236, 230), "natural-hair"),
    "relaxer": ("Relaxer with short tapered style", (238, 248), "natural-hair"),
    "comb-twist": ("Comb twist", (238, 278), "natural-hair"),
    "dread-twist-color": ("Dread twist with style and color", (199, 314), "natural-hair"),
    "mens-braids": ("Men's braids", (205, 264), "mens-braids"),
}


def img(key, cls="", eager=False, alt=None):
    caption, (w, h), _ = PHOTOS[key]
    a = alt or f"{caption} by Dlux Beauty in Stafford, TX"
    load = 'fetchpriority="high"' if eager else 'loading="lazy" decoding="async"'
    c = f' class="{cls}"' if cls else ""
    return f'<img src="/assets/img/work/{key}.jpg" alt="{esc(a)}" width="{w}" height="{h}" {load}{c}>'


def ph(label, sub="Photo needed"):
    return f'<div class="ph" role="img" aria-label="{esc(label)} photo coming soon"><b>{esc(label)}</b>{esc(sub)}</div>'


# ---------------------------------------------------------------------------
# Service menu (from the Dlux Beauty Acuity booking page, Oct 2026)
# (name, minutes, price, note)
# ---------------------------------------------------------------------------
BRAIDS = [
    ("Small Knotless", 300, 300, ""),
    ("Small/Medium Knotless", 300, 250, ""),
    ("Medium Knotless", 240, 230, ""),
    ("Large Knotless", 200, 220, ""),
    ("Jumbo Knotless", 120, 210, ""),
    ("Boho Knotless Small", 300, 350, "Hair not provided. Basic colors only."),
    ("Boho Knotless Medium", 240, 275, "Hair not provided. Basic colors only."),
    ("Boho Bob Knotless", 240, 225, "Hair not provided. Basic colors only."),
    ("Half Styled Half Knotless", 250, 225, ""),
    ("Knotless Touch-Up (Top/Back)", 180, 125, ""),
    ("Miracle Knots", 300, 250, "Hair not provided. 4-bag minimum. Human hair add-on available, natural colors only."),
    ("Freestyle Braids", 200, 220, ""),
    ("2 Feed-In Braid Style", 120, 100, ""),
    ("Layered Feed-In Braids", 300, 275, ""),
    ("Large Braided Ponytail", 200, 200, ""),
    ("Medium Braided Ponytail", 225, 230, ""),
    ("Fashion Twist Bob", 300, 250, ""),
    ("Soft Locs", 300, 350, ""),
    ("Crochet Pre-Loop", 180, 200, ""),
    ("Crochet Individuals", 120, 225, "Hair not provided."),
    ("Braid Take Down & Shampoo", 60, 125, "Detangle, exfoliate, cleanse and blow out."),
]
EXT_INSTALLS = [
    ("Traditional Sew-In", 200, 180, ""),
    ("Half & Half Sew-In Install", 200, 200, ""),
    ("Flip Method Sew-In Install", 225, 225, ""),
    ("Partial Pixie Sew-In Install", 120, 150, ""),
    ("Closure Install", 200, 190, ""),
    ("Frontal Install", 200, 225, ""),
    ("360 Frontal Install", 250, 250, ""),
    ("Wig Install", 120, 180, ""),
    ("Tape-Ins with Silk Press", 300, 600, ""),
    ("Hair Enhancements (Tracks)", 150, 100, ""),
]
EXT_GLUELESS = [
    ("Half & Half Quick Weave", 120, 150, ""),
    ("Glueless Traditional Quick Weave", 120, 175, ""),
    ("Glueless Closure Install", 120, 175, ""),
    ("Glueless Frontal Install", 120, 200, ""),
    ("27-Piece Pixie (Glueless)", 120, 125, ""),
]
EXT_PONY = [
    ("Frontal Ponytail", 120, 175, ""),
    ("Double Frontal Ponytail Style", 200, 225, ""),
    ("Sleek Ponytail with Braid Only", 150, 125, ""),
]
EXT_CARE = [
    ("Closure/Frontal Install Touch-Up", 180, 100, ""),
    ("Basic Sew-In Shampoo/Style Touch-Up", 240, 90, ""),
    ("Refresh Styling", 60, 80, ""),
    ("Weave Sew/Bond Take Down & Shampoo", 150, 100, ""),
]
SILK = [
    ("Silk Press", 180, 150, ""),
    ("Silk Press with Color", 225, 185, ""),
    ("Thermal Iron", 120, 100, ""),
    ("Shampoo with Treatment & Blow Dry", 150, 100, ""),
]
NATURAL = [
    ("Shampoo with Basic Style", 120, 75, ""),
    ("Relaxer", 120, 100, ""),
    ("Color Application with Style", 120, 100, ""),
    ("Highlights", 200, 250, ""),
    ("Comb Twist", 90, 100, ""),
    ("Dread Twist", 120, 100, ""),
    ("Dread Twist, Style & Color", 120, 200, ""),
    ("Sleek Ponytail", 120, 125, ""),
]
MEN = [
    ("Men's Braids", 120, 90, ""),
    ("Men's Box Braids", 200, 125, ""),
    ("Men's 2-Strand Twist", 200, 125, ""),
    ("Men's Dread Twist", 200, 150, ""),
    ("Men's Dread Styled", 120, 90, ""),
]
KIDS_BRAIDS = [
    ("Small Knotless Braids", 220, 190, ""),
    ("Medium Knotless", 200, 150, ""),
    ("Half Styled Half M/Lg Knotless", 200, 150, ""),
    ("Knotless Touch-Up (Front/Back)", 120, 95, ""),
    ("Box Braids (Rubber Band Method)", 120, 190, ""),
    ("Kids Bohemian Braids", 180, 180, ""),
    ("Miracle Knots", 120, 180, "Hair not provided. 2-bag minimum. Hair add-on available."),
    ("Lemonade Braid Style", 120, 125, ""),
    ("Layered Feed-In Braids", 180, 175, ""),
    ("2 Feed-In Braid Style", 120, 70, ""),
    ("Braided Ponytail", 120, 140, ""),
    ("Braids without Weave", 120, 100, ""),
]
KIDS_OTHER = [
    ("Crochet", 120, 150, ""),
    ("Kids Distressed Crochet", 200, 200, ""),
    ("Kids Locs Crochet", 225, 200, ""),
    ("Dread Twist", 45, 100, ""),
    ("Silk Press", 60, 90, ""),
    ("Relaxer", 60, 125, ""),
    ("Sleek Ponytail", 60, 100, ""),
    ("Cleanse Shampoo", 60, 85, ""),
]


def low(*menus):
    return min(p for m in menus for (_, _, p, _) in m)


def dur(mins):
    h, m = divmod(mins, 60)
    out = []
    if h:
        out.append(f"{h} hr")
    if m:
        out.append(f"{m} min")
    return " ".join(out)


def esc(s):
    return html.escape(s, quote=True)


def menu_table(title, rows, foot="", starting=False):
    body = []
    for name, mins, price, note in rows:
        n = f'<span class="note">{esc(note)}</span>' if note else ""
        body.append(
            f'<tr><td><span class="svc">{esc(name)}</span><span class="dur-inline">{dur(mins)}</span>{n}</td>'
            f'<td class="dur dur-col">{dur(mins)}</td>'
            f'<td class="price">{"from " if starting else ""}${price}</td></tr>'
        )
    f = f'<p class="menu-foot">{foot}</p>' if foot else ""
    return (
        f'<div class="menu"><h3>{esc(title)}</h3><table>'
        f'<thead><tr><th scope="col">Service</th><th scope="col" class="dur-col">Time</th><th scope="col">Price</th></tr></thead>'
        f'<tbody>{"".join(body)}</tbody></table>{f}</div>'
    )


# ---------------------------------------------------------------------------
# Icons
# ---------------------------------------------------------------------------
ICONS = {
    "phone": '<path d="M6.6 10.8a15.1 15.1 0 0 0 6.6 6.6l2.2-2.2a1 1 0 0 1 1-.25 11.4 11.4 0 0 0 3.6.57 1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17 17 0 0 1 3 4a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1c0 1.25.2 2.45.57 3.57a1 1 0 0 1-.25 1L6.6 10.8z"/>',
    "mail": '<path d="M20 4H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2zm0 4-8 5-8-5V6l8 5 8-5v2z"/>',
    "pin": '<path d="M12 2a7 7 0 0 0-7 7c0 5.25 7 13 7 13s7-7.75 7-13a7 7 0 0 0-7-7zm0 9.5A2.5 2.5 0 1 1 12 6.5a2.5 2.5 0 0 1 0 5z"/>',
    "clock": '<path d="M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20zm0 18a8 8 0 1 1 0-16 8 8 0 0 1 0 16zm.5-13H11v6l5.2 3.2.8-1.3-4.5-2.7V7z"/>',
    "card": '<path d="M20 4H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2zm0 14H4v-6h16v6zm0-10H4V6h16v2z"/>',
    "x": '<path d="M19 6.4 17.6 5 12 10.6 6.4 5 5 6.4 10.6 12 5 17.6 6.4 19 12 13.4 17.6 19 19 17.6 13.4 12z"/>',
    "users": '<path d="M16 11a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm-8 0a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm0 2c-2.3 0-7 1.2-7 3.5V19h14v-2.5C15 14.2 10.3 13 8 13zm8 0c-.3 0-.6 0-1 .05 1.2.84 2 2 2 3.45V19h6v-2.5c0-2.3-4.7-3.5-7-3.5z"/>',
    "alert": '<path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"/>',
    "menu": '<path d="M3 6h18v2H3V6zm0 5h18v2H3v-2zm0 5h18v2H3v-2z"/>',
    "ig": '<path d="M12 7a5 5 0 1 0 0 10 5 5 0 0 0 0-10zm0 8.2a3.2 3.2 0 1 1 0-6.4 3.2 3.2 0 0 1 0 6.4zM17.3 5.5a1.2 1.2 0 1 0 0 2.4 1.2 1.2 0 0 0 0-2.4zM21.9 7.1c-.1-1.6-.4-3-1.6-4.2S17.6 1.4 16 1.3C14.3 1.2 9.7 1.2 8 1.3c-1.6.1-3 .4-4.2 1.6S2.2 5.5 2.1 7.1C2 8.8 2 13.2 2.1 14.9c.1 1.6.4 3 1.6 4.2s2.6 1.5 4.2 1.6c1.7.1 6.3.1 8 0 1.6-.1 3-.4 4.2-1.6s1.5-2.6 1.6-4.2c.1-1.7.1-6.1 0-7.8zM19.7 17a3.3 3.3 0 0 1-1.8 1.8c-1.3.5-4.3.4-5.9.4s-4.6.1-5.9-.4A3.3 3.3 0 0 1 4.3 17c-.5-1.3-.4-4.3-.4-5.9s-.1-4.6.4-5.9A3.3 3.3 0 0 1 6.1 3.4C7.4 2.9 10.4 3 12 3s4.6-.1 5.9.4a3.3 3.3 0 0 1 1.8 1.8c.5 1.3.4 4.3.4 5.9s.1 4.6-.4 5.9z"/>',
    "gift": '<path d="M20 7h-2.2A3 3 0 0 0 12 3.8 3 3 0 0 0 6.2 7H4a1 1 0 0 0-1 1v4h1v8a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-8h1V8a1 1 0 0 0-1-1zM15 5a1 1 0 1 1 0 2h-2a2 2 0 0 1 2-2zM9 5a2 2 0 0 1 2 2H9a1 1 0 1 1 0-2zm2 14H6v-7h5v7zm0-9H5V9h6v1zm7 9h-5v-7h5v7zm1-9h-6V9h6v1z"/>',
}


def icon(name, cls="i"):
    return f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true" focusable="false">{ICONS[name]}</svg>'


# ---------------------------------------------------------------------------
# Navigation
# ---------------------------------------------------------------------------
SERVICE_PAGES = [
    ("/braids/", "Knotless Braids & Braid Styles"),
    ("/hair-extensions/", "Sew-Ins, Wigs & Extensions"),
    ("/silk-press/", "Silk Press"),
    ("/natural-hair/", "Natural Hair Care & Color"),
    ("/mens-braids/", "Men's Braids & Twists"),
    ("/kids-braids/", "Kids Braids & Styles"),
]
NAV = [
    ("/", "Home", None),
    ("/services/", "Services", SERVICE_PAGES),
    ("/gallery/", "Gallery", None),
    ("/about/", "About", None),
    ("/reviews/", "Reviews", None),
    ("/faq/", "FAQ", None),
    ("/contact/", "Contact", None),
]


def nav_html(current):
    items = []
    for href, label, sub in NAV:
        cur = ' aria-current="page"' if href == current else ""
        if sub:
            cur_attr = ' aria-current="page"'
            subs = "".join(
                f'<li><a href="{h}"{cur_attr if h == current else ""}>{esc(l)}</a></li>' for h, l in sub
            )
            items.append(f'<li class="has-sub"><a href="{href}"{cur}>{label}</a><ul class="sub">{subs}</ul></li>')
        else:
            items.append(f'<li><a href="{href}"{cur}>{label}</a></li>')
    return "".join(items)


def book_href():
    return "/book/"


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------
def business_schema():
    days = []
    for _, _, dlist, opens, closes in BIZ["hours"]:
        days.append({"@type": "OpeningHoursSpecification", "dayOfWeek": dlist, "opens": opens, "closes": closes})
    data = {
        "@type": "HairSalon",
        "@id": f"{SITE_URL}/#business",
        "name": BIZ["name"],
        "alternateName": BIZ["alt_name"],
        "url": f"{SITE_URL}/",
        "telephone": BIZ["phone_e164"],
        "email": BIZ["email"],
        "image": f"{SITE_URL}/assets/img/work/closure-install.jpg",
        "priceRange": "$$",
        "currenciesAccepted": "USD",
        "paymentAccepted": ", ".join(BIZ["payments"]),
        "address": {
            "@type": "PostalAddress",
            "streetAddress": BIZ["street"],
            "addressLocality": BIZ["city"],
            "addressRegion": BIZ["region"],
            "addressCountry": BIZ["country"],
        },
        "areaServed": [{"@type": "City", "name": c} for c in ["Stafford, TX", "Sugar Land, TX", "Missouri City, TX", "Houston, TX"]],
        "openingHoursSpecification": days,
    }
    if BIZ["instagram_url"]:
        data["sameAs"] = [BIZ["instagram_url"]]
    return data


def breadcrumb_schema(trail):
    return {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": name, "item": f"{SITE_URL}{href}"}
            for i, (href, name) in enumerate(trail)
        ],
    }


def service_schema(name, path, desc, menus):
    offers = []
    for m in menus:
        for n, _, p, _ in m:
            offers.append({
                "@type": "Offer",
                "itemOffered": {"@type": "Service", "name": n},
                "priceSpecification": {"@type": "PriceSpecification", "minPrice": p, "priceCurrency": "USD"},
            })
    return {
        "@type": "Service",
        "name": name,
        "serviceType": name,
        "description": desc,
        "url": f"{SITE_URL}{path}",
        "provider": {"@id": f"{SITE_URL}/#business"},
        "areaServed": {"@type": "City", "name": "Stafford, TX"},
        "hasOfferCatalog": {"@type": "OfferCatalog", "name": f"{name} menu", "itemListElement": offers},
    }


def faq_schema(groups):
    qs = []
    for _, items in groups:
        for q, a in items:
            qs.append({"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a)}})
    return {"@type": "FAQPage", "mainEntity": qs}


def strip_tags(s):
    import re
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s)).strip()


# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------
def head(page):
    canon = f"{SITE_URL}{page['path']}"
    robots = "index, follow, max-image-preview:large" if INDEXABLE and not page.get("noindex") else "noindex, follow"
    graph = [business_schema()]
    if page["path"] != "/":
        graph.append(breadcrumb_schema(page["trail"]))
    graph += page.get("schema", [])
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, separators=(",", ":"))
    og_img = page.get("og_image", "closure-install")
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(page['title'])}</title>
<meta name="description" content="{esc(page['desc'])}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{canon}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{BIZ['name']}">
<meta property="og:title" content="{esc(page['title'])}">
<meta property="og:description" content="{esc(page['desc'])}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{SITE_URL}/assets/img/work/{og_img}.jpg">
<meta name="twitter:card" content="summary">
<meta name="theme-color" content="#0e0d0c">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&family=Montserrat:wght@400;500;600&display=swap">
<link rel="stylesheet" href="/assets/css/site.css">
<script type="application/ld+json">{ld}</script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
"""


def header(current):
    return f"""<div class="topbar">
  <div class="wrap">
    <ul>
      <li>{icon('phone')}<a href="tel:{BIZ['phone_e164']}">{BIZ['phone']}</a></li>
      <li class="hide-sm">{icon('mail')}<a href="mailto:{BIZ['email']}">{BIZ['email']}</a></li>
    </ul>
    <ul>
      <li class="hours">{icon('clock')}Mon–Fri 9–9 · Sat–Sun 7–5</li>
      <li>{icon('pin')}{BIZ['city']}, {BIZ['region']}</li>
    </ul>
  </div>
</div>
<header class="site-header">
  <div class="wrap">
    <a class="logo" href="/" aria-label="{BIZ['name']} home"><b>DLUX</b><small>Beauty · Hair Studio</small></a>
    <button class="nav-toggle" type="button" aria-controls="site-nav" aria-expanded="false" aria-label="Open menu">{icon('menu')}</button>
    <nav class="nav" id="site-nav" aria-label="Main">
      <button class="nav-toggle nav-close" type="button" aria-label="Close menu">{icon('x')}</button>
      <ul>{nav_html(current)}</ul>
      <a class="btn header-cta" href="{book_href()}">Book Now</a>
    </nav>
    <div class="nav-shade"></div>
  </div>
</header>
"""


def hours_rows():
    return "".join(f"<tr><td>{d}</td><td>{h}</td></tr>" for d, h, *_ in BIZ["hours"])


def footer():
    svc = "".join(f'<li><a href="{h}">{esc(l)}</a></li>' for h, l in SERVICE_PAGES)
    ig = (f'<a href="{BIZ["instagram_url"]}" rel="noopener">{BIZ["instagram"]}</a>' if BIZ["instagram_url"] else BIZ["instagram"])
    year = date.today().year
    return f"""<footer class="site-footer">
  <div class="wrap cols">
    <div>
      <a class="logo" href="/"><b>DLUX</b><small>Beauty · Hair Studio</small></a>
      <p>Braids, sew-ins, wig installs, silk presses and natural hair care by appointment in {BIZ['city']}, {BIZ['region']}.</p>
      <ul class="foot-info">
        <li>{icon('pin')}<span>{LOCATION_TEXT}</span></li>
        <li>{icon('phone')}<a href="tel:{BIZ['phone_e164']}">{BIZ['phone']}</a></li>
        <li>{icon('mail')}<a href="mailto:{BIZ['email']}">{BIZ['email']}</a></li>
        <li>{icon('ig')}<span>Instagram: {ig}</span></li>
      </ul>
    </div>
    <div>
      <h2>Services</h2>
      <ul><li><a href="/services/">All services &amp; prices</a></li>{svc}</ul>
    </div>
    <div>
      <h2>Studio</h2>
      <ul>
        <li><a href="/book/">Book an appointment</a></li>
        <li><a href="/book/#policies">Booking policies</a></li>
        <li><a href="/gallery/">Gallery</a></li>
        <li><a href="/about/">About Denise</a></li>
        <li><a href="/reviews/">Reviews</a></li>
        <li><a href="/faq/">FAQ</a></li>
        <li><a href="/contact/">Contact</a></li>
      </ul>
    </div>
    <div class="on-dark">
      <h2>Hours</h2>
      <table class="hours"><tbody>{hours_rows()}</tbody></table>
      <p class="small mt-30">Appointments after 7 PM carry an after-hours fee.</p>
    </div>
  </div>
  <div class="copyright">
    <div class="wrap">
      <span>&copy; {year} {BIZ['name']}. All rights reserved.</span>
      <span><a href="/book/#policies">Booking policies</a></span>
    </div>
  </div>
</footer>
<script src="/assets/js/site.js" defer></script>
</body>
</html>
"""


def banner(page, intro=""):
    crumbs = []
    trail = page["trail"]
    for i, (href, name) in enumerate(trail):
        if i == len(trail) - 1:
            crumbs.append(f'<li aria-current="page">{esc(name)}</li>')
        else:
            crumbs.append(f'<li><a href="{href}">{esc(name)}</a></li>')
    p = f"<p>{intro}</p>" if intro else ""
    return f"""<section class="banner">
  <div class="wrap">
    <h1>{page['h1']}</h1>
    {p}
    <nav aria-label="Breadcrumb"><ol class="crumbs">{''.join(crumbs)}</ol></nav>
  </div>
</section>
"""


def cta_band(title="Ready for your next look?", text=None):
    text = text or f"Book online in a few minutes. A $25 non-refundable deposit holds your spot and goes toward your service. Questions? Call or text {BIZ['phone']}."
    return f"""<section class="cta-band">
  <div class="wrap">
    <span class="eyebrow">Hello beauty, ready to book?</span>
    <h2>{title}</h2>
    <p>{text}</p>
    <div class="btn-row on-dark"><a class="btn" href="{book_href()}">Book Now</a><a class="btn btn--ghost" href="tel:{BIZ['phone_e164']}">Call {BIZ['phone']}</a></div>
  </div>
</section>
"""


def todo(title, body):
    return f'<div class="todo"><strong>Content needed: {esc(title)}</strong>{body}</div>'


def write(path, content):
    out = os.path.join(PUBLIC, path.strip("/"), "index.html") if path != "/404" else os.path.join(PUBLIC, "404.html")
    if path == "/":
        out = os.path.join(PUBLIC, "index.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(content)


PAGES = []


def page(path, title, desc, h1, trail, body, schema=None, og_image=None, noindex=False, sitemap=True):
    p = {"path": path, "title": title, "desc": desc, "h1": h1, "trail": trail, "schema": schema or [], "noindex": noindex}
    if og_image:
        p["og_image"] = og_image
    p["body"] = body(p) if callable(body) else body
    p["sitemap"] = sitemap
    PAGES.append(p)
    return p


def render(p):
    current = p["path"]
    return head(p) + header(current) + f'<main id="main">\n{p["body"]}</main>\n' + footer()


HOME = [("/", "Home")]
SERVICES = HOME + [("/services/", "Services")]


# ---------------------------------------------------------------------------
# Shared blocks
# ---------------------------------------------------------------------------
def related(exclude):
    cards = []
    for href, label in SERVICE_PAGES:
        if href == exclude:
            continue
        cards.append(f'<li><a href="{href}">{esc(label)}</a></li>')
    return f"""<section class="section--tight section section--cream">
  <div class="wrap">
    <div class="title-area"><span class="eyebrow">Explore more</span><h2>Other services at Dlux Beauty</h2></div>
    <ul class="pay-list" style="justify-content:center">{''.join(cards)}</ul>
    <p class="center mt-30"><a class="link-arrow" href="/services/">Full service menu &amp; prices</a></p>
  </div>
</section>
"""


def prep_block(items, title="Before your appointment"):
    lis = "".join(f"<li>{i}</li>" for i in items)
    return f'<h2>{title}</h2><ul class="checks">{lis}</ul>'


def mini_faq(items):
    out = []
    for q, a in items:
        out.append(f'<details><summary>{esc(q)}</summary><div class="ans"><p>{a}</p></div></details>')
    return f'<div class="faq">{"".join(out)}</div>'


PRICE_NOTE = "Prices and times come from the Dlux Beauty booking menu and may change. Final pricing is confirmed when you book."
PREP_NATURAL = "Come with your hair free of braids and glue unless you booked a take-down. Shampoo is included free of charge."
PREP_ADDONS = "Want curls, crimping, a wash or a cut? Add it as an “add-on” when you book so enough time is reserved."


def service_page(path, title, desc, h1, intro, photos, lede_html, menus_html, menus, prep, faqs, svc_name, extra=""):
    def body(p):
        media = "".join(img(k) if k in PHOTOS else ph(k) for k in photos)
        return f"""{banner(p, intro)}
<section class="section">
  <div class="wrap split">
    <div>{lede_html}
      <div class="btn-row mt-30"><a class="btn" href="{book_href()}">Book Now</a><a class="btn btn--ghost" href="#menu">See prices</a></div>
    </div>
    <div class="duo">{media}</div>
  </div>
</section>
<section class="section section--cream" id="menu">
  <div class="wrap">
    <div class="title-area"><span class="eyebrow">Menu</span><h2>Prices &amp; appointment times</h2><p>{PRICE_NOTE}</p></div>
    <div class="stack">{menus_html}</div>
  </div>
</section>
<section class="section">
  <div class="wrap split" style="align-items:start">
    <div>{prep_block(prep)}</div>
    <div><h2>Good to know</h2>{mini_faq(faqs)}</div>
  </div>
</section>
{extra}{related(path)}{cta_band()}"""
    return page(path, title, desc, h1, SERVICES + [(path, svc_name)], body,
                schema=[service_schema(svc_name, path, desc, menus)], og_image=photos[0] if photos[0] in PHOTOS else None)


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------
SERVICE_CARDS = [
    ("/braids/", "Knotless Braids", "Small to jumbo knotless, boho knotless, Miracle Knots, feed-ins, braided ponytails, soft locs and crochet.", None, low(BRAIDS)),
    ("/hair-extensions/", "Sew-Ins, Wigs & Extensions", "Traditional and flip-method sew-ins, quick weaves, closure, frontal and 360 installs, wig installs and tape-ins.", "closure-install", low(EXT_INSTALLS, EXT_GLUELESS, EXT_PONY, EXT_CARE)),
    ("/silk-press/", "Silk Press", "Silk press, silk press with color, thermal iron styling and shampoo with treatment and blow dry.", "silk-press", low(SILK)),
    ("/natural-hair/", "Natural Hair Care & Color", "Color, highlights, relaxers, comb twists, dread twists and sleek ponytails.", "color-application", low(NATURAL)),
    ("/mens-braids/", "Men's Braids & Twists", "Men's braids, box braids, 2-strand twists and dread twists.", "mens-braids", low(MEN)),
    ("/kids-braids/", "Kids Braids & Styles", "Knotless, box braids, lemonade braids, crochet, silk press and more for kids, with an adult present.", None, low(KIDS_BRAIDS, KIDS_OTHER)),
]


def service_cards(heading_level="h3"):
    out = []
    for href, name, text, photo, frm in SERVICE_CARDS:
        media = img(photo) if photo else ph(name.split(" ")[0])
        out.append(f"""<article class="card">
  <a class="card-media" href="{href}" tabindex="-1" aria-hidden="true">{media}</a>
  <div class="card-body">
    <div class="card-meta">From ${frm}</div>
    <{heading_level}><a href="{href}">{esc(name)}</a></{heading_level}>
    <p>{text}</p>
    <a class="link-arrow" href="{href}">View {esc(name.split(' &')[0].lower())} menu</a>
  </div>
</article>""")
    return f'<div class="grid g3">{"".join(out)}</div>'


def policy_cards():
    items = [
        ("card", "Deposit", "Every service requires a non-refundable $25 deposit. It is credited toward your appointment."),
        ("clock", "Late policy", "Please arrive on time. There is a 15-minute grace period, then a $25 late fee applies."),
        ("x", "Cancellations", "Cancel at least 24 hours before your appointment. No-call, no-shows are charged half the service fee."),
        ("users", "Guests", "No extra guests. Clients 16 and up may come alone; clients under 16 must be accompanied by an adult."),
    ]
    return "".join(
        f'<div class="policy">{icon(i, "i ic")}<h3>{t}</h3><p>{d}</p></div>' for i, t, d in items
    )


# Home ----------------------------------------------------------------------
def home_body(p):
    strip = "".join(img(k) for k in ["closure-install", "silk-press", "glueless-frontal-install", "comb-twist", "wig-install", "partial-pixie-sew-in"])
    hero_imgs = img("360-frontal-install", eager=True) + img("silk-press", eager=True) + img("traditional-sew-in", eager=True)
    return f"""<section class="hero">
  <div class="wrap">
    <div>
      <span class="eyebrow">Dlux Beauty Hair Studio · Stafford, TX</span>
      <h1>Braids, Sew-Ins &amp; Silk Presses in <em>Stafford, TX</em></h1>
      <p class="lead">Knotless braids, closure and frontal installs, wig installs, silk presses and natural hair care, booked online with clear prices and one-on-one appointments.</p>
      <div class="btn-row on-dark"><a class="btn" href="{book_href()}">Book Now</a><a class="btn btn--ghost" href="/services/">Services &amp; Prices</a></div>
      <ul class="hero-facts">
        <li>{icon('clock')}Open 7 days</li>
        <li>{icon('pin')}{LOCATION_TEXT}</li>
        <li>{icon('phone')}<a href="tel:{BIZ['phone_e164']}" style="color:inherit">{BIZ['phone']}</a></li>
      </ul>
    </div>
    <div class="hero-collage">{hero_imgs}</div>
  </div>
</section>
<section class="info-strip" aria-label="Studio information">
  <div class="wrap">
    <div class="cell">{icon('clock', 'i ic')}<div><h3>Hours</h3><p>Mon–Fri 9 AM–9 PM<br>Sat &amp; Sun 7 AM–5 PM</p></div></div>
    <div class="cell">{icon('pin', 'i ic')}<div><h3>Location</h3><p>{LOCATION_TEXT}<br><a href="/contact/">Directions &amp; contact</a></p></div></div>
    <div class="cell">{icon('card', 'i ic')}<div><h3>Payments</h3><p>Apple Pay, Cash App, Zelle, cash and card</p></div></div>
  </div>
</section>
<section class="section">
  <div class="wrap">
    <div class="title-area"><span class="eyebrow">What we do</span><h2>Hair services in Stafford, TX</h2><p>Choose a service to see every style, appointment time and starting price.</p><hr class="divider"></div>
    {service_cards()}
    <p class="center mt-50"><a class="btn btn--ghost" href="/services/">View the full menu</a></p>
  </div>
</section>
<section class="section section--cream">
  <div class="wrap split">
    <div>
      <span class="eyebrow">Meet your stylist</span>
      <h2>Denise and the Dlux Beauty studio</h2>
      <p class="lead">Dlux Beauty is Denise's hair studio on Murphy Rd in Stafford. Every appointment is one-on-one, from a fresh set of knotless braids to a full frontal install or silk press.</p>
      {todo('Short owner intro', '<p>Two or three sentences from Denise: years doing hair, what she is known for, and why clients come back.</p>')}
      <a class="link-arrow" href="/about/">About Denise</a>
    </div>
    <div class="duo">{img('refresh-styling')}{img('closure-frontal-touch-up')}</div>
  </div>
</section>
<section class="section">
  <div class="wrap">
    <div class="title-area"><span class="eyebrow">Recent work</span><h2>Transformations from the chair</h2></div>
    <div class="strip">{strip}</div>
    <p class="center mt-50"><a class="btn btn--ghost" href="/gallery/">See the gallery</a></p>
  </div>
</section>
<section class="section section--dark" id="policies">
  <div class="wrap">
    <div class="title-area"><span class="eyebrow">Please read before booking</span><h2>Booking policies</h2></div>
    <div class="grid g4">{policy_cards()}</div>
    <p class="center mt-50"><a class="link-arrow" href="/book/#policies" style="color:var(--gold-lt)">All booking details</a></p>
  </div>
</section>
<section class="section">
  <div class="wrap split" style="align-items:start">
    <div>
      <span class="eyebrow">Questions</span>
      <h2>Before you book</h2>
      <p>Quick answers to what clients ask most. See the <a href="/faq/">full FAQ</a> for prep, hair drop-offs and after-hours appointments.</p>
    </div>
    {mini_faq([
        ("Is hair included with braid services?", 'Not for most braid styles. Bring your own hair or choose the hair add-on when you book. See the <a href="/braids/">braid menu</a> for details by style.'),
        ("Do you take walk-ins?", f'Appointments are booked online with a $25 deposit. If you need a time the booking page doesn&rsquo;t show, text {BIZ["phone"]}.'),
        ("Which payments do you accept?", "Apple Pay, Cash App, Zelle, cash and card."),
    ])}
  </div>
</section>
<section class="section section--sand section--tight">
  <div class="wrap center">
    <span class="eyebrow">Tag us, get featured</span>
    <h2>Follow {BIZ['instagram']} on Instagram</h2>
    <p>Share your new look and tag {BIZ['instagram']} for a chance to be featured.</p>
  </div>
</section>
{cta_band()}"""


page("/", "Dlux Beauty | Braids, Sew-Ins & Silk Press in Stafford, TX",
     f"Knotless braids, sew-ins, wig installs, silk presses and natural hair care at Dlux Beauty in Stafford, TX. See prices and book online. Call {BIZ['phone']}.",
     "", HOME, home_body)


# Services hub ----------------------------------------------------------------
MEN_FOOT = '<a href="/mens-braids/">Men&rsquo;s braids details</a>'


def services_body(p):
    return f"""{banner(p, "Every service on the Dlux Beauty menu with appointment times and starting prices. Pick a category for details, prep tips and photos.")}
<section class="section">
  <div class="wrap">
    {service_cards('h2')}
  </div>
</section>
<section class="section section--cream">
  <div class="wrap">
    <div class="title-area"><span class="eyebrow">Price list</span><h2>Full service menu</h2><p>{PRICE_NOTE} Braid and kids prices are starting prices.</p></div>
    <div class="stack">
      {menu_table('Knotless Braids & Braid Styles', BRAIDS, '<a href="/braids/">Braid details &amp; prep</a>', starting=True)}
      {menu_table('Sew-Ins, Installs & Extensions', EXT_INSTALLS + EXT_GLUELESS + EXT_PONY + EXT_CARE, '<a href="/hair-extensions/">Install details &amp; prep</a>')}
      {menu_table('Silk Press', SILK, '<a href="/silk-press/">Silk press details</a>')}
      {menu_table('Natural Hair Care & Color', NATURAL, '<a href="/natural-hair/">Natural hair details</a>')}
      {menu_table("Men's Styles", MEN, MEN_FOOT)}
      {menu_table('Kids Only', KIDS_BRAIDS + KIDS_OTHER, '<a href="/kids-braids/">Kids details &amp; policy</a>', starting=True)}
    </div>
  </div>
</section>
<section class="section">
  <div class="wrap split">
    <div>
      <h2>Gift certificates</h2>
      <p>Dlux Beauty gift certificates are available through the online booking page. They make an easy gift for birthdays, graduations and holidays.</p>
      <a class="btn" href="{book_href()}">Buy or book online</a>
    </div>
    <div class="note-box"><p><strong>Add-ons:</strong> {PREP_ADDONS}</p><p><strong>Natural hair:</strong> {PREP_NATURAL} Take-down is an add-on.</p></div>
  </div>
</section>
{cta_band()}"""


page("/services/", "Hair Services & Prices | Dlux Beauty Stafford, TX",
     "See every Dlux Beauty service with prices and times: knotless braids, sew-ins, frontal and wig installs, silk press, natural hair, men's and kids styles.",
     "Hair Services &amp; Prices", SERVICES, services_body)


# Braids ------------------------------------------------------------------------
service_page(
    "/braids/",
    "Knotless Braids in Stafford, TX | Dlux Beauty",
    f"Knotless braids in Stafford, TX from ${low(BRAIDS)}: small to jumbo, boho knotless, Miracle Knots, feed-ins, soft locs and crochet. See times and book online.",
    "Knotless Braids &amp; Braid Styles in Stafford, TX",
    "Small to jumbo knotless, boho styles, Miracle Knots, feed-ins, ponytails, soft locs and crochet.",
    ["Braids", "Knotless"],
    f"""<span class="eyebrow">Braid menu</span>
<h2>Knotless braids, sized and styled your way</h2>
<p>Dlux Beauty's braid menu covers every knotless size from small to jumbo, boho knotless with curly pieces, half-styled looks, Miracle Knots and feed-in styles. Twist and loc styles include a fashion twist bob and soft locs, with crochet pre-loop and individuals for faster installs.</p>
<p>Prices are starting prices and depend on length and size. Many braid styles do not include hair, so check the notes in the menu below before you book.</p>""",
    menu_table("Knotless", BRAIDS[:10], starting=True) + menu_table("Miracle Knots, feed-ins & ponytails", BRAIDS[10:16], starting=True)
    + menu_table("Twists, locs, crochet & take-down", BRAIDS[16:], starting=True),
    [BRAIDS],
    [
        "Hair is not provided for most braid styles. Bring your own hair or select the hair add-on when booking.",
        "Miracle Knots need a 4-bag minimum. Human hair is available as an add-on in natural colors only.",
        "Boho styles come in basic colors only.",
        PREP_NATURAL,
        "Need old braids removed first? Book <strong>Braid Take Down &amp; Shampoo</strong> (detangle, exfoliate, cleanse and blow out) or add take-down to your appointment.",
        "Dropping off hair ahead of time? Label it with your name and appointment date and time, and text or email to schedule the drop-off.",
    ],
    [
        ("How long do knotless braids take?", "Times on the menu run from about 2 hours for jumbo knotless to 5 hours for small knotless. Boho and layered styles take longer than plain knotless in the same size."),
        ("Can I get just the front or back redone?", f"Yes. Book <strong>Knotless Touch-Up (Top/Back)</strong>, starting at $125."),
        ("Do you braid kids or men?", 'Yes. See <a href="/kids-braids/">kids braids</a> and <a href="/mens-braids/">men\'s braids &amp; twists</a> for those menus and prices.'),
        ("What colors are available for boho and Miracle Knots?", "Boho styles are basic colors only. Miracle Knots with human hair are natural colors only."),
    ],
    "Knotless Braids & Braid Styles",
)

# Hair extensions -------------------------------------------------------------
service_page(
    "/hair-extensions/",
    "Sew-Ins & Wig Installs in Stafford, TX | Dlux Beauty",
    f"Sew-ins, quick weaves, closure, frontal and 360 installs, glueless units, wig installs and tape-ins in Stafford, TX from ${low(EXT_INSTALLS, EXT_GLUELESS, EXT_PONY, EXT_CARE)}. Book online.",
    "Sew-Ins, Wig Installs &amp; Hair Extensions in Stafford, TX",
    "Sew-ins, quick weaves, closure and frontal installs, wig installs, tape-ins, ponytails and install maintenance.",
    ["360-frontal-install", "closure-install"],
    """<span class="eyebrow">Installs &amp; extensions</span>
<h2>Sew-ins, frontals, closures and wigs</h2>
<p>From a traditional sew-in to a 360 lace frontal, Dlux Beauty installs and styles extensions for a natural-looking finish. Prefer no glue? Choose a glueless quick weave, closure or frontal install, or a 27-piece glueless pixie.</p>
<p>Keep your install fresh with touch-ups, refresh styling and a full take-down and shampoo when it's time for a new look.</p>""",
    menu_table("Sew-ins, installs & extensions", EXT_INSTALLS) + menu_table("Glueless & quick weaves", EXT_GLUELESS)
    + menu_table("Ponytails", EXT_PONY) + menu_table("Maintenance & take-down", EXT_CARE),
    [EXT_INSTALLS, EXT_GLUELESS, EXT_PONY, EXT_CARE],
    [
        "Bringing your own bundles, closure, frontal or wig? Hair drop-offs must include your name and appointment date and time. Text or email to schedule the drop-off.",
        PREP_NATURAL,
        "Wearing an old install? Book <strong>Weave Sew/Bond Take Down &amp; Shampoo</strong> or add take-down so your appointment has enough time.",
        PREP_ADDONS,
    ],
    [
        ("What's the difference between a closure and a frontal install?", "A closure covers the top of the head, while a frontal runs ear to ear along the hairline, and a 360 frontal goes all the way around. Closure installs start at $190, frontal installs at $225 and 360 frontal installs at $250."),
        ("Do you offer glueless installs?", "Yes. Glueless traditional quick weave and glueless closure installs start at $175, glueless frontal installs at $200 and a 27-piece glueless pixie at $125."),
        ("How do I maintain my install?", "Book a Closure/Frontal Install Touch-Up ($100), Basic Sew-In Shampoo/Style Touch-Up ($90) or Refresh Styling ($80) between installs."),
        ("Do you do tape-in extensions?", "Yes. Tape-ins are done with a silk press, starting at $600."),
    ],
    "Sew-Ins, Wig Installs & Hair Extensions",
    extra=f"""<section class="section section--cream section--tight">
  <div class="wrap">
    <div class="title-area"><span class="eyebrow">Recent installs</span><h2>Install gallery</h2></div>
    <div class="strip">{''.join(img(k) for k in ['traditional-sew-in','frontal-install','glueless-frontal-install','glueless-closure-install','wig-install','frontal-ponytail'])}</div>
    <p class="center mt-30"><a class="link-arrow" href="/gallery/#installs">More installs</a></p>
  </div>
</section>
""",
)

# Silk press ------------------------------------------------------------------
service_page(
    "/silk-press/",
    "Silk Press in Stafford, TX | Dlux Beauty",
    f"Silk press in Stafford, TX from ${low(SILK)}, plus silk press with color, thermal iron and shampoo with treatment and blow dry. See times and book online.",
    "Silk Press in Stafford, TX",
    "Silk press, silk press with color, thermal iron styling and shampoo with treatment and blow dry.",
    ["silk-press", "thermal-iron"],
    """<span class="eyebrow">Silk press</span>
<h2>Smooth, swinging silk press on natural hair</h2>
<p>A silk press straightens natural hair with heat, without chemicals, for a sleek, light finish with movement. Dlux Beauty offers a classic silk press, a silk press with color, and thermal iron styling.</p>
<p>Want a healthy reset first? Book a shampoo with treatment and blow dry.</p>""",
    menu_table("Silk press & thermal styling", SILK),
    [SILK],
    [
        PREP_NATURAL,
        "Planning color? Book <strong>Silk Press with Color</strong> so your appointment includes both.",
        "Want curls or a trim? Add curling or cutting as an add-on when you book.",
        'Booking for a child? Kids silk press is on the <a href="/kids-braids/">kids menu</a>, starting at $90.',
    ],
    [
        ("How long does a silk press take?", "Plan on about 3 hours for a silk press and 3 hours 45 minutes for a silk press with color."),
        ("Do I need to wash my hair before I come?", "No. Shampoo is included free of charge for natural hair services. Just come with your hair free of braids and glue."),
        ("Can I add highlights?", 'Yes. Highlights are on the <a href="/natural-hair/">natural hair &amp; color</a> menu.'),
    ],
    "Silk Press",
)

# Natural hair ----------------------------------------------------------------
service_page(
    "/natural-hair/",
    "Natural Hair Care & Color in Stafford, TX | Dlux Beauty",
    f"Natural hair care in Stafford, TX: color, highlights, relaxers, comb twists, dread twists, sleek ponytails and shampoo and style from ${low(NATURAL)}. Book online.",
    "Natural Hair Care &amp; Color in Stafford, TX",
    "Color, highlights, relaxers, comb twists, dread twists, sleek ponytails and shampoo and style.",
    ["color-application", "dread-twist-color"],
    """<span class="eyebrow">Natural hair care</span>
<h2>Color, twists and healthy styling</h2>
<p>Dlux Beauty's natural hair menu covers color application with style, highlights and relaxers, plus comb twists, dread twists and a sleek ponytail. For a simple refresh, book a shampoo with basic style.</p>
<p>Looking for a straight, sleek finish? See the <a href="/silk-press/">silk press</a> menu.</p>""",
    menu_table("Natural hair care & color", NATURAL),
    [NATURAL],
    [
        PREP_NATURAL,
        "Take-down of braids or twists is an add-on. Add it when you book.",
        PREP_ADDONS,
    ],
    [
        ("Do you do color on natural hair?", "Yes. Color Application with Style starts at $100, Highlights at $250 and Dread Twist, Style &amp; Color at $200."),
        ("Do you offer relaxers?", 'Yes. Relaxers start at $100 for adults. Kids relaxers are on the <a href="/kids-braids/">kids menu</a>.'),
        ("Do you do twists for men?", 'Yes. See <a href="/mens-braids/">men\'s braids &amp; twists</a> for 2-strand and dread twists.'),
    ],
    "Natural Hair Care & Color",
    extra=f"""<section class="section section--cream section--tight">
  <div class="wrap">
    <div class="strip" style="grid-template-columns:repeat(4,1fr)">{''.join(img(k) for k in ['comb-twist','relaxer','color-application','dread-twist-color'])}</div>
  </div>
</section>
""",
)

# Men -------------------------------------------------------------------------
service_page(
    "/mens-braids/",
    "Men's Braids & Twists in Stafford, TX | Dlux Beauty",
    f"Men's braids in Stafford, TX from ${low(MEN)}: braids, box braids, 2-strand twists, dread twists and dread styling. See times and book online.",
    "Men's Braids &amp; Twists in Stafford, TX",
    "Braids, box braids, 2-strand twists, dread twists and dread styling.",
    ["mens-braids", "comb-twist"],
    """<span class="eyebrow">Men's styles</span>
<h2>Clean braids and twists for men</h2>
<p>Dlux Beauty braids and twists men's hair by appointment, from a quick set of braids to box braids, 2-strand twists and dread twists. Already have dreads? Book a dread styling appointment.</p>""",
    menu_table("Men's styles", MEN),
    [MEN],
    [
        PREP_NATURAL,
        "Need old braids taken down? Add take-down to your booking.",
        "Clients under 16 must be accompanied by an adult.",
    ],
    [
        ("How long do men's braids take?", "Men's braids take about 2 hours. Box braids, 2-strand twists and dread twists take about 3 hours 20 minutes."),
        ("Do you do comb twists?", 'Yes. Comb twists are on the <a href="/natural-hair/">natural hair</a> menu.'),
        ("Do you braid boys?", 'Yes. See the <a href="/kids-braids/">kids menu</a> for kids-only styles and prices.'),
    ],
    "Men's Braids & Twists",
)

# Kids ------------------------------------------------------------------------
service_page(
    "/kids-braids/",
    "Kids Braids & Hairstyles in Stafford, TX | Dlux Beauty",
    f"Kids braids in Stafford, TX from ${low(KIDS_BRAIDS, KIDS_OTHER)}: knotless, box braids, lemonade braids, feed-ins, crochet, silk press and more. Adult must attend.",
    "Kids Braids &amp; Hairstyles in Stafford, TX",
    "Knotless, box braids, lemonade braids, feed-ins, ponytails, crochet, silk press and more for kids.",
    ["Kids", "Braids"],
    """<span class="eyebrow">Kids only</span>
<h2>Braids and styles sized for kids</h2>
<p>The kids menu has its own pricing and shorter appointment times for knotless braids, box braids (rubber band method), bohemian and lemonade braids, feed-ins, braided ponytails and crochet styles. Silk press, relaxer, sleek ponytail and a cleanse shampoo are also available.</p>
<div class="note-box"><p><strong>Kids policy:</strong> clients under 16 must be accompanied by an adult. No extra guests, please.</p></div>""",
    menu_table("Kids braids", KIDS_BRAIDS, starting=True) + menu_table("Kids crochet, silk press & more", KIDS_OTHER, starting=True),
    [KIDS_BRAIDS, KIDS_OTHER],
    [
        "One adult must stay with clients under 16. No extra guests.",
        "Hair is not provided for Kids Miracle Knots (2-bag minimum). Choose the hair add-on if needed.",
        PREP_NATURAL,
        "Bring snacks or a quiet activity for longer appointments.",
    ],
    [
        ("Is there an age limit?", "Clients under 16 are welcome with an adult present. Clients 16 and up may come alone."),
        ("How long do kids braids take?", "Most kids styles take 2 to 3 hours 45 minutes depending on the style. A kids dread twist takes about 45 minutes."),
        ("Can my child get a silk press?", "Yes. Kids silk press starts at $90 and takes about 1 hour."),
    ],
    "Kids Braids & Hairstyles",
)


# Gallery ---------------------------------------------------------------------
def gallery_body(p):
    groups = [
        ("installs", "Sew-ins, wigs &amp; extensions", "/hair-extensions/", "hair-extensions"),
        ("silk-press", "Silk press", "/silk-press/", "silk-press"),
        ("natural-hair", "Natural hair &amp; color", "/natural-hair/", "natural-hair"),
        ("mens", "Men's braids", "/mens-braids/", "mens-braids"),
    ]
    out = []
    for gid, title, href, cat in groups:
        figs = []
        for k, (cap, _, c) in PHOTOS.items():
            if c != cat:
                continue
            figs.append(f'<figure>{img(k)}<figcaption>{esc(cap)}</figcaption></figure>')
        out.append(f"""<section class="section--tight section" id="{gid}" style="padding-top:0">
  <div class="title-area title-area--left"><h2>{title}</h2><a class="link-arrow" href="{href}">View menu &amp; prices</a></div>
  <div class="gallery">{''.join(figs)}</div>
</section>""")
    return f"""{banner(p, "Real work from the Dlux Beauty chair in Stafford, TX: installs, silk presses, color, twists and braids.")}
<div class="section"><div class="wrap">
{todo('Gallery photos', '<p>These photos come from the booking page and are small. Needed: full-size originals plus knotless braid, boho, Miracle Knots, soft locs and kids photos (with parent permission). Before-and-after pairs work best.</p>')}
{''.join(out)}
<section class="section--tight section" id="braids" style="padding-top:0">
  <div class="title-area title-area--left"><h2>Knotless braids &amp; braid styles</h2><a class="link-arrow" href="/braids/">View menu &amp; prices</a></div>
  <div class="gallery"><figure>{ph('Knotless')}<figcaption>Braid photos coming soon</figcaption></figure><figure>{ph('Boho')}<figcaption>Braid photos coming soon</figcaption></figure><figure>{ph('Soft Locs')}<figcaption>Braid photos coming soon</figcaption></figure></div>
</section>
<p class="center">Follow <strong>{BIZ['instagram']}</strong> on Instagram for the latest looks.</p>
</div></div>
{cta_band('Love a look you see here?')}"""


page("/gallery/", "Hair Gallery: Braids, Sew-Ins & Silk Press | Dlux Beauty",
     "Browse real client work from Dlux Beauty in Stafford, TX: frontal and closure installs, wig installs, pixies, silk presses, color, twists and braids.",
     "Gallery &amp; Transformations", HOME + [("/gallery/", "Gallery")], gallery_body, og_image="frontal-install")


# About -----------------------------------------------------------------------
def about_body(p):
    return f"""{banner(p, "The stylist behind Dlux Beauty in Stafford, TX.")}
<section class="section">
  <div class="wrap split">
    <div class="duo">{ph('Denise', 'Headshot needed')}{img('closure-frontal-touch-up')}</div>
    <div>
      <span class="eyebrow">Meet Denise</span>
      <h2>Owner &amp; stylist, Dlux Beauty</h2>
      <p class="lead">Dlux Beauty is Denise's hair studio on Murphy Rd in Stafford, TX, offering braids, installs, silk presses and natural hair care by appointment.</p>
      {todo('Denise bio', '<ul><li>How long she has been doing hair and how she got started</li><li>Training, licenses or certifications</li><li>Signature services and what clients book her for</li><li>What a visit to the studio is like</li><li>A professional headshot and a studio photo</li></ul>')}
      <div class="btn-row"><a class="btn" href="{book_href()}">Book with Denise</a><a class="btn btn--ghost" href="/gallery/">See her work</a></div>
    </div>
  </div>
</section>
<section class="section section--cream">
  <div class="wrap">
    <div class="title-area"><span class="eyebrow">Specialties</span><h2>What Denise does</h2></div>
    <div class="grid g3">
      <div><h3><a href="/braids/">Knotless braids</a></h3><p>Every size from small to jumbo, boho knotless, Miracle Knots, feed-ins and soft locs.</p></div>
      <div><h3><a href="/hair-extensions/">Installs &amp; wigs</a></h3><p>Sew-ins, closure, frontal and 360 installs, glueless units, pixies and wig installs.</p></div>
      <div><h3><a href="/silk-press/">Silk press &amp; natural hair</a></h3><p>Silk press, color, highlights, relaxers and twists for natural hair.</p></div>
    </div>
  </div>
</section>
<section class="section">
  <div class="wrap split">
    <div>
      <h2>The studio</h2>
      <p>Appointments are one-on-one and booked online. To keep things running on time, the studio has a 15-minute grace period, a 24-hour cancellation window and a no-extra-guests policy.</p>
      <a class="link-arrow" href="/book/#policies">Read the booking policies</a>
    </div>
    <div class="note-box"><p><strong>Location:</strong> {LOCATION_TEXT}</p><p><strong>Hours:</strong> Mon–Fri 9 AM–9 PM, Sat–Sun 7 AM–5 PM</p><p><strong>Call or text:</strong> <a href="tel:{BIZ['phone_e164']}">{BIZ['phone']}</a></p></div>
  </div>
</section>
{cta_band()}"""


page("/about/", "About Denise, Owner of Dlux Beauty | Stafford, TX",
     "Meet Denise, owner and stylist at Dlux Beauty in Stafford, TX, specializing in knotless braids, sew-ins, frontal and wig installs, silk press and natural hair.",
     "About Denise", HOME + [("/about/", "About Denise")], about_body)


# Reviews ---------------------------------------------------------------------
def reviews_body(p):
    return f"""{banner(p, "What clients say about their experience at Dlux Beauty in Stafford, TX.")}
<section class="section">
  <div class="wrap prose" style="margin:0 auto">
    {todo('Client reviews', '<p>Add 6 to 10 real reviews with first name and service (for example, "Tasha, frontal install"), with permission. Also needed: the Google Business Profile review link for the button below. Ratings schema will be added only for reviews collected on this site.</p>')}
    <h2>Loved your appointment?</h2>
    <p>Reviews help other clients in Stafford, Sugar Land and Missouri City find the right stylist. It takes a minute and means a lot to a small studio.</p>
    <div class="btn-row"><span class="btn" aria-disabled="true" style="opacity:.55;cursor:default">Leave a Google review (link needed)</span><a class="btn btn--ghost" href="/gallery/">See client results</a></div>
    <h2>Tag us, get featured</h2>
    <p>Post your new look on Instagram and tag <strong>{BIZ['instagram']}</strong> for a chance to be featured.</p>
  </div>
</section>
{cta_band()}"""


page("/reviews/", "Client Reviews | Dlux Beauty Hair Studio, Stafford TX",
     "Read client reviews of Dlux Beauty in Stafford, TX for knotless braids, sew-ins, frontal installs and silk presses, and leave a review of your visit.",
     "Client Reviews", HOME + [("/reviews/", "Reviews")], reviews_body)


# FAQ -------------------------------------------------------------------------
FAQ_GROUPS = [
    ("Booking &amp; deposits", [
        ("How do I book an appointment?", f'Book online through the <a href="/book/">booking page</a>. Choose your service category, then your style and time. If you can&rsquo;t find the time you need, call or text {BIZ["phone"]}.'),
        ("Do I need a deposit?", "Yes. All services require a non-refundable $25 deposit. The deposit is credited toward your appointment."),
        ("Can I book after hours?", f"Appointments after 7 PM carry an after-hours fee. If the booking page won't let you book the time you want, pick any open spot and text {BIZ['phone']} with your preferred date, time and style. You can also send your deposit by Zelle or Cash App with the date, time and style."),
        ("Do you sell gift certificates?", 'Yes. Gift certificates are available through the online <a href="/book/">booking page</a>.'),
    ]),
    ("Policies", [
        ("What is your late policy?", "Please arrive on time. There is a 15-minute grace period. After that, a $25 late fee applies."),
        ("What is your cancellation policy?", "Cancellations must be made at least 24 hours before your appointment. No-call, no-shows are charged half the service fee."),
        ("Can I bring a guest?", "No extra guests are allowed. Clients 16 and up may come alone. Clients under 16 must be accompanied by an adult."),
        ("Do you do kids' hair?", 'Yes. There is a separate <a href="/kids-braids/">kids menu</a>. Clients under 16 must have an adult with them.'),
    ]),
    ("Prep &amp; add-ons", [
        ("How should I prepare my natural hair?", "Unless you booked a take-down or other extra service, come with your hair out of braids and free of any glue. Shampoo is included free of charge. Take-down is an add-on."),
        ("Is hair included with braid services?", 'Not for most braid styles. Bring your own hair or choose the hair add-on when you book. Miracle Knots need a 4-bag minimum (2 bags for kids). See the <a href="/braids/">braid menu</a>.'),
        ("How do I add curls, a wash or a cut?", "Add any extra styling or service, such as curling, crimping, a hair wash or cutting, as an “add-on” when you book. That reserves the extra time."),
        ("How do I drop off my hair before my appointment?", "All drop-offs must include your name and appointment date and time. Text or email to schedule the drop-off."),
    ]),
    ("Payment &amp; location", [
        ("What forms of payment do you accept?", "Apple Pay, Cash App, Zelle, cash and card."),
        ("Where is Dlux Beauty located?", f'Dlux Beauty is on Murphy Rd in Stafford, TX. Your exact address is in your booking confirmation. See <a href="/contact/">contact &amp; directions</a>.'),
        ("What are your hours?", "Monday through Friday 9 AM to 9 PM, Saturday and Sunday 7 AM to 5 PM. Appointments after 7 PM carry an after-hours fee."),
    ]),
]


def faq_body(p):
    groups = []
    for title, items in FAQ_GROUPS:
        groups.append(f'<div class="faq-group"><h2>{title}</h2>{mini_faq(items)}</div>')
    return f"""{banner(p, "Booking, deposits, prep and policy answers for Dlux Beauty clients.")}
<section class="section">
  <div class="wrap prose" style="margin:0 auto">{''.join(groups)}</div>
</section>
{cta_band('Still have a question?', f'Call or text {BIZ["phone"]} or email {BIZ["email"]}.')}"""


page("/faq/", "Booking FAQs & Salon Policies | Dlux Beauty",
     "Answers on deposits, late and cancellation policies, guests and kids, hair prep, add-ons, hair drop-offs and payment at Dlux Beauty in Stafford, TX.",
     "Frequently Asked Questions", HOME + [("/faq/", "FAQ")], faq_body,
     schema=[faq_schema([(t, [(q, a) for q, a in items]) for t, items in FAQ_GROUPS])])


# Contact ---------------------------------------------------------------------
def contact_body(p):
    opts = "".join(f"<option>{esc(l)}</option>" for _, l in SERVICE_PAGES)
    return f"""{banner(p, "Call, text or email Dlux Beauty in Stafford, TX. To book, use the online booking page.")}
<section class="section">
  <div class="wrap split" style="align-items:start">
    <div>
      <span class="eyebrow">Get in touch</span>
      <h2>Contact Dlux Beauty</h2>
      <ul class="contact-list">
        <li>{icon('phone', 'i ic')}<div><strong>Call or text</strong><a href="tel:{BIZ['phone_e164']}">{BIZ['phone']}</a></div></li>
        <li>{icon('mail', 'i ic')}<div><strong>Email</strong><a href="mailto:{BIZ['email']}">{BIZ['email']}</a></div></li>
        <li>{icon('pin', 'i ic')}<div><strong>Location</strong>{LOCATION_TEXT}<br><span class="small muted">Exact address is included in your booking confirmation.</span></div></li>
        <li>{icon('ig', 'i ic')}<div><strong>Instagram</strong>{BIZ['instagram']}</div></li>
      </ul>
      <h3>Hours</h3>
      <table class="hours"><tbody>{hours_rows()}</tbody></table>
      <p class="small muted mt-30">Appointments after 7 PM carry an after-hours fee.</p>
      {todo('Map &amp; address', '<p>Confirm the full street address and whether it should be public. If yes, add a Google Maps embed and directions here.</p>')}
    </div>
    <div>
      <h2>Send a message</h2>
      <p>For questions about services or availability. To book, use the <a href="/book/">booking page</a>.</p>
      <form class="form" name="contact" method="POST" action="/contact/thanks/" data-netlify="true" netlify-honeypot="company">
        <input type="hidden" name="form-name" value="contact">
        <p class="hp"><label>Leave this empty <input name="company"></label></p>
        <div class="row2">
          <div><label for="f-name">Name</label><input id="f-name" name="name" autocomplete="name" required></div>
          <div><label for="f-phone">Phone</label><input id="f-phone" name="phone" type="tel" autocomplete="tel" required></div>
        </div>
        <div><label for="f-email">Email</label><input id="f-email" name="email" type="email" autocomplete="email"></div>
        <div><label for="f-svc">Service</label><select id="f-svc" name="service"><option value="">Choose a service</option>{opts}<option>Something else</option></select></div>
        <div><label for="f-msg">Message</label><textarea id="f-msg" name="message" rows="5" required></textarea></div>
        <div><button class="btn" type="submit">Send message</button></div>
      </form>
    </div>
  </div>
</section>
{cta_band()}"""


page("/contact/", "Contact Dlux Beauty | Hair Studio in Stafford, TX",
     f"Contact Dlux Beauty on Murphy Rd in Stafford, TX. Call or text {BIZ['phone']}, email {BIZ['email']}, or send a message. Open 7 days.",
     "Contact Us", HOME + [("/contact/", "Contact")], contact_body)


def thanks_body(p):
    return f"""{banner(p)}
<section class="section"><div class="wrap center prose" style="margin:0 auto">
<p class="lead">Thanks for reaching out. Denise will get back to you soon. For faster help, call or text <a href="tel:{BIZ['phone_e164']}">{BIZ['phone']}</a>.</p>
<div class="btn-row" style="justify-content:center"><a class="btn" href="{book_href()}">Book Now</a><a class="btn btn--ghost" href="/services/">Browse services</a></div>
</div></section>"""


page("/contact/thanks/", "Message Sent | Dlux Beauty", "Thanks for contacting Dlux Beauty in Stafford, TX.",
     "Message Sent", HOME + [("/contact/", "Contact"), ("/contact/thanks/", "Message sent")], thanks_body, noindex=True, sitemap=False)


# Book ------------------------------------------------------------------------
def book_body(p):
    if BOOKING_URL:
        main_cta = f'<a class="btn" href="{BOOKING_URL}" rel="noopener">Book online</a>'
        note = ""
    else:
        main_cta = f'<a class="btn" href="tel:{BIZ["phone_e164"]}">Call or text {BIZ["phone"]}</a>'
        note = todo("Booking link", "<p>Add the Acuity Scheduling URL in <code>tools/build.py</code> (BOOKING_URL) to turn on the Book online button.</p>")
    pays = "".join(f"<li>{esc(x)}</li>" for x in BIZ["payments"])
    return f"""{banner(p, "Hello beauty, ready to book? Please read the policies below before choosing your appointment.")}
<section class="section">
  <div class="wrap split" style="align-items:start">
    <div>
      <span class="eyebrow">How it works</span>
      <h2>Book in three steps</h2>
      <ol class="steps">
        <li><h3>Pick your category</h3><p>Braid styles, hair weaves, natural hair care, men's styles or kids only.</p></li>
        <li><h3>Choose your style &amp; add-ons</h3><p>Add hair, curling, a wash, a cut or a take-down as an add-on so enough time is reserved.</p></li>
        <li><h3>Pay your $25 deposit</h3><p>The non-refundable deposit holds your time and goes toward your service.</p></li>
      </ol>
      <div class="btn-row mt-30">{main_cta}<a class="btn btn--ghost" href="/services/">Compare prices first</a></div>
    </div>
    <div>
      {note}
      <div class="note-box"><p><strong>After-hours appointments:</strong> appointments after 7 PM carry an after-hours fee. If the booking page won't show the time you want, book any open spot and text {BIZ['phone']} with the date, time and style you want, or send your deposit by Zelle or Cash App with those details.</p></div>
      <h3>Payment options</h3>
      <ul class="pay-list">{pays}</ul>
      <h3 class="mt-30">{icon('gift')} Gift certificates</h3>
      <p>Gift certificates are available through the online booking page.</p>
    </div>
  </div>
</section>
<section class="section section--dark" id="policies">
  <div class="wrap">
    <div class="title-area"><span class="eyebrow">Please read carefully</span><h2>Booking policies</h2></div>
    <div class="grid g4">{policy_cards()}</div>
    <div class="grid g2 mt-50">
      <div class="policy">{icon('alert', 'i ic')}<h3>Styling add-ons</h3><p>If you want any extra styling or service, such as curling, crimping, a hair wash or cutting, add it as an “add-on” when you book.</p></div>
      <div class="policy">{icon('alert', 'i ic')}<h3>Natural hair prep</h3><p>Unless you are paying for an extra service, your natural hair must not be braided and must be free of any glue. Shampoo is free of charge. Take-down is an add-on.</p></div>
      <div class="policy">{icon('alert', 'i ic')}<h3>Hair drop-offs</h3><p>All drop-offs must include your name and appointment date and time. Email or text to schedule a drop-off.</p></div>
      <div class="policy">{icon('alert', 'i ic')}<h3>After hours</h3><p>Booking after 7 PM carries an after-hours fee. Text with your preferred time, date and style if the site won't let you book it.</p></div>
    </div>
  </div>
</section>
{cta_band('Thank you for booking with us', f'Questions before you book? Call or text {BIZ["phone"]} or see the <a href="/faq/" style="color:var(--gold-lt)">FAQ</a>.')}"""


page("/book/", "Book an Appointment | Dlux Beauty Stafford, TX",
     "Book braids, sew-ins, wig installs, silk press or natural hair care at Dlux Beauty in Stafford, TX. $25 deposit holds your spot. Read policies and book.",
     "Book an Appointment", HOME + [("/book/", "Book Now")], book_body)


# 404 -------------------------------------------------------------------------
def nf_body(p):
    return f"""{banner(p, "That page isn't here. Try one of these instead.")}
<section class="section"><div class="wrap">{service_cards()}</div></section>"""


page("/404", "Page Not Found | Dlux Beauty", "The page you were looking for could not be found.",
     "Page Not Found", HOME + [("/404", "Not found")], nf_body, noindex=True, sitemap=False)


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------
def fix_home_banner():
    # Home renders its own hero instead of a banner; h1 lives in the hero.
    pass


def main():
    for p in PAGES:
        write(p["path"], render(p))
    urls = []
    for p in PAGES:
        if not p["sitemap"]:
            continue
        pri = "1.0" if p["path"] == "/" else ("0.9" if p["path"] in [h for h, _ in SERVICE_PAGES] or p["path"] in ("/services/", "/book/") else "0.7")
        urls.append(f"  <url><loc>{SITE_URL}{p['path']}</loc><lastmod>{LASTMOD}</lastmod><priority>{pri}</priority></url>")
    with open(os.path.join(PUBLIC, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(urls) + "\n</urlset>\n")
    with open(os.path.join(PUBLIC, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n")
    print(f"Built {len(PAGES)} pages, {len(urls)} in sitemap. INDEXABLE={INDEXABLE}")


if __name__ == "__main__":
    main()
