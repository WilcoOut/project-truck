#!/usr/bin/env python3
"""
Flask web server + APScheduler for Railway deployment.

Routes:
  GET  /       — serve the latest HTML report
  POST /run    — manually trigger a crawl (returns when done)

The daily crawl runs automatically at 8 AM Eastern via APScheduler.
Data is stored in DATA_DIR (env var) so it survives Railway redeploys
when a Volume is mounted there.
"""
import logging
import os
import threading

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, redirect, url_for

app = Flask(__name__)
crawl_lock = threading.Lock()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)


def run_crawl() -> None:
    if not crawl_lock.acquire(blocking=False):
        log.warning("Crawl already in progress — skipping")
        return
    try:
        log.info("Crawl starting")
        from main import main
        main(open_browser=False)
        log.info("Crawl complete")
    except Exception:
        log.exception("Crawl failed")
    finally:
        crawl_lock.release()


@app.route("/")
def report():
    from config import REPORT_PATH
    if not os.path.exists(REPORT_PATH):
        return (
            "<h1>Project Truck Finder</h1>"
            "<p>No report yet — the first crawl runs at 8 AM ET, "
            "or <form method='post' action='/run' style='display:inline'>"
            "<button>trigger one now</button></form>.</p>"
        ), 200
    with open(REPORT_PATH, "r", encoding="utf-8") as f:
        return f.read(), 200, {"Content-Type": "text/html; charset=utf-8"}


@app.route("/run", methods=["POST"])
def trigger():
    run_crawl()
    return redirect(url_for("report"))


if __name__ == "__main__":
    scheduler = BackgroundScheduler(timezone="America/New_York")
    scheduler.add_job(run_crawl, trigger="cron", hour=8, minute=0)
    scheduler.start()
    log.info("Scheduler started — daily crawl at 08:00 ET")

    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, use_reloader=False)
