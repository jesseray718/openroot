#!/usr/bin/env python3
"""
GOVBID SCRAPER v3.2 — Aggressive Concrete Finder
Less filtering, more results
"""

import requests, csv, os, re, time
from datetime import datetime
from bs4 import BeautifulSoup

# ============================================================
# CONFIG
# ============================================================
OUTPUT_DIR = os.path.expanduser("~/govbids")
DATE = datetime.now().strftime("%Y-%m-%d")
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 14; SM-A155U) AppleWebKit/537.36"
}

# Concrete keywords — if ANY of these appear, it's a match
CONCRETE_KEYWORDS = [
    "concrete", "sidewalk", "curb", "paving", "road", "bridge",
    "foundation", "parking lot", "masonry", "flatwork", "resurfacing",
    "grading", "excavation", "asphalt", "overlay", "demolition",
    "site work", "curb and gutter", "pavement", "playground",
    "retaining wall", "slab", "footing", "pour", "storm sewer",
    "ADA ramp", "street", "culvert", "manhole", "mill", "overlay"
]

# ============================================================
# SOURCES THAT ACTUALLY WORK
# ============================================================
SOURCES = {
    "Missouri Bid Network": "https://www.missouribids.com",
    "MoDOT Projects": "https://www.modot.org/projects",
    "Sikeston Bids": "https://www.sikeston.org/bids_page/index.php",
    "Sikeston BMU": "https://www.sikestonbmu.org/bid-notices.php",
    "Cape County": "https://www.capecounty.us/county-purchasing-information",
}

# ============================================================
# HELPERS
# ============================================================
def matches_concrete(text):
    if not text:
        return False
    t = text.lower()
    return any(kw in t for kw in CONCRETE_KEYWORDS)

def clean_text(text):
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s.,\-]', '', text)
    return text.strip()

def is_useful_link(text):
    """Skip navigation, footer, and junk links."""
    junk = ["home", "about", "contact", "privacy", "terms", "login", "register",
            "road closure", "winter report", "report concern", "map", "alert"]
    t = text.lower()
    return not any(j in t for j in junk) and len(text) > 10 and len(text) < 300

def save_results(results, filename):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=[
            "source", "title", "agency", "location",
            "due_date", "posted_date", "amount",
            "description", "url"
        ])
        w.writeheader()
        for r in results:
            w.writerow(r)
    print(f"  💾 Saved {len(results)} results to {path}")

def safe_get(url, timeout=20):
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout)
        r.raise_for_status()
        return r
    except Exception as e:
        print(f"  ❌ {url[:50]}... → {str(e)[:60]}")
        return None

# ============================================================
# MAIN SCRAPING FUNCTION
# ============================================================
def scrape_source(name, url):
    """Scrape a single source for concrete-related links."""
    print(f"\n🔍 Scanning {name}...")
    results = []

    resp = safe_get(url, timeout=25)
    if not resp:
        return results

    soup = BeautifulSoup(resp.text, "html.parser")

    # Look for all links and text blocks
    candidates = []

    # Get all links
    for link in soup.find_all("a", href=True):
        text = clean_text(link.get_text())
        href = link["href"]
        if href.startswith("/"):
            href = requests.utils.urlparse(url)
            href = f"{href.scheme}://{href.netloc}{href.path}"
        candidates.append((text, href, "link"))

    # Get table rows (often bid listings)
    for row in soup.find_all("tr"):
        text = clean_text(row.get_text())
        if len(text) > 20 and len(text) < 500:
            link = row.find("a", href=True)
            href = link["href"] if link else url
            candidates.append((text, href, "row"))

    # Get list items
    for li in soup.find_all("li"):
        text = clean_text(li.get_text())
        if len(text) > 20 and len(text) < 400:
            link = li.find("a", href=True)
            href = link["href"] if link else url
            candidates.append((text, href, "list"))

    # Filter for concrete + useful
    for text, href, ctype in candidates:
        if not is_useful_link(text):
            continue
        if not matches_concrete(text):
            continue

        title_key = text[:80].lower()
        if not any(title_key in r["title"].lower() for r in results):
            results.append({
                "source": name,
                "title": text[:200],
                "agency": name,
                "location": "Missouri",
                "due_date": "",
                "posted_date": "",
                "amount": "",
                "description": text[:500],
                "url": href
            })

    print(f"  ✅ Found {len(results)} concrete items from {name}")
    return results

# ============================================================
# MAIN
# ============================================================
def main():
    print(f"🔍 GOVBID SCRAPER v3.2 — {DATE}")
    print(f"📍 Area: Sikeston, MO + 100mi radius")
    print(f"🎯 Focus: Concrete / Construction")
    print(f"⚡ AGGRESSIVE MODE — Less filtering, more results")
    print("=" * 55)

    all_results = []

    # Scrape all sources
    for name, url in SOURCES.items():
        results = scrape_source(name, url)
        all_results.extend(results)
        time.sleep(1)  # Don't hammer servers

    # Deduplicate
    seen = set()
    unique = []
    for r in all_results:
        key = r["title"][:80].lower()
        if key not in seen:
            seen.add(key)
            unique.append(r)

    # Sort by source
    unique.sort(key=lambda x: x["source"])

    # Save
    save_results(unique, f"govbids_{DATE}.csv")
    save_results(unique, "latest.csv")

    # Summary
    print(f"\n{'=' * 55}")
    print(f"📊 RESULTS FOR {DATE}")
    print(f"{'=' * 55}")
    print(f"Total concrete bids found: {len(unique)}")

    by_source = {}
    for r in unique:
        s = r["source"]
        by_source[s] = by_source.get(s, 0) + 1

    for src, count in sorted(by_source.items(), key=lambda x: -x[1]):
        print(f"  {src}: {count}")

    if unique:
        print(f"\n🔥 TOP 10 FINDINGS:")
        for i, r in enumerate(unique[:10], 1):
            print(f"  {i}. [{r['source']}] {r['title'][:65]}")
            if r['url'] and r['url'] != "https://www.missouribids.com":
                print(f"     → {r['url'][:75]}")

    print(f"\n📁 Full results: {os.path.join(OUTPUT_DIR, f'govbids_{DATE}.csv')}")
    print(f"\n💡 TIP: Open the CSV on your phone to see which ones are real bids")

if __name__ == "__main__":
    main()
