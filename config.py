import os
import math

# ── Search location ───────────────────────────────────────────────────────────
# ZIP 23185 = Williamsburg, VA
HOME_LAT = 37.2707
HOME_LON = -76.7075
SEARCH_RADIUS_MILES = 500

# ── Target vehicles ───────────────────────────────────────────────────────────
# Desired engine variants:
#   Tacoma  1998–2004 → 3.4L V6 (5VZ-FE)
#   Ranger  1998–2000 → 4.0L OHV V6
#   S-10    1998–2004 → 4.3L V6
#   Dakota  2000–2004 → 3.9L Magnum V6
MODELS = [
    {
        "name": "Toyota Tacoma",
        "make": "Toyota",
        "years": list(range(1998, 2005)),
        "terms": ["Tacoma"],
        "craigslist_terms": ["tacoma"],
    },
    {
        "name": "Ford Ranger",
        "make": "Ford",
        "years": list(range(1998, 2001)),
        "terms": ["Ranger", "Ford Ranger"],
        "craigslist_terms": ["ford ranger"],
    },
    {
        "name": "Chevrolet S-10",
        "make": "Chevrolet",
        "years": list(range(1998, 2005)),
        "terms": ["S10", "S-10", "S 10"],
        "craigslist_terms": ["s10", "s-10"],
    },
    {
        "name": "Dodge Dakota",
        "make": "Dodge",
        "years": list(range(2000, 2005)),
        "terms": ["Dakota"],
        "craigslist_terms": ["dakota"],
    },
]

# Union of all valid years across every model — used for broad year extraction
YEARS = sorted({y for m in MODELS for y in m["years"]})

# ── Price range ───────────────────────────────────────────────────────────────
PRICE_MIN = 500
PRICE_MAX = 8000

# ── Craigslist cities with coordinates ───────────────────────────────────────
# (lat, lon) for the center of each metro; used to filter by SEARCH_RADIUS_MILES
_CL_CITY_COORDS: dict[str, tuple[float, float]] = {
    "albany":        (42.651, -73.755),
    "albuquerque":   (35.085, -106.650),
    "atlanta":       (33.749, -84.388),
    "austin":        (30.267, -97.743),
    "baltimore":     (39.290, -76.612),
    "batonrouge":    (30.451, -91.187),
    "boise":         (43.615, -116.202),
    "boston":        (42.360, -71.059),
    "buffalo":       (42.886, -78.879),
    "charleston":    (32.779, -79.931),
    "charlotte":     (35.227, -80.843),
    "chattanooga":   (35.046, -85.309),
    "chicago":       (41.878, -87.630),
    "cincinnati":    (39.103, -84.512),
    "cleveland":     (41.500, -81.695),
    "columbia":      (34.000, -81.035),
    "columbus":      (39.962, -82.999),
    "dallas":        (32.777, -96.797),
    "denver":        (39.739, -104.984),
    "desmoines":     (41.590, -93.620),
    "detroit":       (42.332, -83.046),
    "fresno":        (36.737, -119.787),
    "grandrapids":   (42.963, -85.668),
    "hartford":      (41.764, -72.685),
    "houston":       (29.760, -95.369),
    "huntsville":    (34.730, -86.586),
    "indianapolis":  (39.768, -86.158),
    "jackson":       (32.298, -90.184),
    "jacksonville":  (30.332, -81.656),
    "kansascity":    (39.099, -94.578),
    "knoxville":     (35.961, -83.921),
    "lasvegas":      (36.175, -115.136),
    "littlerock":    (34.746, -92.289),
    "losangeles":    (34.052, -118.244),
    "memphis":       (35.149, -90.049),
    "miami":         (25.774, -80.190),
    "milwaukee":     (43.039, -87.907),
    "minneapolis":   (44.977, -93.265),
    "nashville":     (36.162, -86.781),
    "neworleans":    (29.951, -90.075),
    "newyork":       (40.713, -74.006),
    "norfolk":       (36.851, -76.285),
    "oklahomacity":  (35.467, -97.517),
    "omaha":         (41.256, -95.934),
    "orlando":       (28.538, -81.379),
    "philadelphia":  (39.952, -75.165),
    "phoenix":       (33.448, -112.074),
    "pittsburgh":    (40.441, -79.996),
    "portland":      (45.523, -122.676),
    "raleigh":       (35.779, -78.638),
    "reno":          (39.529, -119.813),
    "richmond":      (37.541, -77.434),
    "sacramento":    (38.581, -121.494),
    "saltlakecity":  (40.759, -111.888),
    "sanantonio":    (29.425, -98.494),
    "sandiego":      (32.716, -117.161),
    "sfbay":         (37.774, -122.419),
    "seattle":       (47.609, -122.332),
    "shreveport":    (32.525, -93.750),
    "spokane":       (47.659, -117.426),
    "stlouis":       (38.627, -90.198),
    "tampa":         (27.947, -82.459),
    "tucson":        (32.221, -110.926),
    "tulsa":         (36.154, -95.993),
    "washingtondc":  (38.907, -77.037),
    "wichita":       (37.692, -97.337),
}


def _haversine_miles(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 3958.8  # Earth radius in miles
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    return R * 2 * math.asin(math.sqrt(a))


def get_cities_in_radius() -> list[str]:
    """Return CL city slugs within SEARCH_RADIUS_MILES of (HOME_LAT, HOME_LON)."""
    result = []
    for city, (lat, lon) in _CL_CITY_COORDS.items():
        dist = _haversine_miles(HOME_LAT, HOME_LON, lat, lon)
        if dist <= SEARCH_RADIUS_MILES:
            result.append(city)
    return sorted(result)


# ── Quality flags ─────────────────────────────────────────────────────────────
GREEN_FLAGS = [
    "runs", "drives", "running", "complete", "solid frame", "clean title",
    "rebuilt", "restored", "no rust", "original", "barn find",
    "garage kept", "clear title", "working", "good title", "lien free",
    "solid", "drives out", "all there", "all original", "starts",
    "new title", "free and clear",
    # Engine-specific boosts for target variants
    "v6", "3.4l", "3.4 liter", "4.0l", "4.0 liter", "4.3l", "4.3 liter",
    "3.9l", "3.9 liter", "magnum",
]

# Wrong body style / variant — reject these regardless of engine
VARIANT_REJECT_TERMS = [
    "blazer",   # S-10 Blazer is a 2-door SUV, not a pickup
    "jimmy",    # GMC Jimmy — SUV sibling of the S-10 Blazer
]

# Engine displacement / cylinder counts that identify unwanted 4-cyl variants.
# Checked against the listing title on first pass and the full description once fetched.
FOUR_CYL_TERMS = [
    "4cyl", "4-cyl", "4 cyl", "4cylinder", "4 cylinder", "four cylinder",
    "i4", "inline 4", "inline-4",
    "2.4l", "2.4 l", "2.4-liter", "2.4 liter",  # Tacoma 2RZ/2AZ 4-cyl
    "2.2l", "2.2 l", "2.2-liter", "2.2 liter",  # S-10 4-cyl
    "2.5l", "2.5 l", "2.5-liter", "2.5 liter",  # Ranger 4-cyl
]

RED_FLAGS = [
    "fire damage", "flood damage", "bent frame", "no title",
    "salvage title", "frame damage", "wrecked", "totaled",
]

SOFT_RED_FLAGS = [
    "parts only", "roller", "no engine", "no drivetrain",
    "no start", "non runner", "basket case",
]

# ── Manual search links shown in report ──────────────────────────────────────
MANUAL_SEARCH_LINKS = [
    # ── Facebook Marketplace ──────────────────────────────────────────────────
    {
        "group": "Facebook Marketplace",
        "site": "Toyota Tacoma V6 (1998–2004)",
        "url": "https://www.facebook.com/marketplace/search/?query=1998+toyota+tacoma+v6&categoryId=807311116002614",
        "note": "Login required",
    },
    {
        "group": "Facebook Marketplace",
        "site": "Ford Ranger 4.0 V6 (1998–2000)",
        "url": "https://www.facebook.com/marketplace/search/?query=1998+ford+ranger+4.0+v6&categoryId=807311116002614",
        "note": "Login required",
    },
    {
        "group": "Facebook Marketplace",
        "site": "Chevy S-10 V6 (1998–2004)",
        "url": "https://www.facebook.com/marketplace/search/?query=1998+chevy+s10+v6&categoryId=807311116002614",
        "note": "Login required",
    },
    {
        "group": "Facebook Marketplace",
        "site": "Dodge Dakota V6 (2000–2004)",
        "url": "https://www.facebook.com/marketplace/search/?query=2000+dodge+dakota+v6&categoryId=807311116002614",
        "note": "Login required",
    },
    # ── eBay Motors ───────────────────────────────────────────────────────────
    {
        "group": "eBay Motors",
        "site": "Toyota Tacoma V6 (1998–2004)",
        "url": "https://www.ebay.com/sch/6001/i.html?_nkw=1998-2004+toyota+tacoma+v6&_sop=10",
        "note": "Newly listed",
    },
    {
        "group": "eBay Motors",
        "site": "Ford Ranger 4.0 V6 (1998–2000)",
        "url": "https://www.ebay.com/sch/6001/i.html?_nkw=1998-2000+ford+ranger+4.0+v6&_sop=10",
        "note": "Newly listed",
    },
    {
        "group": "eBay Motors",
        "site": "Chevy S-10 V6 (1998–2004)",
        "url": "https://www.ebay.com/sch/6001/i.html?_nkw=1998-2004+chevy+s10+v6&_sop=10",
        "note": "Newly listed",
    },
    {
        "group": "eBay Motors",
        "site": "Dodge Dakota V6 (2000–2004)",
        "url": "https://www.ebay.com/sch/6001/i.html?_nkw=2000-2004+dodge+dakota+v6&_sop=10",
        "note": "Newly listed",
    },
    # ── Hemmings ─────────────────────────────────────────────────────────────
    {
        "group": "Hemmings",
        "site": "Toyota Tacoma (1998–2004)",
        "url": "https://www.hemmings.com/classifieds/cars-for-sale/toyota/tacoma?year_from=1998&year_to=2004",
        "note": "Classic specialist",
    },
    {
        "group": "Hemmings",
        "site": "Ford Ranger (1998–2000)",
        "url": "https://www.hemmings.com/classifieds/cars-for-sale/ford/ranger?year_from=1998&year_to=2000",
        "note": "Classic specialist",
    },
    {
        "group": "Hemmings",
        "site": "Chevy S-10 (1998–2004)",
        "url": "https://www.hemmings.com/classifieds/cars-for-sale/chevrolet/s-10?year_from=1998&year_to=2004",
        "note": "Classic specialist",
    },
    {
        "group": "Hemmings",
        "site": "Dodge Dakota (2000–2004)",
        "url": "https://www.hemmings.com/classifieds/cars-for-sale/dodge/dakota?year_from=2000&year_to=2004",
        "note": "Classic specialist",
    },
]

# ── Paths ─────────────────────────────────────────────────────────────────────
# DATA_DIR defaults to the project root locally.
# On Railway, set DATA_DIR to a mounted Volume path (e.g. /data) so the
# database and report persist across deploys.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.environ.get("DATA_DIR", BASE_DIR)
OUTPUT_DIR = os.path.join(DATA_DIR, "output")
DB_PATH = os.path.join(DATA_DIR, "trucks.db")
REPORT_PATH = os.path.join(OUTPUT_DIR, "index.html")

REQUEST_DELAY = 1.5
REQUEST_TIMEOUT = 15
