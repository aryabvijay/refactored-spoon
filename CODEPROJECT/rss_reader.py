import re
from collections import Counter
import time
import feedparser
from ticker_dict import ticker_dict
import csv

# FEED_URL
LOG_FILE = "stock_counts.csv"
SEEN_FILE = "seen_ids.txt"

def get_headlines(feed_url: str):
    """
    Fetch headlines from an RSS feed.
    Uses requests to fetch the feed bytes (requests uses certifi for CA bundle) and then parses with feedparser.
    Falls back to feedparser.parse(url) if requests isn't available or the fetch fails.
    """
    try:
        # import inside function so script still runs if requests not installed
        import requests

        resp = requests.get(feed_url, timeout=15)
        resp.raise_for_status()
        feed = feedparser.parse(resp.content)
    except Exception as e:
        print("Info: requests fetch failed or not available, falling back to feedparser.parse(url). Reason:", e)
        feed = feedparser.parse(feed_url)

    if getattr(feed, "bozo", False):
        print("Warning: feedparser reported a problem parsing the feed:", getattr(feed, "bozo_exception", ""))

    headlines = []
    for entry in feed.entries:
        # Robust UID fallback: try common id fields, then link, then title
        uid = entry.get("id") or entry.get("guid") or entry.get("link") or entry.get("title")
        if uid is None:
            # skip entries we can't identify reliably
            continue
        uid = str(uid).strip()
        title = entry.get("title") or entry.get("summary") or ""
        title = str(title).strip()
        headlines.append((uid, title))
    return headlines


def build_patterns(ticker_dict):
    """
    For each ticker, build a compiled regex that matches the company name
    as a whole word (case-insensitive via uppercasing).
    """
    patterns = {}
    for ticker, name in ticker_dict.items():
        if not name:
            continue

        name_upper = name.upper()
        pattern = re.compile(r"\b" + re.escape(name_upper) + r"\b") #Note to self: "\b" creates boundary to prevent false +ve.
        patterns[ticker] = pattern

    return patterns

"""
Next two functions are helpers.
To deal with already seen headlines.
"""

def load_seen():
    try:
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f)
    except FileNotFoundError:
        return set()


def save_seen(seen):
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        for id in seen:
            f.write(id + "\n")


def count_mentions(headlines, ticker_dict):
    """
    Count how many headlines mention each company name.
    We count at most 1 per headline per ticker (even if name appears twice).
    Returns a Counter mapping company -> count. 
    Update: Original code was ticker - > count. Does not work.
    Some companies have multiple tickers
    """
    patterns = build_patterns(ticker_dict)
    counts = Counter()

    for headline in headlines:
        text = headline[1].upper()
        matched_companies = set()  #Track which companies matched this headline

        for ticker, pattern in patterns.items():
            company = ticker_dict[ticker]
            if company not in matched_companies and pattern.search(text):
                counts[company] += 1
                matched_companies.add(company)
    return counts

def log_counts(counts):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for company, count in counts.most_common():
            writer.writerow([timestamp, company, count])

def main():
    seen = load_seen()

    raw_headlines = get_headlines(FEED_URL) #requires the feedurl

    # keep only new ones
    new_headlines = [
        (uid, title) for uid, title in raw_headlines
        if uid not in seen
    ]

    # short debug summary
    print(f"Raw: {len(raw_headlines)}, Seen: {len(seen)}, New: {len(new_headlines)}")

    if not new_headlines:
        print("No new headlines. Skipping update.")
        return
    
    # only mark processed (new) headlines as seen
    for uid, _ in new_headlines:
        seen.add(uid)
    save_seen(seen)

    print(f"Fetched {len(new_headlines)} headlines from feed.")
    print()

    counts = count_mentions(new_headlines, ticker_dict)

    print("Top mentioned tickers:")
    for company, count in counts.most_common(20):
        print(f"{company:40} {count}")
    log_counts(counts)

if __name__ == "__main__":
    main()