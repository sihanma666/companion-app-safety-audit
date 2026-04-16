# companion-app-safety-audit

Research data pipeline for auditing AI companion apps across the iOS App Store and Google Play.

## Structure

```
├── data/
│   ├── raw/            # ios.json + android.json (gitignored)
│   └── processed/      # intermediate outputs
├── db/
│   └── companion_apps.db   # SQLite (gitignored)
├── src/
│   ├── normalize.py    # ingest raw JSON → SQLite
│   ├── classify.py     # Claude API classification pass
│   └── export.py       # SQLite → research_output.csv
├── output/
│   └── research_output.csv
├── .env                # ANTHROPIC_API_KEY (gitignored)
└── requirements.txt
```

## Setup

```bash
pip install -r requirements.txt
cp .env .env.local      # add your ANTHROPIC_API_KEY
```

Place `ios.json` and `android.json` in `data/raw/`.

## Usage

```bash
# 1. Ingest raw JSON into SQLite
py src/normalize.py

# 2. Classify apps with Claude (not yet implemented)
py src/classify.py

# 3. Export to CSV (not yet implemented)
py src/export.py
```

## DB Schema

Table: `apps`

| Column | Type | Notes |
|---|---|---|
| app_id | TEXT | primary key (with platform) |
| platform | TEXT | `ios` or `android` |
| title | TEXT | |
| developer | TEXT | |
| developer_legal_name | TEXT | Android only |
| developer_address | TEXT | Android only |
| content_rating | TEXT | |
| price | REAL | |
| free | INTEGER | 0/1 |
| offers_iap | INTEGER | 0/1, Android only |
| iap_range | TEXT | Android only |
| ad_supported | INTEGER | 0/1, Android only |
| score | REAL | |
| reviews | INTEGER | iOS: review count; Android: total rating count |
| installs_min | INTEGER | Android only |
| installs_max | INTEGER | Android only |
| privacy_policy_url | TEXT | iOS: developerWebsite proxy |
| genre | TEXT | |
| released | TEXT | |
| updated | TEXT | |
| description | TEXT | |
| raw_json | TEXT | full original entry as JSON blob |
