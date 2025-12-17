import csv
import time
from datetime import datetime
import yfinance as yf #Used to import live prices; amend logic as desired depending on choice of API
import json

with open("company_to_tickers.json", encoding="utf-8") as f:
    company_to_tickers = json.load(f) #dictionary of companies -> tickers. Essentially inverse of ticker_dict.


class Portfolio:
    """
    This class checks first if the files in question already exist.
    If they do, it loads the relevant data into self.holdings, history etc.
    If they don't, it creates a new file. 
    See later comments for how the state is saved under if __name__ == "__main__"
    """
    def __init__(self, holdings_file="portfolio.csv", history_file="transactions.csv", seen_file="seen_rows.csv", cash_available_file="cash_available.csv"):
        self.holdings_file = holdings_file
        self.history_file = history_file
        self.seen_file = seen_file
        self.cash_available_file = cash_available_file
        self.holdings = {}   
        self.history = []    #transaction log
        self.seen_rows = set()  #timestamp+company tuples
        self.cash = 100000
        self.load_state()
    
    def load_state(self):
        #Holdings
        try:
            with open(self.holdings_file, newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                for row in reader:
                    company, shares = row
                    self.holdings[company] = float(shares)
        except FileNotFoundError:
            pass

        #Transactions
        try:
            with open(self.history_file, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    row["shares"] = float(row["shares"])
                    row["price"] = float(row["price"])
                    row["cost"] = float(row["cost"])
                    self.history.append(row)
        except FileNotFoundError:
            pass

        #Seen rows
        try:
            with open(self.seen_file, newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                for row in reader:
                    self.seen_rows.add(tuple(row))
        except FileNotFoundError:
            pass

        #Cash
        try:
            with open(self.cash_available_file, newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                rows = list(reader)
                self.cash = float(rows[-1][0])
        except FileNotFoundError:
            pass
    
    def save_state(self):
        #Holdings
        with open(self.holdings_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for company, shares in self.holdings.items():
                writer.writerow([company, shares])

        #Cash
        with open(self.cash_available_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([self.cash])
        
            
        #Transactions
        if self.history:
            fieldnames = ["timestamp", "company", "shares", "price", "cost"]
            with open(self.history_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for tx in self.history:
                    writer.writerow(tx)

        #Seen rows
        with open(self.seen_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for key in self.seen_rows:
                writer.writerow(key)

    def buy(self, company, shares, price):
        if shares <= 0 or price <= 0:
            return
        affordable_shares = min(shares, self.cash / price)
        if affordable_shares <= 0:
            return  
        cost = affordable_shares * price
        self.cash -= cost
        self.holdings[company] = self.holdings.get(company, 0) + affordable_shares
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.history.append({
            "timestamp": timestamp,
            "company": company,
            "shares": affordable_shares,
            "price": price,
            "cost": cost
        })

    def summary(self):
        print(f"Cash: ${self.cash:.2f}")
        for company, shares in self.holdings.items():
            print(f"{company}: {shares:.4f} shares")
        print()

def read_new_rows(csv_file, portfolio):
    new_rows = []
    with open(csv_file, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            key = (row[0], row[1])
            if key not in portfolio.seen_rows:
                new_rows.append(row)
                portfolio.seen_rows.add(key)
    return new_rows

def maintain_count(rows):
    counts = {}
    for entry in rows:
        if entry[1] not in counts:
            counts[entry[1]] = 1
        else: 
            counts[entry[1]] += 1
    return counts

PRICE_CACHE = {}

def price_provider(company):
    if company in PRICE_CACHE:
        return PRICE_CACHE[company]

    tickers = company_to_tickers.get(company)
    if not tickers:
        return None

    ticker = tickers[0]  #In case of multiple tickers, we take the first one available.

    try:
        data = yf.Ticker(ticker).history(period="1d")
        if not data.empty:
            price = float(data["Close"].iloc[-1])
            PRICE_CACHE[company] = price
            return price
    except Exception as e:
        print(f"Price fetch failed for {company} ({ticker}): {e}")

    return None

def buy_strategy(portfolio, to_buy, price_provider):
    total_mentions = sum(to_buy.values())
    if total_mentions == 0:
        print("No new mentions to buy.")
        return

    for company, mentions in to_buy.items():
        price = price_provider(company)
        if price is None:
            print(f"No price for {company}, skipping.")
            continue
        
        allocation = (min(portfolio.cash, 10000)) * (mentions / total_mentions)
        shares = allocation / price

        portfolio.buy(
            company=company,
            shares=shares,
            price=price
        )
       


if __name__ == "__main__":
    portfolio = Portfolio()
    new_rows = read_new_rows("feed_counts.csv", portfolio)
    to_buy = maintain_count(new_rows)

    """
    This updates the portfolio. 
    Prevents wiping of data so long as the csv's are maintained.
    """
    buy_strategy(portfolio, to_buy, price_provider)
    portfolio.save_state()  

    print("\nPortfolio summary:")
    portfolio.summary()