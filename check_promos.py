"""
Runs on a schedule via .github/workflows/update.yml.

Checks the official KrisFlyer / Scoot promotion pages for changes since the
last run. It does NOT try to re-parse exact mileage/discount numbers off
these pages (they're JS-heavy marketing pages and that would be fragile) --
instead it fingerprints each page's visible text and, when the fingerprint
changes, flags data.json for review and sends an ntfy push alert so a human
(or a future Claude session) can go look and update the award chart /
promotions by hand.

State (per-URL content hash + last-checked time) lives in state.json so runs
know what "changed" means relative to last time.
"""
import hashlib
import json
import os
import sys
import time
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

# ntfy.sh topic for push alerts. Anyone who knows this topic name can
# subscribe (ntfy topics aren't private), so it's a specific string rather
# than something guessable, but it carries no sensitive info either way.
NTFY_TOPIC = "krisflyer-scoot-promo-watch-sg"

MONITORED = [
    dict(id="sia-redemption-sale", label="SIA Global Redemption Sale page",
         url="https://www.singaporeair.com/en_UK/sg/ppsclub-krisflyer/kf-flight-redemption/"),
    dict(id="sia-spontaneous-escapes", label="SIA Spontaneous Escapes page",
         url="https://www.singaporeair.com/en_UK/sg/plan-travel/promotions/global/kf/kf-promo/kfescapes/"),
    dict(id="scoot-spontaneous-escapes", label="Scoot Spontaneous Escapes page",
         url="https://www.flyscoot.com/en/krisflyer/spontaneous-escapes"),
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def fetch_text(session, url):
    """Fetch a page and return its normalized visible-text fingerprint input."""
    resp = session.get(url, headers=HEADERS, timeout=25)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    text = soup.get_text(separator=" ", strip=True)
    text = " ".join(text.split())
    return text


def fingerprint(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def send_ntfy(title, message, url=None):
    try:
        headers = {"Title": title, "Priority": "default", "Tags": "airplane,bell"}
        if url:
            headers["Click"] = url
        requests.post(
            "https://ntfy.sh/" + NTFY_TOPIC,
            data=message.encode("utf-8"),
            headers=headers,
            timeout=15,
        )
    except Exception as e:
        print("ntfy send failed:", e, file=sys.stderr)


def main():
    now_iso = datetime.now(timezone.utc).isoformat()

    state = {}
    if os.path.exists("state.json"):
        with open("state.json", "r", encoding="utf-8") as f:
            state = json.load(f)

    with open("data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    session = requests.Session()
    changed = []

    for entry in MONITORED:
        eid, url, label = entry["id"], entry["url"], entry["label"]
        try:
            # Warm up with a homepage visit first so the site sets its normal
            # cookies before we request the actual page -- some airline sites
            # are stricter with completely cookie-less first requests.
            homepage = url.split("/en_UK/")[0] if "/en_UK/" in url else \
                ("https://" + url.split("/")[2])
            try:
                session.get(homepage, headers=HEADERS, timeout=20)
            except Exception:
                pass
            time.sleep(1)

            text = fetch_text(session, url)
            h = fingerprint(text)
        except Exception as e:
            print(f"[{eid}] fetch failed: {e}", file=sys.stderr)
            continue

        prev = state.get(eid, {})
        prev_hash = prev.get("hash")

        if prev_hash and prev_hash != h:
            changed.append(entry)
            print(f"[{eid}] CHANGED since last check")
        else:
            print(f"[{eid}] no change" if prev_hash else f"[{eid}] first check, seeding hash")

        state[eid] = {"hash": h, "checkedAt": now_iso}

    data.setdefault("meta", {})["lastChecked"] = now_iso

    if changed:
        urls = [c["url"] for c in changed]
        labels = [c["label"] for c in changed]
        data["meta"]["lastChangeDetected"] = {
            "at": now_iso,
            "urls": urls,
            "labels": labels,
        }
        send_ntfy(
            "KrisFlyer/Scoot promo page changed",
            "Changed: " + "; ".join(labels) + ". Review and update the award chart if needed.",
            url=urls[0],
        )

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

    print("Done. Changed:", [c["id"] for c in changed])


if __name__ == "__main__":
    main()
