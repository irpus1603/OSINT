#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
News Media Crawler (RSS-first)
- Pulls RSS feeds
- Matches security-related keywords (EN + ID)
- Optional: fetches full article text for deeper matching
- Writes results to CSV

Usage:
    python newscrawler.py --save output.csv --full    # with full-article fetch
    python newscrawler.py --save output.csv           # headlines+descriptions only
"""

import argparse
import csv
import hashlib
import re
import time
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

import feedparser
import requests
from bs4 import BeautifulSoup

# -----------------------------
# CONFIG: Feeds & Keywords
# -----------------------------

FEEDS = [
    # Global
    "https://feeds.reuters.com/reuters/topNews",
    "https://feeds.reuters.com/reuters/worldNews",
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://rss.cnn.com/rss/edition_world.rss",
    "https://www.aljazeera.com/xml/rss/all.xml",
    "https://apnews.com/apf-topnews?output=rss",
    # Indonesia
    "https://www.kompas.com/kompascom/feed",          # Kompas
    "https://rss.detik.com/index.php/detikcom",       # Detikcom
    "https://www.cnnindonesia.com/nasional/rss",      # CNN Indonesia - Nasional
    "https://www.cnnindonesia.com/internasional/rss", # CNN Indonesia - Internasional
    "https://www.antaranews.com/rss/terkini.xml",     # Antara
    "https://www.thejakartapost.com/rss",             # The Jakarta Post
]

# Keyword patterns (regex). Use \b for word boundaries and allow suffixes via \w*
# Feel free to edit/expand this list.
KEYWORD_PATTERNS = [
    # English
    r"\bterror(ism|ist|ize|ized|izing|s)?\b",
    r"\bbomb(ing|ings|ed|s)?\b",
    r"\bexplos(ion|ive|ives|ions)\b",
    r"\battack(s|ed|ing)?\b",
    r"\bmilitant(s)?\b",
    r"\binsurg(en(t|cy)|ents?)\b",
    r"\bhostage(s|taking)?\b",
    r"\bshoot(ing|ings|er|ers)?\b",
    r"\bthreat(s|ened|ening)?\b",
    r"\bsecurity\b",
    r"\briot(s|ing)?\b",
    r"\bprotest(s|er|ers|ing)?\b",
    r"\bdemonstrat(e|ion|ions|or|ors|ing|ed|es)\b",
    r"\bextrem(ist|ism|ists)?\b",
    r"\bradicali(s|z)(e|ed|ing|ation)\b",
    r"\bcyber(-|\s)?attack(s|ed|ing)?\b",
    # Indonesian
    r"\bteror(isme|is|isnya)?\b",
    r"\bbom(ber|bunuhdiri| meledak| meledakkan| ledakan)?\b",
    r"\bledak(an|an\-)?\b",
    r"\bserang(an| menyerang| diserang)?\b",
    r"\bkerusuh(an)?\b",
    r"\bdemo(nstrasi)?\b",
    r"\bunjuk\s?rasa\b",
    r"\bpenculikan\b",
    r"\bsandera\b",
    r"\bancam(an| mengancam)?\b",
    r"\bkeamanan\b",
    r"\bekstrem(is|isme)?\b",
    r"\bradikalisasi\b",
    r"\bpenembak(an)?\b",
]

# Compile regex patterns once
KEYWORD_REGEXES = [re.compile(p, flags=re.IGNORECASE) for p in KEYWORD_PATTERNS]

# Request headers & timeouts
HEADERS = {
    "User-Agent": "SecurityNewsCrawler/1.0 (+https://example.org/)",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}
REQ_TIMEOUT = 12  # seconds
FETCH_SLEEP = 0.7 # polite rate limiting when fetching pages


# -----------------------------
# Helpers
# -----------------------------

def sha1(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8", "ignore")).hexdigest()

def parse_pubdate(entry) -> str:
    # Try to parse RSS pubDate/updated fields, fallback to now (UTC ISO8601)
    for key in ("published", "updated", "pubDate"):
        if key in entry and entry[key]:
            try:
                dt = parsedate_to_datetime(entry[key])
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt.isoformat()
            except Exception:
                pass
    return datetime.now(timezone.utc).isoformat()

def extract_text_from_html(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    # Remove script/style
    for s in soup(["script", "style", "noscript"]):
        s.extract()
    # Prefer article content if present
    candidates = []
    for selector in ["article", "main", "div#content", "div.article", "div.post", "section.article"]:
        for node in soup.select(selector):
            candidates.append(node.get_text(separator=" ", strip=True))
    # Fallback to all paragraphs
    if not candidates:
        paragraphs = [p.get_text(separator=" ", strip=True) for p in soup.find_all("p")]
        candidates.append(" ".join(paragraphs))
    # Return the longest chunk as the main text
    candidates = [c for c in candidates if c]
    if not candidates:
        return ""
    return max(candidates, key=len)

def fetch_full_article(url: str) -> str:
    try:
        r = requests.get(url, headers=HEADERS, timeout=REQ_TIMEOUT)
        if r.status_code != 200 or not r.text:
            return ""
        return extract_text_from_html(r.text)
    except Exception:
        return ""


def match_keywords(text: str):
    """Return set of keyword patterns that matched."""
    hits = set()
    if not text:
        return hits
    for rx in KEYWORD_REGEXES:
        if rx.search(text):
            hits.add(rx.pattern)
    return hits


# -----------------------------
# Core crawler
# -----------------------------

def crawl(feeds, fetch_full=True, dedupe_map=None):
    """
    Iterate feeds -> entries -> match keywords -> yield hits
    """
    dedupe_map = dedupe_map or set()

    for feed_url in feeds:
        try:
            parsed = feedparser.parse(feed_url)
        except Exception as e:
            print(f"[WARN] Failed to parse feed: {feed_url} ({e})")
            continue

        if parsed.bozo:
            # bozo = True indicates parse warnings/errors (still may have entries)
            pass

        for entry in parsed.entries:
            url = entry.get("link") or ""
            title = (entry.get("title") or "").strip()
            summary = (entry.get("summary") or entry.get("description") or "").strip()
            published = parse_pubdate(entry)

            if not url:
                continue

            uid = sha1(url)
            if uid in dedupe_map:
                continue

            base_text = f"{title}\n{summary}"
            hits = match_keywords(base_text)

            full_text = ""
            if fetch_full and not hits:
                # Only fetch full article if headline/summary didn't match
                time.sleep(FETCH_SLEEP)
                full_text = fetch_full_article(url)
                if full_text:
                    hits = match_keywords(f"{base_text}\n{full_text}")

            if hits:
                excerpt = (summary or full_text[:1000]).replace("\n", " ").strip()
                yield {
                    "title": title,
                    "url": url,
                    "published": published,
                    "matched_keywords": ";".join(sorted(hits)),
                    "excerpt": excerpt,
                }   

            dedupe_map.add(uid)


# -----------------------------
# CLI
# -----------------------------

def main():
    ap = argparse.ArgumentParser(description="News media crawler for security-related keywords.")
    ap.add_argument("--save", default="news_hits.csv", help="CSV output path")
    ap.add_argument("--full", action="store_true", help="Fetch full article pages for deeper matching")
    ap.add_argument("--feeds", nargs="*", help="Override feed URLs (space-separated)")
    ap.add_argument("--sleep", type=float, default=0.0, help="Sleep seconds between feeds (politeness)")
    args = ap.parse_args()

    feeds = args.feeds if args.feeds else FEEDS

    # Crawl
    dedupe = set()
    rows = list(crawl(feeds=feeds, fetch_full=args.full, dedupe_map=dedupe))

    # Save CSV
    with open(args.save, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["published", "title", "url", "matched_keywords", "excerpt"])
        w.writeheader()
        for r in sorted(rows, key=lambda x: x["published"], reverse=True):
            w.writerow(r)

    print(f"[OK] Saved {len(rows)} matches to {args.save}")

    if args.sleep > 0:
        time.sleep(args.sleep)


if __name__ == "__main__":
    main()
