"""Assemble the redesigned cafekokomo.com pages (index.html, menu.html, 404.html).

Reuses the live site's exact menu cards, structured data and booking/order pop-ups
from repo-latest/index.html so prices, diet dots and GA4 hooks stay identical.
Usage: python3 build.py <repo-latest dir> <redesign dir> <menu_items.json>
"""
import html
import json
import re
import sys

SRC, OUT, ITEMS = sys.argv[1], sys.argv[2], sys.argv[3]
old = open(f"{SRC}/index.html", encoding="utf-8").read()
items = {html.unescape(i["name"]): i for i in json.load(open(ITEMS, encoding="utf-8"))}


def between(text, start, end, include_start=True):
    i = text.index(start)
    j = text.index(end, i + len(start))
    return text[i if include_start else i + len(start):j]


# ---- carried-over blocks -------------------------------------------------
jsonld = between(old, '<script type="application/ld+json">', "</script>") + "</script>"
jsonld = jsonld.replace('"hasMenu": "https://cafekokomo.com/#menu"', '"hasMenu": "https://cafekokomo.com/menu"')
jsonld = jsonld.replace("https://cafekokomo.com/assets/images/media__1779297184171.jpg",
                        "https://cafekokomo.com/assets/images/v2/og-cafe-kokomo.jpg")
assert '"hasMenu": "https://cafekokomo.com/menu"' in jsonld
_ld = json.loads(jsonld[jsonld.index(">") + 1:jsonld.rindex("</script>")])
if "https://www.instagram.com/cafekokomo/" not in _ld["sameAs"]:
    _ld["sameAs"].append("https://www.instagram.com/cafekokomo/")
_ld["amenityFeature"] = [{"@type": "LocationFeatureSpecification", "name": n, "value": True}
                         for n in ("Wi-Fi", "Power outlets", "Outdoor seating", "Table reservations", "Vegetarian options")]
jsonld = '<script type="application/ld+json">\n    ' + json.dumps(_ld, ensure_ascii=False) + "\n    </script>"
IG = "https://www.instagram.com/cafekokomo/"
IG_SVG = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="2" y="2" width="20" height="20" rx="5"/><path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"/><line x1="17.5" y1="6.5" x2="17.51" y2="6.5"/></svg>'

menu_sec = between(old, '<section id="menu"', "</section>")
menu_body = menu_sec[menu_sec.index("<!-- Menu Search Bar -->"):]
while menu_body.count("</div>") > menu_body.count("<div"):            # drop the old .container close + the stray extra </div>
    menu_body = menu_body[:menu_body.rstrip().rindex("</div>")]
assert menu_body.count("<div") == menu_body.count("</div>"), "menu block div imbalance"
assert menu_body.count('class="menu-item-card"') == 128
menu_body = menu_body.replace("Search signature brews, bites, or desserts...", "Search the menu: latte, pasta, cheesecake…")
menu_body = menu_body.replace(" reveal-on-scroll", "")

popups = between(old, '<a href="javascript:void(0)" id="whatsapp-floating-btn"', "<!-- Leaflet Map JS -->")
popups = popups.replace("Experience the sensory curation of Cafe Kokomo. in the comfort of\n                your sanctuary.",
                        "Delivered from our kitchen in Santacruz East.")
popups = re.sub(r"Experience the sensory curation of Cafe Kokomo\.\s+in the comfort of\s+your sanctuary\.",
                "Delivered from our kitchen in Santacruz East.", popups)
assert "sensory curation" not in popups
for a, b in [("1 Guest (Solo)", "1 guest"), ("2 Guests (Intimate)", "2 guests"), ("3 Guests (Small Group)", "3 guests"),
             ("4 Guests (Standard)", "4 guests"), ("5 Guests (Gathering)", "5 guests"), ("6 Guests (Gathering)", "6 guests"),
             ("7+ Guests (Large Group)", "7+ guests"), ("Desired Date", "Date"), ("Preferred Time", "Time"),
             ("Special Requests (Dietary/Seating)", "Anything we should know?"), ("Send WhatsApp Reservation", "Send booking request on WhatsApp"),
             ("e.g. Low seating preference, dietary restrictions...", "e.g. window seat, birthday, allergies"), ("Full Name", "Your name")]:
    assert a in popups, a
    popups = popups.replace(a, b)
popups = re.sub(r'\s*<option[^>]*>\s*11:00 PM\s*</option>', "", popups)          # 11 PM is closing time
assert "11:00 PM" not in popups
popups = re.sub(r'<p class="wa-reservation-footer-text">.*?</p>', '<p class="wa-reservation-footer-text">This opens WhatsApp with your request. We\'ll reply there to confirm your table.</p>', popups, flags=re.S)
assert "encrypted" not in popups and "Concierge" not in popups

popups = re.sub(r'(src|href)="(?!https?:|/|#|mailto:|tel:|javascript:)', r'\1="/', popups)   # root-relative so sub-pages work
menu_body = re.sub(r'(src|href)="(?!https?:|/|#|mailto:|tel:|javascript:)', r'\1="/', menu_body)
directions = re.search(r'href="(https://www\.google\.com/maps/dir/\?api=1&destination=[^"]+)"', old).group(1)
reviews_url = "https://www.google.com/maps/place/Cafe+Kokomo/@19.0774537,72.8493026,17z/data=!4m8!3m7!1s0x3be7c92dd3fb1915:0x5bf202a9900faa42!8m2!3d19.0774537!4d72.8493026!9m1!1b1"

# real guest quotes from the current site (skip the one-liner)
rev_seg = between(old, 'id="reviews"', 'id="instagram"')
names = re.findall(r'reviewer-name">([^<]+)', rev_seg)
texts = [re.sub(r"\s+", " ", html.unescape(re.sub("<[^>]+>", "", t))).strip()
         for t in re.findall(r'class="review-(?:body|text|content)[^"]*">\s*(.*?)\s*</p>', rev_seg, re.S)]
quotes, seen = [], set()
for n, t in zip(names, texts):
    if n in seen or len(t) < 40:
        continue
    seen.add(n)
    quotes.append((n, t))

FAQ = [
    ("What time is Cafe Kokomo open?", "Every day, 11 AM to 11 PM."),
    ("Where exactly is the cafe?", "4, Pratap CHS Ltd, Shivaji Road, near Vakola Bridge, Santacruz East, Mumbai 400055. It's an 11-minute walk from Nap Manor Hostels."),
    ("Do I need to book a table?", "You can walk in. To book ahead, use Book a table on this site: it opens WhatsApp with your request and we reply to confirm."),
    ("Can I book for a group or a celebration?", "Yes. For 7 or more people, choose 7+ guests when you book and tell us the occasion in the notes, so we can set up the tables."),
    ("Do you have vegetarian options?", "Yes. 103 of the 128 items on the menu are vegetarian. Every dish carries a dot: green for veg, yellow for egg and red for non-veg, and the menu page has a Veg only filter."),
    ("Is there Wi-Fi? Can I work from the cafe?", "Yes. There's Wi-Fi and plug points, and you're welcome to stay through the afternoon."),
    ("Do you serve breakfast all day?", "Yes. The all-day breakfast includes the English Breakfast, omelettes, scrambled eggs, bagels and the Loaded Pancake Stacker."),
    ("Do you have matcha?", "Yes, five matcha drinks at ₹299: Iced Matcha, Iced Coconut Matcha, Iced Strawberry Glow Matcha, and the Velvet Vanilla Matcha, hot or iced."),
    ("Do you have anything gluten-free?", "The World's Best Chocolate Cake is marked gluten-free on our menu (it contains egg). Ask us about other dishes."),
    ("Do you deliver?", "Yes, through Swiggy and Zomato. Delivery prices are set separately from the dine-in prices on this site."),
    ("How can I pay?", "Cash, card or UPI."),
    ("What are Sip & Paint and Blind Date Book?", "Sip & Paint (₹149) gives you a canvas, brushes and paints at your table, and the painting goes home with you. Blind Date Book (₹199) is a hand-wrapped surprise book in the genre you choose."),
    ("How much does a meal cost?", "An espresso is ₹149 and most pastas and sandwiches are ₹329 to ₹399. A meal for two usually comes to about ₹400 to ₹600."),
]
FAQ_LD = '    <script type="application/ld+json">\n    ' + json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
    {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}, ensure_ascii=False) + "\n    </script>\n"
MENU_CRUMB_LD = '    <script type="application/ld+json">\n    ' + json.dumps({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
    {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://cafekokomo.com/"},
    {"@type": "ListItem", "position": 2, "name": "Menu", "item": "https://cafekokomo.com/menu"}]}) + "\n    </script>\n"

DIET = {"veg": ("diet-veg", "Veg"), "egg": ("diet-egg", "Contains egg"), "nonveg": ("diet-nonveg", "Non-veg")}


def dot(name):
    cls, label = DIET.get(items[name]["diet"], ("", ""))
    return f'<span class="diet-dot {cls}" role="img" aria-label="{label}"></span>' if cls else ""


def price(name):
    return items[name]["price"]


# ---- shared chrome -------------------------------------------------------
def head(title, desc, canonical, extra=""):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{desc}">
    <link rel="canonical" href="{canonical}">
    <meta name="theme-color" content="#F5F5F2">
    <meta property="og:type" content="website">
    <meta property="og:url" content="{canonical}">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{desc}">
    <meta property="og:image" content="https://cafekokomo.com/assets/images/v2/og-cafe-kokomo.jpg">
    <meta property="og:image:type" content="image/jpeg">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="630">
    <meta property="og:image:alt" content="Cafe Kokomo's glass front on Shivaji Road at night, with the line-art mural inside">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{title}">
    <meta name="twitter:description" content="{desc}">
    <meta name="twitter:image" content="https://cafekokomo.com/assets/images/v2/og-cafe-kokomo.jpg">
    <link rel="apple-touch-icon" sizes="180x180" href="/favicon/apple-touch-icon.png">
    <link rel="icon" type="image/png" sizes="32x32" href="/favicon/favicon-32x32.png">
    <link rel="icon" type="image/png" sizes="16x16" href="/favicon/favicon-16x16.png">
    <link rel="manifest" href="/favicon/site.webmanifest">
    <link rel="shortcut icon" href="/favicon/favicon.ico">
    <link href="https://api.fontshare.com/v2/css?f[]=satoshi@400,500,700,900&display=swap" rel="stylesheet">
    <link href="https://api.fontshare.com/v2/css?f[]=gambetta@400,401,500,501&display=swap" rel="stylesheet">
{extra}    <link rel="stylesheet" href="/components.css">
    <link rel="stylesheet" href="/kokomo.css">
    <script src="https://unpkg.com/lucide@1.31.0/dist/umd/lucide.min.js" integrity="sha384-/ApD3KXMqTmTxEJjuldaZDgdJj7/Hox2LRuKqV3rC7Bu/wE4obLaJRjF1rLHNP57" crossorigin="anonymous"></script>
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-KW30HD1D45"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());
      gtag('config', 'G-KW30HD1D45');
    </script>
    {jsonld}
</head>
"""


LEAFLET_CSS = '    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha384-sHL9NAb7lN7rfvG5lfHpm643Xkcjzp4jFvuavGOndn6pjVqS6ny56CAt3nsEVT4H" crossorigin="anonymous">\n'
LEAFLET_JS = '<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha384-cxOPjt7s7Iz04uaHJceBmS+qpjv2JkIHNVcuOrM+YHwZOmJGBXI00mdUXEq65HTH" crossorigin="anonymous"></script>\n'


def nav(on_menu=False, sub=False):
    p = "/" if (on_menu or sub) else ""
    cur = ' aria-current="page"' if on_menu else ""
    links = [("/menu", "Menu", cur), (f"{p}#experiences", "Experiences", ""), (f"{p}#space", "The space", ""),
             (f"{p}#reviews", "Reviews", ""), (f"{p}#faq", "FAQ", ""), (f"{p}#visit", "Visit", "")]
    a = "\n".join(f'            <a class="nav-link" href="{h}"{c}>{t}</a>' for h, t, c in links)
    m = "\n".join(f'        <a class="mobile-nav-link" href="{h}">{t}</a>' for h, t, c in links)
    return f"""<body{' class="menu-page"' if on_menu else ''}>
<a class="skip-link" href="#main">Skip to content</a>
<header class="site-nav">
    <div class="wrap nav-inner">
        <a href="/" class="logo" aria-label="Cafe Kokomo home">cafe kokomo<span class="logo-dot">.</span></a>
        <nav class="nav-links" aria-label="Main">
{a}
        </nav>
        <div class="nav-cta">
            <button type="button" class="btn btn-outline" data-open-order>Order online</button>
            <a href="javascript:void(0)" class="btn btn-dark" data-open-reservation>Book a table</a>
            <button type="button" class="nav-toggle" aria-label="Open menu" aria-expanded="false" aria-controls="mobile-panel"><span></span><span></span><span></span></button>
        </div>
    </div>
</header>
<div class="mobile-panel" id="mobile-panel">
{m}
        <a class="mobile-nav-link" href="{IG}" target="_blank" rel="noopener">Instagram</a>
        <button type="button" class="btn btn-outline" data-open-order>Order online</button>
</div>
"""


FOOTER = f"""<footer class="site-footer">
    <div class="wrap">
        <div class="footer-top">
            <div>
                <a href="/" class="logo">cafe kokomo<span class="logo-dot">.</span></a>
                <p>Coffee, comfort food and a table to stay a while. Shivaji Road, Santacruz East, since 2021.</p>
            </div>
            <a href="javascript:void(0)" class="btn btn-light" data-open-reservation>Book a table</a>
        </div>
        <div class="footer-cols">
            <div>
                <h4>Visit</h4>
                <a href="{directions}" target="_blank" rel="noopener">4, Pratap CHS Ltd, Shivaji Road,<br>near Vakola Bridge, Santacruz East,<br>Mumbai 400055</a>
                <a href="/#visit">Open daily, 11 AM – 11 PM</a>
            </div>
            <div>
                <h4>Contact</h4>
                <a href="tel:+918591515657">+91 85915 15657</a>
                <a href="tel:+918879440033">+91 88794 40033</a>
                <a href="mailto:info@cafekokomo.com">info@cafekokomo.com</a>
            </div>
            <div>
                <h4>Explore</h4>
                <a href="/menu">Full menu</a>
                <a href="/#experiences">Experiences</a>
                <a href="/#reviews">Reviews</a>
                <a href="https://www.instagram.com/cafekokomo" target="_blank" rel="noopener">Instagram @cafekokomo</a>
                <a href="/#careers">Work with us</a>
            </div>
            <div>
                <h4>Guides</h4>
                <a href="/guides/work-friendly-cafe-santacruz-east">Work-friendly cafe</a>
                <a href="/guides/matcha-santacruz-east">Matcha in Santacruz East</a>
                <a href="/guides/veg-friendly-cafe-vakola">Veg-friendly cafe</a>
                <a href="/guides/cafe-near-bkc">Cafe near BKC</a>
            </div>
            <div>
                <h4>Order in</h4>
                <a href="https://www.swiggy.com/city/mumbai/cafe-kokomo-santacruz-east-rest431996" target="_blank" rel="noopener noreferrer">Swiggy</a>
                <a href="https://www.zomato.com/mumbai/cafe-kokomo-santacruz-east/order" target="_blank" rel="noopener noreferrer">Zomato</a>
            </div>
        </div>
        <div class="footer-bottom">
            <span>&copy; 2026 Cafe Kokomo · FSSAI Reg. No. 21521020000524 · <a href="/privacy">Privacy</a></span>
            <span>Staying nearby? <a href="https://napmanorhostels.com/" target="_blank" rel="noopener">Nap Manor Hostels</a> is an 11-minute walk away.</span>
        </div>
    </div>
</footer>
"""


def tail(with_map):
    return "\n" + popups + (LEAFLET_JS if with_map else "") + '<script src="/script.js"></script>\n</body>\n</html>\n'


# ---- homepage ------------------------------------------------------------
best = [("The Classic Cold Coffee", "Cold coffee"), ("Cappuccino", "Hot coffee"), ("Alfredo Pasta", "Pasta"),
        ("Americano", "Hot coffee"), ("Seasoned Fries", "Bites"), ("Pink Sauce Pasta", "Pasta"),
        ("Iced Americano", "Iced coffee"), ("Iced hazelnut latte", "Iced coffee")]
best_li = "\n".join(
    f'                    <li><span class="name">{dot(n)}{html.escape(n)}<span class="cat">{c}</span></span><span class="price">{price(n)}</span></li>'
    for n, c in best)

dishes = [("Espresso Tonic", "espresso-tonic", True), ("Affogato", "affogato", False), ("Hummus & Pita", "hummus-pita", False),
          ("Butter Croissant", "croissant", False), ("New York Cheesecake", "ny-cheesecake", False),
          ("Kokomo Special Loaded Nachos", "loaded-nachos", True), ("Oreo Milkshake", "oreo-shake", False),
          ("Classic Hot Chocolate", "hot-chocolate", False)]
dish_html = "\n".join(
    f"""                <figure class="dish{' wide' if w else ''} reveal-on-scroll">
                    <img loading="lazy" decoding="async" src="/assets/images/v2/{img}-800.webp" srcset="/assets/images/v2/{img}-480.webp 480w, /assets/images/v2/{img}-800.webp 800w" sizes="(max-width: 640px) 50vw, {'50vw' if w else '25vw'}" alt="{html.escape(n)} at Cafe Kokomo" width="800" height="1000">
                    <figcaption><span>{dot(n)}{html.escape(n)}</span><span class="price">{price(n)}</span></figcaption>
                </figure>""" for n, img, w in dishes)

ig_html = "\n".join(
    f'                <a class="ig-tile reveal-on-scroll" href="{IG}" target="_blank" rel="noopener" aria-label="{alt} — open @cafekokomo on Instagram"><img loading="lazy" decoding="async" src="/assets/images/v2/{img}-600.webp" alt="{alt}" width="600" height="600"><span class="ig-icon">{IG_SVG}</span></a>'
    for img, alt in [("ig-barista", "Barista pouring latte art"), ("ig-frappe", "Coffee frappe"), ("ig-mural", "The line-art mural and tables"),
                     ("ig-popcorn", "Classic chicken popcorn"), ("ig-latte", "Latte with heart latte art"), ("ig-terrace", "Tables outside the cafe in the evening")])
quote_html = "\n".join(
    f"""                <blockquote class="quote reveal-on-scroll"><p>{html.escape(t)}</p><footer><b>{html.escape(n)}</b><span aria-label="5 stars">★★★★★</span></footer></blockquote>"""
    for n, t in quotes[:5])

qb_times = "".join(f'<option value="{t}"{" selected" if t == "1:00 PM" else ""}>{t}</option>' for t in ["11:00 AM","12:00 PM","1:00 PM","2:00 PM","3:00 PM","4:00 PM","5:00 PM","6:00 PM","7:00 PM","8:00 PM","9:00 PM","10:00 PM"])
qb_guests = "".join(f'<option value="{g}"{" selected" if g == "2 guests" else ""}>{g}</option>' for g in ["1 guest", "2 guests", "3 guests", "4 guests", "5 guests", "6 guests", "7+ guests"])
faq_html = "\n".join(f'                <details class="faq-item"><summary>{html.escape(q)}</summary><p>{html.escape(a)}</p></details>' for q, a in FAQ)
ticker_items = ["Open every day, 11 AM – 11 PM", "Matcha bar", "All-day breakfast", "Sip &amp; Paint, ₹149",
                "Blind Date Book, ₹199", "Veg, egg and non-veg marked on every dish", "11-minute walk from Nap Manor Hostels",
                "Order in on Swiggy &amp; Zomato"]
ticker = "".join(f"<span>{t}</span>" for t in ticker_items)

index = head("Cafe Kokomo | Coffee & comfort food in Santacruz East, Mumbai",
             "Cafe Kokomo is a cozy, tropical-themed cafe on Shivaji Road, near Vakola Bridge, Santacruz East: single-origin coffee, a matcha bar, all-day breakfast, pasta and bakes. Open every day, 11 AM to 11 PM.",
             "https://cafekokomo.com/", FAQ_LD + LEAFLET_CSS + '    <link rel="preload" as="image" href="/assets/images/v2/shopfront-night-1600.webp" imagesrcset="/assets/images/v2/shopfront-night-800.webp 800w, /assets/images/v2/shopfront-night-1600.webp 1600w" imagesizes="(max-width: 900px) 100vw, 50vw">\n') + nav() + f"""<main id="main">
    <section class="hero" id="home">
        <div class="wrap hero-grid">
            <div>
                <span class="eyebrow">Santacruz East · since 2021</span>
                <h1>Coffee first. <span class="accent">Then stay a while.</span></h1>
                <p class="hero-lede">Single-origin coffee, a matcha bar, all-day breakfast, pasta and bakes on Shivaji Road, near Vakola Bridge. Open every day, 11 AM to 11 PM.</p>
                <div class="hero-meta">
                    <p class="hero-status" id="open-status" aria-live="polite"></p>
                    <span class="addr">4, Pratap CHS, Shivaji Road</span>
                </div>
                <div class="hero-actions">
                    <a href="javascript:void(0)" class="btn btn-dark" data-open-reservation>Book a table</a>
                    <button type="button" class="btn btn-outline" data-open-order>Order online</button>
                    <a href="/menu" class="text-link">See the full menu</a>
                </div>
                <div class="proof">
                    <a class="proof-item" href="{reviews_url}" target="_blank" rel="noopener"><strong>4.6</strong><span class="star">★</span><span>Google · 335 reviews</span></a>
                    <a class="proof-item" href="https://www.zomato.com/mumbai/cafe-kokomo-santacruz-east" target="_blank" rel="noopener"><strong>4.4</strong><span class="star">★</span><span>Zomato</span></a>
                    <a class="proof-item" href="https://www.swiggy.com/city/mumbai/cafe-kokomo-santacruz-east-rest431996" target="_blank" rel="noopener"><strong>4.7</strong><span class="star">★</span><span>Swiggy · 1,000+ ratings</span></a>
                </div>
            </div>
            <div class="hero-visual">
                <div class="hero-photo-main">
                    <img fetchpriority="high" decoding="async" src="/assets/images/v2/shopfront-night-1600.webp" srcset="/assets/images/v2/shopfront-night-800.webp 800w, /assets/images/v2/shopfront-night-1600.webp 1600w" sizes="(max-width: 900px) 100vw, 50vw" alt="Cafe Kokomo's glass front and sign on Shivaji Road at night" width="1600" height="1067">
                </div>
                <div class="hero-photo-card">
                    <img decoding="async" src="/assets/images/v2/cappuccino-480.webp" alt="Cappuccino with latte art on a bed of coffee beans" width="480" height="600">
                </div>
                <div class="hero-stamp"><strong>Est. 2021</strong>Near Vakola Bridge</div>
            </div>
        </div>
    </section>

    <section class="bookbar-wrap" aria-label="Book a table">
        <div class="wrap">
            <form class="bookbar" id="quick-book">
                <div class="bb-title"><strong>Book a table</strong><span>We confirm on WhatsApp</span></div>
                <label>Date<input type="date" id="qb-date" required></label>
                <label>Time<select id="qb-time">{qb_times}</select></label>
                <label>Guests<select id="qb-guests">{qb_guests}</select></label>
                <button class="btn btn-dark" type="submit">Continue</button>
            </form>
        </div>
    </section>

    <div class="ticker" aria-label="Quick facts"><div class="ticker-track">{ticker}{ticker}</div></div>

    <section class="section" id="most-ordered">
        <div class="wrap ordered-grid">
            <div class="ordered-photos reveal-on-scroll">
                <figure><img loading="lazy" decoding="async" src="/assets/images/v2/latte-800.webp" alt="Latte with heart latte art" width="800" height="1000"></figure>
                <figure><img loading="lazy" decoding="async" src="/assets/images/v2/fries-800.webp" alt="A bowl of seasoned fries" width="800" height="1000"></figure>
            </div>
            <div>
                <span class="eyebrow">Most ordered</span>
                <h2 class="section-title-xl" style="font-size: clamp(2.25rem, 5.2vw, 4rem); font-weight: 900; margin: 14px 0 12px;">What Santacruz East <span class="accent">actually</span> orders.</h2>
                <p style="color: var(--color-text-secondary); max-width: 46ch;">Our eight most-ordered dishes and drinks, counted from our own bills, 13 August to 11 October 2026.</p>
                <ol class="ordered-list reveal-on-scroll">
{best_li}
                </ol>
                <p class="ordered-note"><a class="text-link" href="/menu">See all 128 items on the menu</a></p>
            </div>
        </div>
    </section>

    <section class="section band" id="signatures">
        <div class="wrap">
            <div class="section-head">
                <div><span class="eyebrow">On the table</span><h2>Worth the <span class="accent">photo.</span></h2></div>
                <p>A few dishes we're known for, shot in the cafe. Every dish on the menu carries a veg, egg or non-veg dot.</p>
            </div>
            <div class="dish-grid">
{dish_html}
            </div>
            <div class="dishes-foot"><span>Prices shown are dine-in prices.</span><a class="btn btn-dark" href="/menu">Open the full menu</a></div>
        </div>
    </section>

    <section class="section" id="space">
        <div class="wrap">
            <div class="space-grid">
                <div class="space-main reveal-on-scroll"><img loading="lazy" decoding="async" src="/assets/images/v2/mural-1600.webp" srcset="/assets/images/v2/mural-800.webp 800w, /assets/images/v2/mural-1600.webp 1600w" sizes="(max-width: 900px) 100vw, 60vw" alt="The black-and-white line-art mural with the kokomo name, above round black tables and white chairs" width="1600" height="1067"></div>
                <div class="space-copy">
                    <span class="eyebrow">The space</span>
                    <h2>Come for the coffee. <span class="accent">Stay for that wall.</span></h2>
                    <p>A cozy, tropical-themed cafe, and the black-and-white line-art mural is the first thing you see when you walk in. It's also the thing most people photograph.</p>
                    <p>Round black tables, white chairs, plants along the glass front, and a counter by the window for a quick coffee on your own.</p>
                    <p>Behind the counter: single-origin beans and custom roasts, latte art with award-winning microfoam, and a few greens we grow ourselves.</p>
                    <div class="space-facts">
                        <div><strong>2021</strong><span>Opened</span></div>
                        <div><strong>7 days</strong><span>11 AM – 11 PM</span></div>
                        <div><strong>128</strong><span>On the menu</span></div>
                    </div>
                </div>
            </div>
            <div class="space-strip">
                <figure class="reveal-on-scroll"><img loading="lazy" decoding="async" src="/assets/images/v2/coffee-bar-800.webp" alt="The coffee bar with grinder and cups" width="800" height="533"></figure>
                <figure class="reveal-on-scroll"><img loading="lazy" decoding="async" src="/assets/images/v2/window-bar-800.webp" alt="Window counter with tall wooden stools" width="800" height="533"></figure>
                <figure class="reveal-on-scroll"><img loading="lazy" decoding="async" src="/assets/images/v2/outdoor-night-800.webp" alt="Tables outside the glass front in the evening" width="800" height="533"></figure>
            </div>
        </div>
    </section>

    <section class="section band" id="experiences">
        <div class="wrap">
            <div class="section-head">
                <div><span class="eyebrow">Beyond the menu</span><h2>Things to do <span class="accent">besides eat.</span></h2></div>
                <p>Ask at the counter or add them to your order like any other item.</p>
            </div>
            <div class="exp-grid">
                <article class="exp-card feature reveal-on-scroll">
                    <span class="tag">At your table</span>
                    <h3>Sip &amp; Paint</h3>
                    <p>Your own canvas, brushes and paints. No experience needed, and the painting goes home with you.</p>
                    <span class="exp-price">₹149</span>
                </article>
                <article class="exp-card reveal-on-scroll">
                    <span class="tag">For readers</span>
                    <h3>Blind Date Book</h3>
                    <p>A hand-wrapped surprise book. Pick a genre and we'll choose the book.</p>
                    <span class="exp-price">₹199</span>
                </article>
                <article class="exp-card reveal-on-scroll">
                    <span class="tag">Work or catch up</span>
                    <h3>Stay as long as you like</h3>
                    <p>Wi-Fi, plug points and a quiet table through the afternoon. Book ahead for groups.</p>
                    <a href="javascript:void(0)" class="text-link" data-open-reservation>Book a table</a>
                </article>
            </div>
        </div>
    </section>

    <section class="section" id="reviews">
        <div class="wrap reviews-grid">
            <div class="reveal-on-scroll">
                <span class="eyebrow">Reviews</span>
                <div class="rating-big" style="margin-top: 18px;">4.6</div>
                <div class="rating-stars" aria-hidden="true">★★★★★</div>
                <p class="rating-sub">from 335 reviews on Google</p>
                <div class="rating-others">
                    <div><strong>4.4</strong><span>Zomato</span></div>
                    <div><strong>4.7</strong><span>Swiggy</span></div>
                </div>
                <a class="btn btn-outline" href="{reviews_url}" target="_blank" rel="noopener">Read them on Google</a>
            </div>
            <div class="quotes">
{quote_html}
            </div>
        </div>
    </section>

    <section class="section" id="instagram">
        <div class="wrap">
            <div class="section-head">
                <div><span class="eyebrow">Instagram</span><h2>Follow along <span class="accent">@cafekokomo</span></h2></div>
                <p>Photos of the food, the space and what's new at the cafe. Tap any photo to open our Instagram.</p>
            </div>
            <div class="ig-grid">
{ig_html}
            </div>
            <div class="dishes-foot"><span>@cafekokomo on Instagram</span><a class="btn btn-dark" href="{IG}" target="_blank" rel="noopener">{IG_SVG}Follow on Instagram</a></div>
        </div>
    </section>

    <section class="section" id="faq">
        <div class="wrap faq-grid">
            <div>
                <span class="eyebrow">FAQ</span>
                <h2 style="font-size: clamp(2.25rem, 5vw, 3.75rem); font-weight: 900; margin: 14px 0 16px;">Questions, <span class="accent">answered.</span></h2>
                <p style="color: var(--color-text-secondary); max-width: 34ch; margin-bottom: 24px;">Anything else? Call us on +91 85915 15657 or message us on WhatsApp.</p>
                <a href="javascript:void(0)" class="btn btn-dark" data-open-reservation>Book a table</a>
            </div>
            <div class="faq-list">
{faq_html}
            </div>
        </div>
    </section>

    <section class="careers-band" id="careers">
        <div class="wrap careers-inner">
            <div>
                <span class="eyebrow">Work with us</span>
                <h2>Make the coffee. <span class="accent">Join the team.</span></h2>
                <p>We're always happy to hear from baristas, cooks and service staff in and around Santacruz East. Email your CV with the role you want in the subject line.</p>
            </div>
            <a class="btn btn-dark" href="mailto:info@cafekokomo.com?subject=Job%20application%20-%20">Email your CV</a>
        </div>
    </section>

    <section class="section band" id="visit">
        <div class="wrap">
            <div class="section-head">
                <div><span class="eyebrow">Visit</span><h2>Find us near <span class="accent">Vakola Bridge.</span></h2></div>
                <p>On Shivaji Road in Santacruz East. Walk in, or book a table on WhatsApp and we'll confirm.</p>
            </div>
            <div class="visit-grid">
                <div class="visit-map" id="map-section"><div id="footer-map" role="region" aria-label="Map showing Cafe Kokomo"></div></div>
                <div class="visit-card">
                    <div><h3>Address</h3><address>Cafe Kokomo, 4, Pratap CHS Ltd, Shivaji Road, near Vakola Bridge, Santacruz East, Mumbai 400055</address></div>
                    <div><h3>Hours</h3><p>Open every day, 11 AM – 11 PM</p></div>
                    <div><h3>Call</h3><p><a href="tel:+918591515657">+91 85915 15657</a> · <a href="tel:+918879440033">+91 88794 40033</a></p></div>
                    <p class="visit-note">Staying at <a href="https://napmanorhostels.com/" target="_blank" rel="noopener">Nap Manor Hostels</a>? We're an 11-minute walk away.</p>
                    <div class="visit-actions">
                        <a class="btn btn-dark" href="{directions}" target="_blank" rel="noopener">Get directions</a>
                        <a class="btn btn-outline" href="javascript:void(0)" data-open-reservation>Book a table</a>
                    </div>
                </div>
            </div>
        </div>
    </section>
</main>
""" + FOOTER + tail(True)

# ---- menu page -----------------------------------------------------------
menu = head("Menu & prices | Cafe Kokomo, Santacruz East",
            "Cafe Kokomo's full dine-in menu with prices: coffee, matcha, frappes, teas, all-day breakfast, bites and croissants, pasta and sandwiches, desserts. Veg, egg and non-veg marked.",
            "https://cafekokomo.com/menu", MENU_CRUMB_LD) + nav(on_menu=True) + f"""<main id="main">
    <section class="page-head">
        <div class="wrap">
            <span class="eyebrow">Dine-in menu</span>
            <h1>The <span class="accent">menu.</span></h1>
            <p>All {len(items)} dishes and drinks with dine-in prices. Green dot is veg, yellow has egg, red is non-veg. Delivery prices on Swiggy and Zomato are different.</p>
            <div class="hero-actions">
                <a href="javascript:void(0)" class="btn btn-dark" data-open-reservation>Book a table</a>
                <button type="button" class="btn btn-outline" data-open-order>Order online</button>
            </div>
        </div>
    </section>
    <section id="menu" class="menu-section">
        <div class="wrap">
            {menu_body}
            <p class="menu-empty" id="menu-empty">Nothing matches that search. Try a shorter word, or clear the Veg only filter.</p>
        </div>
    </section>
</main>
""" + FOOTER + tail(False)

# ---- 404 -----------------------------------------------------------------
notfound = head("Page not found | Cafe Kokomo", "This page doesn't exist. Head back to Cafe Kokomo's home page or menu.",
                "https://cafekokomo.com/").replace('<link rel="canonical" href="https://cafekokomo.com/">', '<meta name="robots" content="noindex">') + nav(sub=True) + """<main id="main">
    <section class="page-head" style="min-height: 60vh;">
        <div class="wrap">
            <span class="eyebrow">404</span>
            <h1>This page <span class="accent">isn't here.</span></h1>
            <p>The link may be old. The menu and everything else are one click away.</p>
            <div class="hero-actions"><a class="btn btn-dark" href="/">Go to the home page</a><a class="btn btn-outline" href="/menu">See the menu</a></div>
        </div>
    </section>
</main>
""" + FOOTER + tail(False)

privacy = head("Privacy | Cafe Kokomo", "How cafekokomo.com handles your information: analytics, the WhatsApp booking form and the services the site loads.",
               "https://cafekokomo.com/privacy") + nav(sub=True) + """<main id="main">
    <section class="page-head">
        <div class="wrap prose">
            <span class="eyebrow">Privacy</span>
            <h1>Privacy, <span class="accent">plainly.</span></h1>
            <p>Last updated 13 October 2026. This page covers cafekokomo.com, run by Cafe Kokomo, 4, Pratap CHS Ltd, Shivaji Road, Santacruz East, Mumbai 400055.</p>
            <h2>What we measure</h2>
            <p>We use Google Analytics to count visits and see which pages people use and which buttons they tap (call, WhatsApp, directions, order online, book a table). It doesn't tell us who you are, and we don't run ads or sell data.</p>
            <h2>Booking a table</h2>
            <p>The booking form doesn't send anything to our server. It opens WhatsApp on your phone with your name, party size, date, time and notes filled in, and you choose whether to send it. We only see what you send us on WhatsApp, and we use it to confirm your table.</p>
            <h2>Services the site loads</h2>
            <p>Fonts come from Fontshare, icons and the map library from unpkg, map tiles from OpenStreetMap and analytics from Google. Like any website, these services see your IP address when your browser loads them. Order links take you to Swiggy or Zomato, whose own policies apply there.</p>
            <h2>Questions</h2>
            <p>Email <a href="mailto:info@cafekokomo.com">info@cafekokomo.com</a> or call +91 85915 15657.</p>
        </div>
    </section>
</main>
""" + FOOTER + tail(False)

DIRECTIONS_LINK = f'<a href="{directions}" target="_blank" rel="noopener">Get directions</a>'
VISIT_P = ("<p>Cafe Kokomo, 4, Pratap CHS Ltd, Shivaji Road, near Vakola Bridge, Santacruz East, Mumbai 400055. Open every day, 11 AM to 11 PM. "
           f"Call +91 85915 15657. {DIRECTIONS_LINK}. Staying at <a href=\"https://napmanorhostels.com/\" target=\"_blank\" rel=\"noopener\">Nap Manor Hostels</a>? We're an 11-minute walk away.</p>")
BKC_P = ("<p>By road the cafe is about 3.4 km from the SEBI building in BKC, 4.6 km from the US Consulate and 4.7 km from Jio World Centre "
         "(OpenStreetMap routing). How long it takes depends on traffic.</p>")
GUIDES = [
    dict(slug="work-friendly-cafe-santacruz-east", short="Work-friendly cafe",
         title="Work-friendly cafe in Santacruz East, Mumbai | Cafe Kokomo",
         desc="Cafe Kokomo near Vakola Bridge has Wi-Fi and plug points, opens 11 AM to 11 PM every day, and serves coffee from ₹149 with sandwiches and pasta for a long session.",
         h1='A work-friendly cafe <span class="accent">in Santacruz East.</span>',
         lede="Cafe Kokomo is on Shivaji Road, near Vakola Bridge, and opens every day from 11 AM to 11 PM. There's Wi-Fi and plug points, and you're welcome to stay through the afternoon.",
         sections=[
            ("What you get", "<ul><li>Wi-Fi and plug points</li><li>Open every day, 11 AM to 11 PM</li><li>A counter by the window for working on your own, and round tables for two to four</li><li>Cash, card or UPI</li></ul>"),
            ("What to order for a long session", "<p>Coffee starts at ₹149 for an espresso. A cappuccino is ₹249 and The Classic Cold Coffee, our most-ordered drink, is ₹299. For food that works next to a laptop: sandwiches and panini at ₹329 to ₹349, pastas at ₹399, fries from ₹229 and croissants from ₹249. The <a href=\"/menu\">full menu</a> has 128 items.</p>"),
            ("Meetings and small groups", "<p>Book a table on WhatsApp from this site and mention the meeting in the notes. For 7 or more people, choose 7+ guests so we can set up the tables.</p>"),
            ("Getting here", BKC_P + VISIT_P),
         ]),
    dict(slug="matcha-santacruz-east", short="Matcha in Santacruz East",
         title="Matcha in Santacruz East, Mumbai | Cafe Kokomo's matcha bar",
         desc="Five matcha drinks at ₹299 at Cafe Kokomo near Vakola Bridge, Santacruz East: Iced Matcha, Iced Coconut Matcha, Iced Strawberry Glow Matcha and Velvet Vanilla Matcha, hot or iced.",
         h1='Matcha <span class="accent">in Santacruz East.</span>',
         lede="Cafe Kokomo's matcha bar has five drinks, all ₹299, made with select-grade matcha.",
         sections=[
            ("The five drinks", "<ul><li><strong>Iced Matcha</strong>: matcha with chilled milk. No added sugar.</li><li><strong>Iced Coconut Matcha</strong>: matcha with coconut and chilled milk. No added sugar.</li><li><strong>Iced Strawberry Glow Matcha</strong>: matcha with strawberry and chilled milk.</li><li><strong>Iced Velvet Vanilla Matcha</strong>: matcha with vanilla and chilled milk.</li><li><strong>Hot Velvet Vanilla Matcha</strong>: a warm matcha latte with vanilla and steamed milk.</li></ul>"),
            ("Which one to order", "<p>If you want to taste the matcha itself, start with the Iced Matcha or the Iced Coconut Matcha, which have no added sugar. Strawberry Glow and Velvet Vanilla add strawberry or vanilla, and the Velvet Vanilla is the one to order hot.</p>"),
            ("Something to eat with it", "<p>A Butter Croissant (₹249), a Honey Glazed Cinnamon Roll (₹219) or a slice of New York Cheesecake (₹299). Everything is on the <a href=\"/menu\">full menu</a>.</p>"),
            ("Ordering in", "<p>Iced Matcha is also on our Swiggy and Zomato menus. Delivery prices are set separately from the dine-in prices here.</p>"),
            ("Getting here", VISIT_P),
         ]),
    dict(slug="veg-friendly-cafe-vakola", short="Veg-friendly cafe",
         title="Veg-friendly cafe near Vakola, Santacruz East | Cafe Kokomo",
         desc="103 of the 128 items at Cafe Kokomo near Vakola Bridge are vegetarian, and every dish is marked veg, egg or non-veg. Pastas, sandwiches, hummus, falafel and more.",
         h1='A veg-friendly cafe <span class="accent">near Vakola.</span>',
         lede="103 of the 128 items on Cafe Kokomo's menu are vegetarian. Every dish is marked: a green dot for veg, yellow for egg and red for non-veg, and the menu page has a Veg only filter.",
         sections=[
            ("Veg mains", "<p>All seven pastas are veg at ₹399: Alfredo, Pesto, Pink Sauce, Arrabbiata, Creamy Mushroom Alfredo Spaghetti, Cacio E Pepe and Garlic Chilli Aglio Olio. So are the Basil Pesto Panini (₹329), Grilled Veggie Sandwich (₹329), Spicy Cottage Cheese Sandwich (₹349), Falafel &amp; Hummus Bowl (₹369) and Mediterranean Salad (₹299).</p>"),
            ("Small plates to share", "<p>Hummus &amp; Pita (₹269), Nachos &amp; Hummus (₹299), Falafel with Hummus (6 pieces, ₹299), Kokomo Special Loaded Nachos (₹299), Vada Pav Sliders (₹269), Thai Chilli Potatoes (₹269), Truffle Parmesan Fries (₹299) and Seasoned Fries (₹249).</p>"),
            ("If you don't eat egg", "<p>Eight items contain egg and carry the yellow dot: the five egg dishes on the breakfast menu, both cheesecakes and the World's Best Chocolate Cake. Everything else marked green is veg.</p>"),
            ("Getting here", VISIT_P),
         ]),
    dict(slug="cafe-near-bkc", short="Cafe near BKC",
         title="Cafe near BKC, Mumbai | Cafe Kokomo, Santacruz East",
         desc="Cafe Kokomo is about 3.4 to 4.7 km by road from BKC, near Vakola Bridge in Santacruz East. Open 11 AM to 11 PM daily, Wi-Fi and plug points, meal for two about ₹400 to ₹600.",
         h1='A cafe <span class="accent">near BKC.</span>',
         lede="Cafe Kokomo is in Santacruz East, near Vakola Bridge, a short drive from Bandra Kurla Complex.",
         sections=[
            ("How far it is", BKC_P),
            ("What you'll find", "<ul><li>Open every day, 11 AM to 11 PM</li><li>Wi-Fi and plug points</li><li>128 dishes and drinks: coffee from ₹149, pastas and sandwiches at ₹329 to ₹399</li><li>A meal for two usually comes to about ₹400 to ₹600</li></ul>"),
            ("Before or after an appointment", "<p>If you have time to fill around a meeting or a visa appointment in BKC, you can sit with a coffee and a sandwich, charge your phone and get back on the road.</p>"),
            ("Booking for a meeting", "<p>Book a table on WhatsApp from this site and mention the meeting in the notes. For 7 or more people, choose 7+ guests.</p>"),
            ("Getting here", VISIT_P),
         ]),
]

def crumb_ld(items):
    return '    <script type="application/ld+json">\n    ' + json.dumps({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(items)]}, ensure_ascii=False) + "\n    </script>\n"

def guide_cards(skip=None):
    return "\n".join(f'                <a class="guide-card" href="/guides/{g["slug"]}"><strong>{g["short"]}</strong><span>{html.escape(g["desc"][:110])}…</span></a>'
                     for g in GUIDES if g["slug"] != skip)

guide_pages = []
for g in GUIDES:
    url = f'https://cafekokomo.com/guides/{g["slug"]}'
    body = "\n".join(f"            <h2>{h}</h2>\n            {c}" for h, c in g["sections"])
    page = head(g["title"], g["desc"], url, crumb_ld([("Home", "https://cafekokomo.com/"), ("Guides", "https://cafekokomo.com/guides/"), (g["short"], url)])) + nav(sub=True) + f"""<main id="main">
    <section class="page-head">
        <div class="wrap prose">
            <nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> / <a href="/guides/">Guides</a> / <span>{g["short"]}</span></nav>
            <h1>{g["h1"]}</h1>
            <p class="guide-lede">{g["lede"]}</p>
{body}
            <div class="guide-cta">
                <h2>Ready when you are</h2>
                <p>Book a table and we'll confirm on WhatsApp, or have a look at the menu first.</p>
                <div class="hero-actions"><a href="javascript:void(0)" class="btn btn-dark" data-open-reservation>Book a table</a><a href="/menu" class="btn btn-outline">See the menu</a></div>
            </div>
        </div>
    </section>
    <section class="section band more-guides">
        <div class="wrap">
            <span class="eyebrow">More guides</span>
            <div class="guide-grid">
{guide_cards(skip=g["slug"])}
            </div>
        </div>
    </section>
</main>
""" + FOOTER + tail(False)
    guide_pages.append((f'guides/{g["slug"]}.html', page))

guides_index = head("Guides | Cafe Kokomo, Santacruz East", "Short guides to Cafe Kokomo near Vakola Bridge, Santacruz East: working from the cafe, matcha, vegetarian food and getting here from BKC.",
                    "https://cafekokomo.com/guides/", crumb_ld([("Home", "https://cafekokomo.com/"), ("Guides", "https://cafekokomo.com/guides/")])) + nav(sub=True) + f"""<main id="main">
    <section class="page-head">
        <div class="wrap">
            <nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> / <span>Guides</span></nav>
            <h1>Guides to <span class="accent">Cafe Kokomo.</span></h1>
            <p>Working from the cafe, matcha, vegetarian food, and getting here from BKC.</p>
            <div class="guide-grid" style="margin-top: 32px;">
{guide_cards()}
            </div>
        </div>
    </section>
</main>
""" + FOOTER + tail(False)

import os
os.makedirs(f"{OUT}/guides", exist_ok=True)
for name, page in guide_pages + [("guides/index.html", guides_index)]:
    assert page.count("<main") == 1 and page.count("<div") == page.count("</div>"), name
    open(f"{OUT}/{name}", "w", encoding="utf-8").write(page)
    print(name, len(page) // 1024, "KB")

for name, page in (("index.html", index), ("menu.html", menu), ("404.html", notfound), ("privacy.html", privacy)):
    assert page.count("<main") == 1 and "{" not in re.sub(r"<script.*?</script>|<style.*?</style>", "", page, flags=re.S).replace("{len", ""), name
    open(f"{OUT}/{name}", "w", encoding="utf-8").write(page)
    print(name, len(page) // 1024, "KB")
print("quotes used:", [n for n, _ in quotes[:5]])
