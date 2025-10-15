#!/usr/bin/env python3
"""
Crawl public Twitter/X posts via snscrape (no API key).
- Filters: query keywords, geocode (lon, lat, radius), language, since/until dates.
- Output: JSONL + CSV.
- Dedup: by tweet id.
- Usage examples are at the bottom or run:  python crawl_twitter_snscrape.py -h
"""

import argparse
import csv
import datetime as dt
import json
import os
import subprocess
import sys
import ssl
import urllib3
from typing import Iterator, Dict, Any, Optional, Set

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def build_query(q: str,
                lang: Optional[str],
                lon: Optional[float],
                lat: Optional[float],
                radius: Optional[str],
                since: Optional[str],
                until: Optional[str]) -> str:
    parts = []

    # keywords / boolean query
    q = (q or "").strip()
    if q:
        parts.append(q)

    # language
    if lang:
        parts.append(f"lang:{lang}")

    # geocode (lon,lat,radius) — radius like "10km", "5mi"
    if lon is not None and lat is not None and radius:
        parts.append(f"geocode:{lon},{lat},{radius}")

    # time bounding (YYYY-MM-DD)
    # snscrape supports since/until in query
    if since:
        parts.append(f"since:{since}")
    if until:
        parts.append(f"until:{until}")

    # If nothing provided, default to last 24h (since)
    if not since and not until:
        since_dt = (dt.datetime.utcnow() - dt.timedelta(days=1)).date().isoformat()
        parts.append(f"since:{since_dt}")

    query = " ".join(parts)
    return query


def run_snscrape(query: str, max_results: int, verify_ssl: bool = True) -> Iterator[Dict[str, Any]]:
    """
    Run snscrape CLI and yield JSON objects per line.
    """
    cmd = [
        "snscrape",
        "--jsonl",
        f"--max-results={max_results}",
        "twitter-search",
        query
    ]
    
    # Set environment variables for SSL bypass
    env = os.environ.copy()
    if not verify_ssl:
        env['PYTHONHTTPSVERIFY'] = '0'
        env['CURL_CA_BUNDLE'] = ''
        env['REQUESTS_CA_BUNDLE'] = ''

    # Start process
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
    except FileNotFoundError:
        sys.stderr.write(
            "\nERROR: snscrape not found. Install it with:\n"
            "  pipx install snscrape   (recommended)\n"
            "or\n"
            "  pip install snscrape\n\n"
        )
        sys.exit(1)

    assert proc.stdout is not None
    for line in proc.stdout:
        line = line.strip()
        if not line:
            continue
        try:
            yield json.loads(line)
        except json.JSONDecodeError:
            # Skip malformed lines
            continue

    # Drain stderr to surface any useful warnings
    stderr = (proc.stderr.read() if proc.stderr else "") or ""
    proc.wait()
    if proc.returncode not in (0, None):
        sys.stderr.write(f"\nWARNING: snscrape exited with code {proc.returncode}\n{stderr}\n")


def normalize(tweet: Dict[str, Any]) -> Dict[str, Any]:
    """
    Pick stable fields and flatten into a consistent structure.
    """
    user = tweet.get("user") or {}
    coords = tweet.get("coordinates") or {}
    place = tweet.get("place") or {}

    def to_iso(ts: Any) -> Optional[str]:
        try:
            return str(ts) if ts is not None else None
        except Exception:
            return None

    return {
        "id": tweet.get("id"),
        "url": f"https://x.com/{user.get('username')}/status/{tweet.get('id')}" if user.get("username") and tweet.get("id") else tweet.get("url"),
        "date": to_iso(tweet.get("date")),
        "content": tweet.get("rawContent"),
        "lang": tweet.get("lang"),
        "username": user.get("username"),
        "displayname": user.get("displayname"),
        "user_verified": user.get("verified"),
        "user_created": to_iso(user.get("created")),
        "likeCount": tweet.get("likeCount"),
        "retweetCount": tweet.get("retweetCount"),
        "replyCount": tweet.get("replyCount"),
        "quoteCount": tweet.get("quoteCount"),
        "viewCount": tweet.get("viewCount"),
        "sourceLabel": tweet.get("sourceLabel"),
        # location signals
        "lon": coords.get("longitude"),
        "lat": coords.get("latitude"),
        "place_name": place.get("fullName") if isinstance(place, dict) else None,
        "place_type": place.get("type") if isinstance(place, dict) else None,
        "place_country": place.get("country") if isinstance(place, dict) else None,
        "place_countryCode": place.get("countryCode") if isinstance(place, dict) else None,
        # raw for debugging (keep small)
        # "raw": tweet,  # uncomment if you want full record
    }


def write_jsonl(path: str, rows: Iterator[Dict[str, Any]]) -> int:
    count = 0
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
            count += 1
    return count


def write_csv(path: str, rows: Iterator[Dict[str, Any]], fieldnames: list[str]) -> int:
    count = 0
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k) for k in fieldnames})
            count += 1
    return count


def main():
    ap = argparse.ArgumentParser(description="Crawl public Twitter/X posts using snscrape.")
    ap.add_argument("-q", "--query", default="", help="Keyword/boolean query (e.g. 'demo OR \"unjuk rasa\"').")
    ap.add_argument("--lang", default=None, help="Language code (e.g., 'in' for Bahasa Indonesia, 'en').")
    ap.add_argument("--lon", type=float, default=None, help="Longitude (e.g., 106.827 for Jakarta Monas).")
    ap.add_argument("--lat", type=float, default=None, help="Latitude (e.g., -6.175).")
    ap.add_argument("--radius", default=None, help="Radius (e.g., '10km' or '5mi'). Requires lon/lat.")
    ap.add_argument("--since", default=None, help="Start date YYYY-MM-DD (default: 24h ago).")
    ap.add_argument("--until", default=None, help="End date YYYY-MM-DD (exclusive).")
    ap.add_argument("--max-results", type=int, default=500, help="Max results to fetch (default: 500).")
    ap.add_argument("--out-prefix", default="tweets", help="Output file prefix (default: tweets).")
    ap.add_argument("--min-words", type=int, default=0, help="Filter: keep tweets with at least N words.")
    ap.add_argument("--require-geo", action="store_true", help="Filter: only keep tweets with coordinates.")
    ap.add_argument("--dedup", action="store_true", help="Deduplicate by tweet id (recommended).")
    ap.add_argument("--no-ssl-verify", action="store_true", help="Disable SSL certificate verification (use with caution).")
    args = ap.parse_args()

    query = build_query(
        q=args.query,
        lang=args.lang,
        lon=args.lon,
        lat=args.lat,
        radius=args.radius,
        since=args.since,
        until=args.until
    )

    print(f"\nQuery: {query}\nFetching up to {args.max_results} results...", file=sys.stderr)

    seen: Set[str] = set()
    records: list[Dict[str, Any]] = []
    fetched = 0

    for raw in run_snscrape(query, max_results=args.max_results, verify_ssl=not args.no_ssl_verify):
        fetched += 1
        norm = normalize(raw)

        # dedup by id
        if args.dedup:
            tid = str(norm.get("id"))
            if tid in seen:
                continue
            seen.add(tid)

        # optional filters
        if args.min_words > 0:
            word_count = len((norm.get("content") or "").split())
            if word_count < args.min_words:
                continue

        if args.require_geo and not (norm.get("lon") is not None and norm.get("lat") is not None):
            continue

        records.append(norm)

    # outputs
    jsonl_path = f"{args.out_prefix}.jsonl"
    csv_path = f"{args.out_prefix}.csv"

    # Write JSONL
    json_count = write_jsonl(jsonl_path, iter(records))

    # Write CSV
    if records:
        fieldnames = list(records[0].keys())
        csv_count = write_csv(csv_path, iter(records), fieldnames)
    else:
        csv_count = 0
        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            pass

    print(f"\nFetched: {fetched} raw tweets")
    print(f"Kept: {len(records)} tweets after filters")
    print(f"Wrote: {json_count} to {jsonl_path}")
    print(f"Wrote: {csv_count} to {csv_path}")


if __name__ == "__main__":
    main()
