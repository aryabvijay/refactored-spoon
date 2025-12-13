# Headline Tracker
This project fetches headlines from RSS feeds, counts mentions of companies, and logs the results for trend tracking. It’s designed to be run periodically (e.g., every few hours) and avoids double-counting the same headlines. It fetches headlines from feeds, counts mentions of companies using a dictionary of tickers and names, handles multiple tickers per company, keeps track of already seen headlines to avoid double-counting, logs results to a CSV file with timestamps, and can be scheduled via Task Scheduler (Windows) or cron (Linux/macOS). Local CSV and seen files are ignored from GitHub for safety. The feed_url may be amended, but the code assumes the feed is an RSS one, with some sort of an identification (like a link) and a title. 

# Planned Feature
A buy strategy that relies on counts of number of headlines. The actual strategy is to be decided. 

# Setup
Clone the repository using `git clone https://github.com/yourusername/yourrepo.git` and `cd yourrepo`. Install dependencies with `pip install feedparser`. Update `ticker_dict.py` with your list of tickers and company names if needed. Optionally, set paths in `feed_logger.py` such as `LOG_FILE`, `SEEN_FILE`, and `FEED_URL`.

# Usage
Run the script manually using `python feed_logger.py` or schedule it to run periodically via Task Scheduler. The script fetches new headlines, counts mentions of companies, appends results to the CSV log, and skips headlines that have already been seen.

# Output
`feed_counts.csv` contains cumulative logs of company mentions with timestamps. `seen_headlines.txt` tracks processed headlines to prevent double-counting (ignored in GitHub via `.gitignore`). Example CSV row: `2025-12-13 12:00:00, Microsoft, 5`.

# Contributing
Add new tickers to `ticker_dict.py`, ensure `.gitignore` is respected (don’t commit local CSV or seen files), and use branches/PRs if collaborating with friends.




