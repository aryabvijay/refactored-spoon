# Headline Tracker
This project fetches headlines from RSS feeds, counts mentions of companies, and logs the results for trend tracking. It’s designed to be run periodically (e.g., every few hours) and avoids double-counting the same headlines. It fetches headlines from feeds, counts mentions of companies using a dictionary of tickers and names, handles multiple tickers per company, keeps track of already seen headlines to avoid double-counting, logs results to a CSV file with timestamps, and can be scheduled via Task Scheduler (Windows) or cron (Linux/macOS). Local CSV and seen files are ignored from GitHub for safety. The feed_url may be amended, but the code assumes the feed is an RSS one, with some sort of an identification (like a link) and a title. 

# Buy Strategy
The project includes a simple buy strategy for demonstration purposes. The buy_strategy function:
Uses the counted mentions of companies in the latest headlines to determine which stocks to buy.
Fetches real-time stock prices via yfinance (users need to have it installed).
Allocates a portion of available cash proportionally to the number of mentions for each company.
Buys as many shares as the allocated budget allows at the current price.
Updates the portfolio object with new holdings, cash balance, and transaction history.
Saves the state to CSV files so purchases, holdings, and cash are persisted between runs.

Note: The strategy is illustrative, not financial advice. Prices are fetched live, and allocations are simplified; users can replace price_provider with a different source or modify the allocation logic.

# Setup
Clone the repository using `git clone https://github.com/yourusername/yourrepo.git` and `cd yourrepo`. Install dependencies with `pip install feedparser yfinance`. Update `ticker_dict.py` with your list of tickers and company names if needed. Optionally, set paths in `feed_logger.py` such as `LOG_FILE`, `SEEN_FILE`, and `FEED_URL`.

# Usage
Run the script manually using `python feed_logger.py` or schedule it to run periodically via Task Scheduler. The script fetches new headlines, counts mentions of companies, appends results to the CSV log, and skips headlines that have already been seen.

# Output
`feed_counts.csv` contains cumulative logs of company mentions with timestamps. `seen_headlines.txt` tracks processed headlines to prevent double-counting (ignored in GitHub via `.gitignore`). Example CSV row: `2025-12-13 12:00:00, Microsoft, 5`.

For the buy strategy, additional CSV files are used to track your portfolio:
portfolio.csv – current holdings (company and number of shares)
transactions.csv – transaction history including timestamp, shares bought, price, and total cost
cash_available.csv – remaining cash available for buying

These files are updated automatically whenever the buy strategy runs and are ignored in GitHub via .gitignore.

# Contributing
Add new tickers to `ticker_dict.py`, ensure `.gitignore` is respected (don’t commit local CSV or seen files), and use branches/PRs if collaborating with friends.




