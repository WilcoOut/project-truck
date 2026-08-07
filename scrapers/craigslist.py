import re
import hashlib
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from scrapers import fetch
from config import get_cities_in_radius, PRICE_MIN, PRICE_MAX, MODELS


def _unique_search_terms() -> list[str]:
    """Collect unique CL search terms across all models (preserving order)."""
    seen: set[str] = set()
    terms: list[str] = []
    for model in MODELS:
        for t in model["craigslist_terms"]:
            if t not in seen:
                seen.add(t)
                terms.append(t)
    return terms


def fetch_listing_image(url: str) -> str | None:
    """Fetch the first photo from a Craigslist listing detail page."""
    resp = fetch(url)
    if not resp:
        return None
    soup = BeautifulSoup(resp.text, "lxml")
    img = soup.select_one("figure.iw img, .gallery img")
    return img.get("src") if img else None


class CraigslistScraper:
    name = "Craigslist"

    def search(self) -> list[dict]:
        results = []
        seen_urls: set[str] = set()
        cities = get_cities_in_radius()
        search_terms = _unique_search_terms()

        for city in cities:
            for term in search_terms:
                url = (
                    f"https://{city}.craigslist.org/search/cto"
                    f"?query={quote_plus(term)}&min_price={PRICE_MIN}&max_price={PRICE_MAX}"
                )
                resp = fetch(url)
                if not resp:
                    continue

                soup = BeautifulSoup(resp.text, "lxml")
                items = soup.select("li.cl-static-search-result")

                for item in items:
                    link_tag = item.find("a", href=True)
                    if not link_tag:
                        continue
                    item_url = link_tag.get("href", "")
                    if not item_url or item_url in seen_urls:
                        continue
                    seen_urls.add(item_url)

                    id_match = re.search(r"/(\d{9,})\.", item_url)
                    item_id = (
                        f"cl_{id_match.group(1)}"
                        if id_match
                        else f"cl_{hashlib.md5(item_url.encode()).hexdigest()[:12]}"
                    )

                    title = item.get("title", "")
                    if not title:
                        title_tag = item.select_one(".title")
                        title = title_tag.get_text(strip=True) if title_tag else ""

                    price_tag = item.select_one(".price")
                    price_text = price_tag.get_text(strip=True) if price_tag else ""
                    price_match = re.search(r"\$([0-9,]+)", price_text)
                    price = (
                        int(price_match.group(1).replace(",", ""))
                        if price_match
                        else None
                    )

                    loc_tag = item.select_one(".location")
                    location = loc_tag.get_text(strip=True) if loc_tag else city

                    img_tag = item.find("img")
                    image_url = img_tag.get("src") if img_tag else None
                    # Prefer the larger thumbnail Craigslist serves at 600x450
                    if image_url and "300x300" in image_url:
                        image_url = image_url.replace("300x300", "600x450")

                    results.append(
                        {
                            "id": item_id,
                            "source": "Craigslist",
                            "url": item_url,
                            "title": title,
                            "price": price,
                            "location": location,
                            "description": "",
                            "image_url": image_url,
                        }
                    )

        return results
