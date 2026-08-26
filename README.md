# J-Indie Radar

Discover Hidden Japanese Indie Gems & Untranslated Classics.

English editorial site for Japanese Steam indies. Python generates static HTML into `docs/` for GitHub Pages or Cloudflare Pages.

## Setup

```powershell
cd "D:\For_work01\J-Indie Radar"
python -m pip install -r requirements.txt
copy .env.example .env
python scripts/fetch_and_summarize.py --seed
```

`--seed` publishes 20+ bundled English dossiers. Gemini is not required for the first build.

## Daily Gemini updates

Put `GEMINI_API_KEY` in `.env` and extra Steam app IDs in `data/watchlist.json`.

```powershell
python scripts/fetch_and_summarize.py --update --max 3
```

- Default model: `gemini-1.5-flash`
- `time.sleep(8)` after each Gemini call
- Exponential backoff on HTTP 429

GitHub Actions runs at 10:00 JST (`cron: '0 1 * * *'`) and adds up to 3 titles. Store `GEMINI_API_KEY` as a repository secret.

## AdSense checklist

1. Set `SITE_URL`, `CONTACT_EMAIL`, `ADSENSE_CLIENT_ID`, `GA_MEASUREMENT_ID`
2. Replace the publisher id in `docs/ads.txt`
3. Rebuild: `python scripts/build_site.py`
4. GitHub Pages: publish the `docs/` folder. Cloudflare Pages: output directory `docs`

Required pages: `privacy.html`, `about.html`, `contact.html`, `disclaimer.html`.
