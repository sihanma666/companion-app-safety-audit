"""
normalize.py — Parse data/raw/ios.json and data/raw/android.json into SQLite.

Each app is inserted into the `apps` table with a unified schema.
Fields that don't exist on a given platform are stored as NULL.

Field mapping
-------------
iOS source field          → DB column
-----------------------------------------
appId                     → app_id
(literal 'ios')           → platform
title                     → title
developer                 → developer
(n/a)                     → developer_legal_name  NULL
(n/a)                     → developer_address     NULL
contentRating             → content_rating
price                     → price
free                      → free
(n/a)                     → offers_iap            NULL
(n/a)                     → iap_range             NULL
(n/a)                     → ad_supported          NULL
score                     → score
reviews                   → reviews
(n/a)                     → installs_min          NULL
(n/a)                     → installs_max          NULL
developerWebsite          → privacy_policy_url    (best proxy available on iOS)
primaryGenre              → genre
released                  → released
updated                   → updated
description               → description
(full entry)              → raw_json

Android source field      → DB column
-----------------------------------------
appId                     → app_id
(literal 'android')       → platform
title                     → title
developer                 → developer
developerLegalName        → developer_legal_name
developerLegalAddress     → developer_address
contentRating             → content_rating
price                     → price
free                      → free
offersIAP                 → offers_iap
IAPRange                  → iap_range
adSupported               → ad_supported
score                     → score
ratings                   → reviews              (total rating count)
minInstalls               → installs_min
maxInstalls               → installs_max
privacyPolicy             → privacy_policy_url
genre                     → genre
released                  → released
updated                   → updated
description               → description
(full entry)              → raw_json
"""

import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IOS_JSON = ROOT / "data" / "raw" / "ios.json"
ANDROID_JSON = ROOT / "data" / "raw" / "android.json"
DB_PATH = ROOT / "db" / "companion_apps.db"

CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS apps (
    app_id              TEXT NOT NULL,
    platform            TEXT NOT NULL CHECK (platform IN ('ios', 'android')),
    title               TEXT,
    developer           TEXT,
    developer_legal_name TEXT,
    developer_address   TEXT,
    content_rating      TEXT,
    price               REAL,
    free                INTEGER,          -- 1/0 boolean
    offers_iap          INTEGER,          -- 1/0 boolean
    iap_range           TEXT,
    ad_supported        INTEGER,          -- 1/0 boolean
    score               REAL,
    reviews             INTEGER,
    installs_min        INTEGER,
    installs_max        INTEGER,
    privacy_policy_url  TEXT,
    genre               TEXT,
    released            TEXT,
    updated             TEXT,
    description         TEXT,
    raw_json            TEXT,
    PRIMARY KEY (app_id, platform)
);
"""


def bool_to_int(value) -> int | None:
    """Convert Python bool / JSON bool to 0/1 for SQLite."""
    if value is None:
        return None
    return 1 if value else 0


def normalize_ios(entry: dict) -> dict:
    return {
        "app_id":               entry.get("appId"),
        "platform":             "ios",
        "title":                entry.get("title"),
        "developer":            entry.get("developer"),
        "developer_legal_name": None,
        "developer_address":    None,
        "content_rating":       entry.get("contentRating"),
        "price":                entry.get("price"),
        "free":                 bool_to_int(entry.get("free")),
        "offers_iap":           None,
        "iap_range":            None,
        "ad_supported":         None,
        "score":                entry.get("score"),
        "reviews":              entry.get("reviews"),
        "installs_min":         None,
        "installs_max":         None,
        # iOS has no dedicated privacy policy URL; developerWebsite is the
        # closest available field.
        "privacy_policy_url":   entry.get("developerWebsite"),
        "genre":                entry.get("primaryGenre"),
        "released":             entry.get("released"),
        "updated":              entry.get("updated"),
        "description":          entry.get("description"),
        "raw_json":             json.dumps(entry, ensure_ascii=False),
    }


def normalize_android(entry: dict) -> dict:
    return {
        "app_id":               entry.get("appId"),
        "platform":             "android",
        "title":                entry.get("title"),
        "developer":            entry.get("developer"),
        "developer_legal_name": entry.get("developerLegalName"),
        "developer_address":    entry.get("developerLegalAddress"),
        "content_rating":       entry.get("contentRating"),
        "price":                entry.get("price"),
        "free":                 bool_to_int(entry.get("free")),
        "offers_iap":           bool_to_int(entry.get("offersIAP")),
        "iap_range":            entry.get("IAPRange"),
        "ad_supported":         bool_to_int(entry.get("adSupported")),
        "score":                entry.get("score"),
        # `ratings` = total rating count; `reviews` = text review count.
        # We store the broader rating count as the reviews figure.
        "reviews":              entry.get("ratings"),
        "installs_min":         entry.get("minInstalls"),
        "installs_max":         entry.get("maxInstalls"),
        "privacy_policy_url":   entry.get("privacyPolicy"),
        "genre":                entry.get("genre"),
        "released":             entry.get("released"),
        "updated":              entry.get("updated"),
        "description":          entry.get("description"),
        "raw_json":             json.dumps(entry, ensure_ascii=False),
    }


COLUMNS = [
    "app_id", "platform", "title", "developer", "developer_legal_name",
    "developer_address", "content_rating", "price", "free", "offers_iap",
    "iap_range", "ad_supported", "score", "reviews", "installs_min",
    "installs_max", "privacy_policy_url", "genre", "released", "updated",
    "description", "raw_json",
]

INSERT_SQL = f"""
INSERT OR REPLACE INTO apps ({', '.join(COLUMNS)})
VALUES ({', '.join(['?'] * len(COLUMNS))});
"""


def load_json(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    # Both files wrap results under a top-level "results" key.
    if isinstance(data, list):
        return data
    return data.get("results", [])


def main():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    con = sqlite3.connect(DB_PATH)
    con.execute(CREATE_TABLE)

    total = 0
    for path, normalizer, platform_label in [
        (IOS_JSON,     normalize_ios,     "iOS"),
        (ANDROID_JSON, normalize_android, "Android"),
    ]:
        if not path.exists():
            print(f"WARNING: {path} not found — skipping {platform_label}.", file=sys.stderr)
            continue

        entries = load_json(path)
        rows = [normalizer(e) for e in entries]
        con.executemany(INSERT_SQL, [[r[col] for col in COLUMNS] for r in rows])
        con.commit()
        print(f"{platform_label}: inserted {len(rows)} rows.")
        total += len(rows)

    con.close()
    print(f"Done. {total} total rows in {DB_PATH}.")


if __name__ == "__main__":
    main()
