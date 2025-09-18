"""
Simple Portfolio Manager - No Unicode Issues
============================================
"""

import os
import json
import csv
from datetime import datetime

class SimplePortfolio:
    def __init__(self):
        self.base_dir = os.path.dirname(__file__)
        self.data_dir = os.path.join(self.base_dir, 'portfolio_data')
        self.portfolio_file = os.path.join(self.data_dir, 'current_portfolio.json')
        self.transactions_file = os.path.join(self.data_dir, 'transactions.csv')

        os.makedirs(self.data_dir, exist_ok=True)
        self.portfolio = self.load_portfolio()

    def load_portfolio(self):
        if os.path.exists(self.portfolio_file):
            try:
                with open(self.portfolio_file, 'r') as f:
                    return json.load(f)
            except:
                return self.init_portfolio()
        else:
            return self.init_portfolio()

    def init_portfolio(self):
        return {
            'RGTI': {'shares': 46.15, 'avg_cost': 19.50, 'total_invested': 900.00},
            'BBAI': {'shares': 157.89, 'avg_cost': 3.80, 'total_invested': 600.00},
            'QUBT': {'shares': 46.58, 'avg_cost': 3.22, 'total_invested': 150.00},
            'IONQ': {'shares': 11.83, 'avg_cost': 8.45, 'total_invested': 100.00},
            'CASH': {'balance': 650.00},
            'last_updated': datetime.now().isoformat()
        }

    def save_portfolio(self):
        self.portfolio['last_updated'] = datetime.now().isoformat()
        with open(self.portfolio_file, 'w') as f:
            json.dump(self.portfolio, f, indent=2)

    def save_transaction(self, trans_data):
        file_exists = os.path.exists(self.transactions_file)
        with open(self.transactions_file, 'a', newline='') as f:
            fieldnames = ['date', 'symbol', 'action', 'shares', 'price', 'amount', 'notes']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow(trans_data)

    def buy_stock(self, symbol, shares_or_amount, price, is_dollar_amount=False):
        symbol = symbol.upper()

        if is_dollar_amount:
            dollar_amount = shares_or_amount
            shares = dollar_amount / price
        else:
            shares = shares_or_amount
            dollar_amount = shares * price

        if self.portfolio['CASH']['balance'] < dollar_amount:
            print(f"[ERROR] Not enough cash! Need ${dollar_amount:.2f}, have ${self.portfolio['CASH']['balance']:.2f}")
            return False

        self.portfolio['CASH']['balance'] -= dollar_amount

        if symbol in self.portfolio and symbol != 'CASH':
            old_shares = self.portfolio[symbol]['shares']
            old_total = self.portfolio[symbol]['total_invested']
            new_shares = old_shares + shares
            new_total = old_total + dollar_amount
            new_avg_cost = new_total / new_shares

            self.portfolio[symbol] = {
                'shares': new_shares,
                'avg_cost': new_avg_cost,
                'total_invested': new_total
            }
        else:
            self.portfolio[symbol] = {
                'shares': shares,
                'avg_cost': price,
                'total_invested': dollar_amount
            }

        transaction = {
            'date': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'symbol': symbol,
            'action': 'BUY',
            'shares': shares,
            'price': price,
            'amount': dollar_amount,
            'notes': f"{'Dollar amount' if is_dollar_amount else 'Share count'} purchase"
        }

        self.save_transaction(transaction)
        self.save_portfolio()

        print(f"[OK] BUY CONFIRMED:")
        print(f"     {shares:.2f} shares of {symbol} at ${price:.2f}")
        print(f"     Total: ${dollar_amount:.2f}")
        print(f"     Cash remaining: ${self.portfolio['CASH']['balance']:.2f}")

        return True

    def sell_stock(self, symbol, shares_or_percentage, price, is_percentage=False):
        symbol = symbol.upper()

        if symbol not in self.portfolio or symbol == 'CASH':
            print(f"[ERROR] No position in {symbol}")
            return False

        if is_percentage:
            percentage = shares_or_percentage
            total_shares = self.portfolio[symbol]['shares']
            shares = total_shares * (percentage / 100)
        else:
            shares = shares_or_percentage

        if self.portfolio[symbol]['shares'] < shares:
            print(f"[ERROR] Not enough shares! Have {self.portfolio[symbol]['shares']:.2f}, trying to sell {shares:.2f}")
            return False

        dollar_amount = shares * price
        self.portfolio['CASH']['balance'] += dollar_amount

        remaining_shares = self.portfolio[symbol]['shares'] - shares

        if remaining_shares == 0:
            del self.portfolio[symbol]
            print(f"[OK] POSITION CLOSED: {symbol}")
        else:
            old_avg_cost = self.portfolio[symbol]['avg_cost']
            new_total_invested = remaining_shares * old_avg_cost

            self.portfolio[symbol] = {
                'shares': remaining_shares,
                'avg_cost': old_avg_cost,
                'total_invested': new_total_invested
            }
            print(f"[OK] PARTIAL SALE: {shares:.2f} shares of {symbol}")

        transaction = {
            'date': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'symbol': symbol,
            'action': 'SELL',
            'shares': shares,
            'price': price,
            'amount': dollar_amount,
            'notes': f"{'Percentage' if is_percentage else 'Share count'} sale"
        }

        self.save_transaction(transaction)
        self.save_portfolio()

        print(f"     {shares:.2f} shares at ${price:.2f}")
        print(f"     Total received: ${dollar_amount:.2f}")
        print(f"     Cash balance: ${self.portfolio['CASH']['balance']:.2f}")

        return True

    def show_portfolio(self):
        print("\n" + "="*50)
        print("CURRENT PORTFOLIO")
        print("="*50)

        total_value = 0
        cash = self.portfolio['CASH']['balance']

        for symbol, data in self.portfolio.items():
            if symbol in ['CASH', 'last_updated']:
                continue

            shares = data['shares']
            avg_cost = data['avg_cost']
            invested = data['total_invested']

            print(f"\n{symbol}:")
            print(f"  Shares: {shares:.2f}")
            print(f"  Avg Cost: ${avg_cost:.2f}")
            print(f"  Invested: ${invested:.2f}")

            total_value += invested

        print(f"\nCASH: ${cash:.2f}")
        print(f"TOTAL PORTFOLIO: ${total_value + cash:.2f}")
        print("="*50)

    def quick_menu(self):
        while True:
            print("\nPORTFOLIO MANAGER")
            print("-" * 20)
            print("1. Buy Stock")
            print("2. Sell Stock")
            print("3. View Portfolio")
            print("4. Recent Transactions")
            print("5. Exit")

            choice = input("\nSelect (1-5): ").strip()

            if choice == '1':
                self.quick_buy()
            elif choice == '2':
                self.quick_sell()
            elif choice == '3':
                self.show_portfolio()
            elif choice == '4':
                self.show_recent_transactions()
            elif choice == '5':
                print("Goodbye!")
                break
            else:
                print("[ERROR] Invalid choice")

    def quick_buy(self):
        print("\nBUY STOCK")
        print("-" * 10)

        symbol = input("Symbol (e.g., RGTI): ").upper()
        amount_type = input("Enter (1) dollar amount or (2) number of shares? ").strip()
        price = float(input(f"Current price of {symbol}: $"))

        if amount_type == '1':
            amount = float(input("Dollar amount to invest: $"))
            self.buy_stock(symbol, amount, price, is_dollar_amount=True)
        else:
            shares = float(input("Number of shares: "))
            self.buy_stock(symbol, shares, price, is_dollar_amount=False)

    def quick_sell(self):
        print("\nSELL STOCK")
        print("-" * 10)

        positions = [s for s in self.portfolio.keys() if s not in ['CASH', 'last_updated']]
        if not positions:
            print("[ERROR] No positions to sell")
            return

        print("Current positions:")
        for i, symbol in enumerate(positions, 1):
            shares = self.portfolio[symbol]['shares']
            print(f"  {i}. {symbol} ({shares:.2f} shares)")

        try:
            choice = int(input(f"\nSelect position (1-{len(positions)}): ")) - 1
            symbol = positions[choice]
        except:
            print("[ERROR] Invalid selection")
            return

        price = float(input(f"Current price of {symbol}: $"))
        sell_type = input("Sell (1) percentage or (2) number of shares? ").strip()

        if sell_type == '1':
            percentage = float(input("Percentage to sell (e.g., 50 for 50%): "))
            self.sell_stock(symbol, percentage, price, is_percentage=True)
        else:
            shares = float(input("Number of shares to sell: "))
            self.sell_stock(symbol, shares, price, is_percentage=False)

    def show_recent_transactions(self):
        if not os.path.exists(self.transactions_file):
            print("No transactions yet")
            return

        print("\nRECENT TRANSACTIONS")
        print("-" * 30)

        with open(self.transactions_file, 'r') as f:
            reader = csv.DictReader(f)
            transactions = list(reader)

        recent = transactions[-10:] if len(transactions) > 10 else transactions

        for trans in reversed(recent):
            action_symbol = "BUY" if trans['action'] == 'BUY' else "SELL"
            print(f"{trans['date']} | {action_symbol} {trans['shares']} {trans['symbol']} @ ${trans['price']} = ${trans['amount']}")

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == 'buy' and len(sys.argv) >= 5:
            manager = SimplePortfolio()
            symbol, amount, price = sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
            manager.buy_stock(symbol, amount, price, is_dollar_amount=True)
        elif sys.argv[1] == 'sell' and len(sys.argv) >= 5:
            manager = SimplePortfolio()
            symbol, percentage, price = sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
            manager.sell_stock(symbol, percentage, price, is_percentage=True)
        elif sys.argv[1] == 'portfolio':
            manager = SimplePortfolio()
            manager.show_portfolio()
        else:
            print("Usage:")
            print("  py simple_portfolio.py buy SYMBOL DOLLARS PRICE")
            print("  py simple_portfolio.py sell SYMBOL PERCENTAGE PRICE")
            print("  py simple_portfolio.py portfolio")
    else:
        manager = SimplePortfolio()
        manager.quick_menu()