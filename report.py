import os
from datetime import datetime
from config import (
    REPORT_PATH, OUTPUT_DIR, MANUAL_SEARCH_LINKS,
    HOME_LAT, HOME_LON, SEARCH_RADIUS_MILES, get_cities_in_radius,
    PRICE_MIN, PRICE_MAX,
)

CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: #f0f2f5;
    color: #1a202c;
}
a { color: inherit; text-decoration: none; }

/* ── Header ── */
header {
    background: linear-gradient(135deg, #1a202c 0%, #2d3748 100%);
    color: white;
    padding: 1.5rem 2rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 4px solid #d69e2e;
}
header h1 { font-size: 1.6rem; font-weight: 800; letter-spacing: -0.5px; }
header p { opacity: 0.6; font-size: 0.8rem; margin-top: 0.2rem; }
.header-meta { text-align: right; font-size: 0.78rem; opacity: 0.65; line-height: 1.6; }

/* ── Stats bar ── */
.stats {
    display: flex;
    gap: 1px;
    background: #e2e8f0;
    border-bottom: 1px solid #e2e8f0;
}
.stat {
    flex: 1;
    background: white;
    text-align: center;
    padding: 1rem 0.5rem;
}
.stat .num  { font-size: 1.8rem; font-weight: 800; line-height: 1; }
.stat .lbl  { font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.5px; color: #718096; margin-top: 0.2rem; }
.stat.s-new     .num { color: #c05621; }
.stat.s-total   .num { color: #553c9a; }
.stat.s-toyota  .num { color: #276749; }
.stat.s-ford    .num { color: #2b6cb0; }
.stat.s-chevy   .num { color: #b7791f; }
.stat.s-dodge   .num { color: #c05621; }

/* ── Controls bar ── */
.controls {
    background: white;
    border-bottom: 1px solid #e2e8f0;
    padding: 0.75rem 1.5rem;
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
    align-items: center;
}
.ctrl-group { display: flex; align-items: center; gap: 0.4rem; flex-wrap: wrap; }
.ctrl-label {
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.4px;
    color: #718096;
    margin-right: 0.2rem;
}
.ctrl-btn {
    background: #edf2f7;
    border: 1px solid #e2e8f0;
    color: #4a5568;
    font-size: 0.78rem;
    font-weight: 500;
    padding: 0.3rem 0.75rem;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.12s;
}
.ctrl-btn:hover { background: #e2e8f0; }
.ctrl-btn.active {
    background: #2b6cb0;
    border-color: #2b6cb0;
    color: white;
}
.ctrl-btn.active.ford  { background: #2b6cb0; border-color: #2b6cb0; }
.ctrl-btn.active.chevy { background: #276749; border-color: #276749; }
.ctrl-btn.active.new-f { background: #c05621; border-color: #c05621; }
.ctrl-divider { width: 1px; height: 24px; background: #e2e8f0; }

/* ── Price range slider ── */
.price-filter { align-items: center; gap: 0.6rem; }
.pr-display {
    font-size: 0.82rem; font-weight: 600; color: #4a5568;
    min-width: 140px; white-space: nowrap;
}
.pr-wrap {
    position: relative;
    width: 200px; height: 22px;
    display: flex; align-items: center;
}
.pr-track {
    position: absolute;
    left: 0; right: 0; top: 50%;
    transform: translateY(-50%);
    height: 4px; border-radius: 2px;
    background: #e2e8f0;
    pointer-events: none;
}
.pr-fill {
    position: absolute;
    height: 100%; border-radius: 2px;
    background: #2b6cb0;
}
.pr-thumb {
    position: absolute;
    width: 100%; height: 22px;
    appearance: none; -webkit-appearance: none;
    background: transparent;
    pointer-events: none;
    margin: 0;
}
.pr-thumb::-webkit-slider-thumb {
    appearance: none; -webkit-appearance: none;
    width: 16px; height: 16px; border-radius: 50%;
    background: #2b6cb0; border: 2px solid white;
    box-shadow: 0 1px 3px rgba(0,0,0,0.25);
    pointer-events: all; cursor: pointer;
}
.pr-thumb::-moz-range-thumb {
    width: 16px; height: 16px; border-radius: 50%;
    background: #2b6cb0; border: 2px solid white;
    box-shadow: 0 1px 3px rgba(0,0,0,0.25);
    pointer-events: all; cursor: pointer; border: none;
}

/* ── Count badge ── */
.count-badge {
    display: inline-block;
    background: rgba(0,0,0,0.12);
    border-radius: 999px;
    font-size: 0.65rem;
    padding: 0 5px;
    margin-left: 3px;
    font-weight: 700;
}

/* ── Grid ── */
.grid-wrap { padding: 1.25rem 1.5rem 2rem; }
.grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 1.1rem;
}
.no-results {
    grid-column: 1/-1;
    text-align: center;
    padding: 3rem;
    color: #a0aec0;
    font-size: 0.95rem;
}

/* ── Card ── */
.card {
    background: white;
    border-radius: 10px;
    overflow: hidden;
    box-shadow: 0 1px 4px rgba(0,0,0,0.08);
    transition: transform 0.15s, box-shadow 0.15s;
    position: relative;
    display: flex;
    flex-direction: column;
}
.card:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0,0,0,0.12); }
.card.is-new { border: 2px solid #dd6b20; }
.new-ribbon {
    position: absolute;
    top: 10px;
    left: -2px;
    background: #dd6b20;
    color: white;
    font-size: 0.65rem;
    font-weight: 800;
    padding: 3px 10px 3px 8px;
    border-radius: 0 4px 4px 0;
    letter-spacing: 0.5px;
    z-index: 2;
}

/* ── Image ── */
.card-img { width: 100%; height: 185px; object-fit: cover; display: block; background: #edf2f7; }
.no-img {
    width: 100%; height: 185px;
    background: linear-gradient(135deg, #2d3748, #4a5568);
    display: flex; align-items: center; justify-content: center;
    color: #a0aec0; font-size: 0.82rem; font-weight: 600; letter-spacing: 0.5px;
}

/* ── Card body ── */
.card-body { padding: 0.85rem 0.95rem 0.4rem; flex: 1; }
.card-title {
    font-size: 0.92rem; font-weight: 600; line-height: 1.35; color: #2d3748;
    margin-bottom: 0.45rem;
    display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
}
.card-row { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 0.55rem; }
.price { font-size: 1.3rem; font-weight: 800; color: #276749; }
.price.no-price { font-size: 0.82rem; color: #a0aec0; font-weight: 400; }
.location { font-size: 0.75rem; color: #718096; max-width: 55%; text-align: right; }

/* ── Score bar ── */
.score-row { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.6rem; }
.score-track { flex: 1; height: 5px; background: #e2e8f0; border-radius: 99px; overflow: hidden; }
.score-fill { height: 100%; border-radius: 99px; }
.score-label { font-size: 0.68rem; color: #718096; width: 26px; text-align: right; }

/* ── Tags ── */
.tags { display: flex; flex-wrap: wrap; gap: 3px; margin-bottom: 0.55rem; min-height: 20px; }
.tag { font-size: 0.66rem; font-weight: 600; padding: 2px 7px; border-radius: 999px; }
.tag-green { background: #c6f6d5; color: #22543d; }
.tag-red   { background: #fed7d7; color: #742a2a; }

/* ── Card footer ── */
.card-footer {
    padding: 0.6rem 0.95rem;
    background: #f7fafc;
    border-top: 1px solid #edf2f7;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 0.5rem;
}
.source-info { font-size: 0.7rem; color: #a0aec0; }
.btn-view {
    display: inline-block;
    background: #2b6cb0;
    color: white;
    padding: 0.32rem 0.85rem;
    border-radius: 6px;
    font-size: 0.78rem;
    font-weight: 600;
    white-space: nowrap;
}
.btn-view:hover { background: #2c5282; }

/* ── Manual links ── */
.manual-section {
    margin: 0 1.5rem 2rem;
    background: white;
    border-radius: 10px;
    overflow: hidden;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.manual-section h3 {
    background: #2d3748; color: white;
    padding: 0.75rem 1.2rem;
    font-size: 0.82rem; font-weight: 700; letter-spacing: 0.3px;
}
.manual-link {
    display: flex; justify-content: space-between; align-items: center;
    padding: 0.6rem 1.2rem;
    border-bottom: 1px solid #edf2f7;
}
.manual-link:last-child { border-bottom: none; }
.manual-link a { color: #2b6cb0; font-weight: 600; font-size: 0.88rem; }
.manual-link a:hover { text-decoration: underline; }
.manual-note { font-size: 0.73rem; color: #a0aec0; }
.manual-group + .manual-group { border-top: 2px solid #edf2f7; }
.manual-group h4 {
    padding: 0.45rem 1.2rem;
    font-size: 0.75rem; font-weight: 700; letter-spacing: 0.4px;
    color: #718096; text-transform: uppercase;
    background: #f7fafc;
}

/* ── Criteria ── */
.criteria { margin: 0 1.5rem 1.5rem; display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.criteria-box { background: white; border-radius: 10px; padding: 0.9rem 1.1rem; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }
.criteria-box h4 { font-size: 0.78rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.4px; margin-bottom: 0.5rem; }
.criteria-box.look h4 { color: #276749; }
.criteria-box.avoid h4 { color: #c53030; }
.criteria-box ul { padding-left: 1rem; }
.criteria-box li { font-size: 0.8rem; color: #4a5568; line-height: 1.6; }

.section-head {
    padding: 1.25rem 1.5rem 0.5rem;
    font-size: 0.85rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.5px; color: #4a5568;
    border-top: 1px solid #e2e8f0;
}
.run-footer { text-align: center; padding: 1.25rem; color: #a0aec0; font-size: 0.76rem; border-top: 1px solid #e2e8f0; }
"""

JS = """
(function () {
    var currentSort   = 'default';
    var currentFilter = 'all';
    var priceMin = PRICE_LO;
    var priceMax = PRICE_DEFAULT_HI;

    function getCards() {
        return Array.from(document.querySelectorAll('#listings-grid .card'));
    }

    function applyControls() {
        var cards = getCards();
        var noResults = document.getElementById('no-results');

        cards.forEach(function (c) {
            // Model / new filter
            var show = true;
            if (currentFilter === 'new')
                show = c.dataset.isNew === '1';
            else if (currentFilter !== 'all')
                show = c.dataset.model === currentFilter;

            // Price filter — listings with no price always pass through
            if (show) {
                var p = parseFloat(c.dataset.price);
                if (p > 0) show = (p >= priceMin && p <= priceMax);
            }

            c.style.display = show ? '' : 'none';
        });

        // Sort visible
        var visible = cards.filter(function (c) { return c.style.display !== 'none'; });
        visible.sort(function (a, b) {
            if (currentSort === 'price-asc') {
                var pa = parseFloat(a.dataset.price) || 999999;
                var pb = parseFloat(b.dataset.price) || 999999;
                return pa - pb;
            }
            if (currentSort === 'price-desc') {
                var pa2 = parseFloat(a.dataset.price) || 0;
                var pb2 = parseFloat(b.dataset.price) || 0;
                return pb2 - pa2;
            }
            if (currentSort === 'newest') {
                return a.dataset.date < b.dataset.date ? 1 : -1;
            }
            if (currentSort === 'make') {
                return a.dataset.make.localeCompare(b.dataset.make);
            }
            var newDiff = parseInt(b.dataset.isNew) - parseInt(a.dataset.isNew);
            if (newDiff !== 0) return newDiff;
            return parseFloat(b.dataset.score) - parseFloat(a.dataset.score);
        });

        var grid = document.getElementById('listings-grid');
        visible.forEach(function (c) { grid.appendChild(c); });
        if (noResults) noResults.style.display = visible.length === 0 ? 'block' : 'none';
    }

    function updatePriceTrack() {
        var lo   = parseInt(document.getElementById('pr-min').value);
        var hi   = parseInt(document.getElementById('pr-max').value);
        var span = PRICE_HI - PRICE_LO;
        var fill = document.getElementById('pr-fill');
        fill.style.left  = ((lo - PRICE_LO) / span * 100) + '%';
        fill.style.width = ((hi - lo)        / span * 100) + '%';
        document.getElementById('pr-lo').textContent = '$' + lo.toLocaleString();
        document.getElementById('pr-hi').textContent = hi >= PRICE_HI ? 'Any' : '$' + hi.toLocaleString();
        priceMin = lo;
        priceMax = hi;
        applyControls();
    }

    document.querySelectorAll('.sort-btn').forEach(function (btn) {
        btn.addEventListener('click', function () {
            document.querySelectorAll('.sort-btn').forEach(function (b) { b.classList.remove('active'); });
            btn.classList.add('active');
            currentSort = btn.dataset.sort;
            applyControls();
        });
    });

    document.querySelectorAll('.filter-btn').forEach(function (btn) {
        btn.addEventListener('click', function () {
            document.querySelectorAll('.filter-btn').forEach(function (b) { b.classList.remove('active'); });
            btn.classList.add('active');
            currentFilter = btn.dataset.filter;
            applyControls();
        });
    });

    var prMin = document.getElementById('pr-min');
    var prMax = document.getElementById('pr-max');
    if (prMin && prMax) {
        prMin.addEventListener('input', function () {
            if (parseInt(prMin.value) > parseInt(prMax.value)) prMin.value = prMax.value;
            updatePriceTrack();
        });
        prMax.addEventListener('input', function () {
            if (parseInt(prMax.value) < parseInt(prMin.value)) prMax.value = prMin.value;
            updatePriceTrack();
        });
        updatePriceTrack();  // initialise fill on page load
    }
})();
"""


def _score_color(score: float) -> str:
    if score >= 70:
        return "#38a169"
    if score >= 50:
        return "#d69e2e"
    return "#e53e3e"


def _price_html(price) -> str:
    if price:
        return f'<span class="price">${price:,}</span>'
    return '<span class="price no-price">Price not listed</span>'


def _image_html(image_url, title) -> str:
    if image_url:
        safe = title.replace('"', "&quot;")
        return (
            f'<img class="card-img" src="{image_url}" alt="{safe}" loading="lazy" '
            f'onerror="this.parentElement.innerHTML=\'<div class=no-img>No Photo</div>\'">'
        )
    return '<div class="no-img">No Photo</div>'


def _card_html(listing: dict) -> str:
    is_new = int(listing.get("is_new", 0))
    score = listing.get("score", 50) or 50
    price = listing.get("price") or 0
    make = listing.get("make", "")
    first_seen = (listing.get("first_seen") or "")[:10]

    new_class = "is-new" if is_new else ""
    ribbon = '<div class="new-ribbon">NEW</div>' if is_new else ""
    score_color = _score_color(score)

    green_tags = "".join(
        f'<span class="tag tag-green">{f}</span>'
        for f in listing.get("green_flags", [])[:5]
    )
    red_tags = "".join(
        f'<span class="tag tag-red">{f}</span>'
        for f in listing.get("red_flags", [])[:3]
    )

    model_name = listing.get("model", "")

    return (
        f'<div class="card {new_class}" '
        f'data-score="{score:.0f}" '
        f'data-price="{price}" '
        f'data-make="{make}" '
        f'data-model="{model_name}" '
        f'data-date="{first_seen}" '
        f'data-is-new="{is_new}">'
        f"{ribbon}"
        f"{_image_html(listing.get('image_url'), listing.get('title', ''))}"
        f'<div class="card-body">'
        f'<div class="card-title">{listing.get("title", "No title")}</div>'
        f'<div class="card-row">'
        f"{_price_html(listing.get('price'))}"
        f'<span class="location">{listing.get("location", "")}</span>'
        f"</div>"
        f'<div class="score-row">'
        f'<div class="score-track"><div class="score-fill" style="width:{score:.0f}%;background:{score_color}"></div></div>'
        f'<span class="score-label">{score:.0f}</span>'
        f"</div>"
        f'<div class="tags">{green_tags}{red_tags}</div>'
        f"</div>"
        f'<div class="card-footer">'
        f'<span class="source-info">{listing.get("source", "")} &middot; {first_seen}</span>'
        f'<a href="{listing.get("url", "#")}" target="_blank" rel="noopener" class="btn-view">View Listing &rarr;</a>'
        f"</div>"
        f"</div>"
    )


def _model_count(listings: list[dict], model_name: str) -> int:
    return sum(1 for l in listings if l.get("model") == model_name)


def _controls_html(listings: list[dict], price_lo: int, price_hi: int, price_default_hi: int) -> str:
    from config import MODELS as _MODELS
    total   = len(listings)
    new_cnt = sum(1 for l in listings if l.get("is_new"))

    filter_buttons = ""
    for m in _MODELS:
        cnt = _model_count(listings, m["name"])
        filter_buttons += (
            f'    <button class="ctrl-btn filter-btn" data-filter="{m["name"]}">'
            f'{m["name"]} <span class="count-badge">{cnt}</span></button>\n'
        )

    return f"""
<div class="controls">
  <div class="ctrl-group">
    <span class="ctrl-label">Sort:</span>
    <button class="ctrl-btn sort-btn active" data-sort="default">Score</button>
    <button class="ctrl-btn sort-btn" data-sort="price-asc">Price Low &rarr; High</button>
    <button class="ctrl-btn sort-btn" data-sort="price-desc">Price High &rarr; Low</button>
    <button class="ctrl-btn sort-btn" data-sort="newest">Newest First</button>
    <button class="ctrl-btn sort-btn" data-sort="make">Make / Model</button>
  </div>
  <div class="ctrl-divider"></div>
  <div class="ctrl-group">
    <span class="ctrl-label">Filter:</span>
    <button class="ctrl-btn filter-btn active" data-filter="all">All <span class="count-badge">{total}</span></button>
{filter_buttons}    <button class="ctrl-btn filter-btn new-f" data-filter="new">New Today <span class="count-badge">{new_cnt}</span></button>
  </div>
  <div class="ctrl-divider"></div>
  <div class="ctrl-group price-filter">
    <span class="ctrl-label">Price:</span>
    <span class="pr-display"><span id="pr-lo">${price_lo:,}</span> &ndash; <span id="pr-hi">Any</span></span>
    <div class="pr-wrap">
      <div class="pr-track"><div class="pr-fill" id="pr-fill"></div></div>
      <input type="range" id="pr-min" class="pr-thumb"
             min="{price_lo}" max="{price_hi}" value="{price_lo}" step="250">
      <input type="range" id="pr-max" class="pr-thumb"
             min="{price_lo}" max="{price_hi}" value="{price_default_hi}" step="250">
    </div>
  </div>
</div>
"""


def _manual_links_html() -> str:
    groups: dict[str, list[dict]] = {}
    for lnk in MANUAL_SEARCH_LINKS:
        groups.setdefault(lnk.get("group", "Other"), []).append(lnk)

    sections = ""
    for group_name, links in groups.items():
        items = "".join(
            f'<div class="manual-link">'
            f'<a href="{lnk["url"]}" target="_blank" rel="noopener">{lnk["site"]}</a>'
            f'<span class="manual-note">{lnk["note"]}</span>'
            f"</div>"
            for lnk in links
        )
        sections += f'<div class="manual-group"><h4>{group_name}</h4>{items}</div>'

    return f'<div class="manual-section"><h3>Manual Search Links (open in browser)</h3>{sections}</div>'


def _criteria_html() -> str:
    look = [
        "Solid frame — rust here is a deal-killer",
        "Solid cab corners, floors, and rockers",
        "Running drivetrain — easier to rebuild what's there",
        "Complete truck — missing classic parts get expensive",
        "Clear title — no headaches later",
    ]
    avoid = [
        "Fire or flood damage",
        "Bent frame (accident history)",
        "Rollers with no drivetrain",
        "No title or salvage title",
    ]
    li = lambda items: "".join(f"<li>{i}</li>" for i in items)
    return (
        f'<div class="criteria">'
        f'<div class="criteria-box look"><h4>Prioritize</h4><ul>{li(look)}</ul></div>'
        f'<div class="criteria-box avoid"><h4>Avoid</h4><ul>{li(avoid)}</ul></div>'
        f"</div>"
    )


_MAKE_CSS = {
    "Toyota":     "s-toyota",
    "Ford":       "s-ford",
    "Chevrolet":  "s-chevy",
    "Dodge":      "s-dodge",
}
_MAKE_LABEL = {
    "Chevrolet": "Chevy",
}


def generate_report(listings: list[dict], new_count: int) -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    total = len(listings)
    timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    cities_in_range = len(get_cities_in_radius())

    # Compute price bounds from actual listings (fall back to config limits)
    prices = [l["price"] for l in listings if l.get("price")]
    price_lo = (min(prices) // 250) * 250 if prices else PRICE_MIN
    price_hi = ((max(prices) + 249) // 250) * 250 if prices else PRICE_MAX
    price_default_hi = min(3000, price_hi)

    # Build per-make counts dynamically from the current MODELS config
    from config import MODELS as _MODELS
    make_order = list(dict.fromkeys(m["make"] for m in _MODELS))
    make_stats_html = "\n".join(
        f'  <div class="stat {_MAKE_CSS.get(make, "s-make")}">'
        f'<div class="num">{sum(1 for l in listings if l.get("make") == make)}</div>'
        f'<div class="lbl">{_MAKE_LABEL.get(make, make)}</div></div>'
        for make in make_order
    )
    subtitle = " &bull; ".join(m["name"] for m in _MODELS)

    all_cards = "".join(_card_html(l) for l in listings)
    if not all_cards:
        all_cards = '<div class="no-results">No listings yet — run the crawler first.</div>'

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Project Truck Finder &mdash; {timestamp}</title>
<style>{CSS}</style>
</head>
<body>

<header>
  <div>
    <h1>Project Truck Finder</h1>
    <p>{subtitle}</p>
  </div>
  <div class="header-meta">
    {SEARCH_RADIUS_MILES}-mile radius &bull; {cities_in_range} Craigslist markets<br>
    Updated {timestamp}
  </div>
</header>

<div class="stats">
  <div class="stat s-new">  <div class="num">{new_count}</div><div class="lbl">New Today</div></div>
  <div class="stat s-total"><div class="num">{total}</div>    <div class="lbl">Total Tracked</div></div>
{make_stats_html}
</div>

{_controls_html(listings, price_lo, price_hi, price_default_hi)}

<div class="grid-wrap">
  <div class="grid" id="listings-grid">
    {all_cards}
    <div id="no-results" class="no-results" style="display:none">No listings match this filter.</div>
  </div>
</div>

<div class="section-head">Manual Search Links</div>
{_manual_links_html()}

<div class="section-head">Buying Criteria</div>
{_criteria_html()}

<div class="run-footer">
  Project Truck Finder &mdash; {SEARCH_RADIUS_MILES}-mile radius from ZIP 23185 (Williamsburg, VA)
  &mdash; Updated {timestamp}
</div>

<script>var PRICE_LO={price_lo};var PRICE_HI={price_hi};var PRICE_DEFAULT_HI={price_default_hi};{JS}</script>
</body>
</html>
"""

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(html)
