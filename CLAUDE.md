# CLAUDE.md — companion-app-safety-audit

This file documents key decisions and context for the research data pipeline.
**Review and update this manually** as the project evolves.

---

## Data sources

| File | Platform | Apps |
|---|---|---|
| `data/raw/ios.json` | iOS App Store | 453 |
| `data/raw/android.json` | Google Play | 492 |

Both are simplified copies of the originals (in `data/`), with the following
fields stripped before ingestion:

**iOS stripped:** `supportedDevices`, `screenshots`, `icon`, `ipadScreenshots`,
`appletvScreenshots`, `primaryGenreId`, `genreIds`

**Android stripped:** `androidVersion`, `androidVersionText`, `androidMaxVersion`,
`screenshots`, `headerImage`, `icon`, `descriptionHTML`, `scoreText`, `priceText`,
`preregister`, `earlyAccessEnabled`, `isAvailableInPlayPass`, `genreId`, `comments`

---

## DB schema decisions

Table: `apps` in `db/companion_apps.db`. Primary key is `(app_id, platform)`.

### Platform-asymmetric fields (NULL where not applicable)

| Column | iOS | Android |
|---|---|---|
| `developer_legal_name` | NULL | `developerLegalName` |
| `developer_address` | NULL | `developerLegalAddress` |
| `offers_iap` | NULL | `offersIAP` |
| `iap_range` | NULL | `IAPRange` |
| `ad_supported` | NULL | `adSupported` |
| `installs_min` | NULL | `minInstalls` |
| `installs_max` | NULL | `maxInstalls` |

### Fields requiring interpretation

- **`reviews`** — iOS: `reviews` (review count). Android: `ratings` (total rating
  count, broader than text review count). These are not strictly equivalent.
  <!-- TODO: decide whether to track both separately -->

- **`privacy_policy_url`** — iOS has no dedicated privacy policy field.
  Currently populated from `developerWebsite` as the closest proxy.
  <!-- TODO: decide whether to NULL this out for iOS or accept the proxy -->

- **`free`** — stored as `INTEGER` (0/1), converted from JSON boolean on both platforms.

- **`raw_json`** — stores the full simplified entry (post-stripping) as a JSON
  blob. The original unstripped files remain in `data/` if needed.

---

## Pipeline scripts

| Script | Status | Purpose |
|---|---|---|
| `src/normalize.py` | Done | Ingest `ios.json` + `android.json` → SQLite |
| `src/classify.py` | Scaffold | Claude API classification pass |
| `src/export.py` | Scaffold | SQLite → `output/research_output.csv` |

Run order: `normalize.py` → `classify.py` → `export.py`

---

## Open questions
<!-- Fill these in as decisions are made -->

- [ ] What classification dimensions should `classify.py` cover? (e.g. AI companion
      flag, targets minors, monetises emotional dependency, data sharing risks)
- [ ] Should classifications be written back to new columns on `apps`, or to a
      separate `classifications` table joined by `(app_id, platform)`?
- [ ] How to handle the `reviews` / `ratings` asymmetry between platforms?
- [ ] Accept `developerWebsite` as `privacy_policy_url` proxy for iOS, or NULL it?
- [ ] Which columns appear in the final `research_output.csv`?
