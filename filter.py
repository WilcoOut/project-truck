import re
from config import GREEN_FLAGS, RED_FLAGS, SOFT_RED_FLAGS, MODELS


def extract_year(text: str) -> int | None:
    # Covers all model years: 1998-2004
    m = re.search(r"\b(199[89]|200[0-4])\b", text or "")
    return int(m.group(1)) if m else None


def extract_price(text: str) -> int | None:
    text = text or ""
    m = re.search(r"\$\s*([0-9,]+)", text)
    if m:
        return int(m.group(1).replace(",", ""))
    return None


def detect_make_model(text: str, year: int | None = None) -> tuple[str | None, str | None]:
    """Return (make, model_name) for the best matching MODELS entry.

    If year is known, prefer the entry whose year range includes it.
    If year is unknown, return the first term match (caller must not reject on year).
    """
    text = text or ""
    term_matches = []
    for model in MODELS:
        if any(re.search(rf"\b{re.escape(t)}\b", text, re.IGNORECASE) for t in model["terms"]):
            if year is not None and year in model["years"]:
                return model["make"], model["name"]   # exact generation match
            term_matches.append(model)

    if not term_matches:
        return None, None

    # No year supplied or no year-range match — return the first candidate
    # (filter_listing will do the final year validation)
    return term_matches[0]["make"], term_matches[0]["name"]


def score_listing(listing: dict) -> tuple[float, list[str], list[str]]:
    text = f"{listing.get('title', '')} {listing.get('description', '')}".lower()

    found_green = [f for f in GREEN_FLAGS if f in text]
    found_red   = [f for f in RED_FLAGS   if f in text]
    found_soft  = [f for f in SOFT_RED_FLAGS if f in text]
    all_red = found_red + found_soft

    if found_red:
        return 0.0, found_green, all_red

    score = 50.0
    score += min(len(found_green) * 5, 30)
    score -= len(found_soft) * 10

    price = listing.get("price")
    if price:
        if 1000 <= price <= 8000:
            score += 10
        elif price > 15000:
            score -= 10
    else:
        score -= 5

    # Year was already validated against the model's range before scoring
    if listing.get("year"):
        score += 10

    if listing.get("make"):
        score += 5

    return max(0.0, min(100.0, score)), found_green, all_red


def filter_listing(raw: dict) -> dict | None:
    """Enrich + score a raw listing. Returns None if it should be excluded."""
    combined = f"{raw.get('title', '')} {raw.get('description', '')}".strip()

    # Extract year first — needed for generation-aware model matching
    if not raw.get("year"):
        raw["year"] = extract_year(combined)

    year = raw.get("year")

    if not raw.get("make"):
        make, model_name = detect_make_model(combined, year)
        raw["make"] = make
        raw["model"] = model_name

    if not raw.get("make"):
        return None

    # Find the matched model definition and validate the year against its range
    matched = next(
        (m for m in MODELS if m["make"] == raw["make"] and m["name"] == raw["model"]),
        None,
    )
    if matched and year is not None and year not in matched["years"]:
        return None

    score, green_flags, red_flags = score_listing(raw)
    if score == 0.0 and red_flags:
        return None

    raw["score"] = score
    raw["green_flags"] = green_flags
    raw["red_flags"] = red_flags
    return raw
