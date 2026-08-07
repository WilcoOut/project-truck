import time
import requests
from config import REQUEST_DELAY, REQUEST_TIMEOUT

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def fetch(url: str, delay: bool = True) -> requests.Response | None:
    if delay:
        time.sleep(REQUEST_DELAY)
    try:
        resp = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        return resp
    except Exception as e:
        print(f"    [fetch error] {url[:80]}: {e}")
        return None
