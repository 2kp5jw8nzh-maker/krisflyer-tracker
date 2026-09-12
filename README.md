# krisflyer-tracker

A KrisFlyer (Singapore Airlines & Scoot) award-miles redemption board for
flights out of Singapore, hosted on GitHub Pages so it keeps working without
any Claude subscription.

**Live site:** enable GitHub Pages in this repo's Settings → Pages
(Source: `Deploy from a branch`, Branch: `main` / `/ (root)`), then the board
is at `https://<your-username>.github.io/krisflyer-tracker/`.

## What it does

- `index.html` — the board itself: SIA + Scoot award charts (Saver &
  Advantage, one-way & return), filters, a "search by miles budget" tool, and
  active promotions with their discounts already baked into the mileage
  figures. It's a static page that fetches `data.json` at load time.
- `data.json` — the actual data: zone award charts, destination lists, and
  current promotions. Edit this (or `build_data.py`, then re-run it) whenever
  the award chart or promotions change.
- `build_data.py` — regenerates `data.json` from hand-maintained Python
  tables. Run this after you update the tables inside it.
- `check_promos.py` — runs on a schedule (via GitHub Actions) and checks
  whether the official KrisFlyer/Scoot promotion pages have changed since the
  last run. It doesn't try to auto-parse exact discount terms off those pages
  (too fragile) — instead, when it detects a change, it flags a banner on the
  site and sends a push notification via [ntfy](https://ntfy.sh) so you know
  to go check and update `data.json` by hand (or ask Claude to help).
- `.github/workflows/update.yml` — the scheduled GitHub Action that runs
  `check_promos.py` every 6 hours and commits any changes.

## Get promo-change alerts on your phone

1. Install the [ntfy app](https://ntfy.sh/) (iOS/Android) or use ntfy.sh in a
   browser.
2. Subscribe to the topic: **`krisflyer-scoot-promo-watch-sg`**
3. You'll get a push notification whenever the checker notices one of the
   monitored promo pages has changed.

Note: ntfy topics aren't private — anyone who knows the topic name could in
theory subscribe too. There's nothing sensitive in these alerts, but if you'd
rather have a topic only you know, edit `NTFY_TOPIC` in `check_promos.py` to
something less guessable and re-subscribe to the new name.

## Updating the award chart / promotions by hand

1. Edit the tables in `build_data.py` (or `data.json` directly for small
   tweaks).
2. If you edited `build_data.py`, run `python build_data.py` to regenerate
   `data.json`.
3. Commit and push — GitHub Pages picks up the change automatically.

## Manually triggering a promo check

Go to the **Actions** tab → **Check KrisFlyer promo pages** → **Run workflow**,
instead of waiting for the next scheduled run.
