"""
Market Open Intelligence Brief
Specialized 9:30 AM report focused on overnight developments and trading opportunities
"""

import os
import csv
import json
import urllib.request
import urllib.parse
import ssl
from datetime import datetime, timedelta
import time

class MarketOpenBrief:
    """Generate focused market open intelligence brief"""

    def __init__(self):
        self.base_dir = os.path.dirname(__file__)
        self.data_dir = os.path.join(self.base_dir, 'data')
        self.output_dir = os.path.join(self.base_dir, 'output')

        # Telegram configuration
        self.telegram_config = {
            'bot_token': '8339992762:AAF_JmZpaeVZGY0a-r6z4CuLblCFqBQQDtY',
            'chat_id': '7970392707'  # Kyle's chat ID
        }

        # Portfolio configuration
        self.current_portfolio = {
            'RGTI': {'shares': 3.14, 'entry_price': 19.09},
            'BBAI': {'shares': 11.86, 'entry_price': 5.06},
            'LAES': {'shares': 17.80, 'entry_price': 3.37}
        }

        # Watchlist for quick monitoring
        self.watchlist = ['ARQQ', 'IONQ', 'INOD', 'RKLB']

        # SSL context
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE

        os.makedirs(self.output_dir, exist_ok=True)

    def load_api_keys(self):
        """Load API keys from CSV file"""
        api_keys = {}
        try:
            csv_path = os.path.join(self.data_dir, 'Oriana APIs - APIs.csv')
            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                for row in reader:
                    if len(row) >= 2 and row[1].strip():
                        api_keys[row[0].strip()] = row[1].strip()
            return api_keys
        except Exception as e:
            print(f"Error loading API keys: {e}")
            return {}

    def get_pre_market_data(self):
        """Get current market data for portfolio and watchlist"""
        api_keys = self.load_api_keys()
        if 'FMP' not in api_keys:
            return {}

        all_symbols = list(self.current_portfolio.keys()) + self.watchlist
        market_data = {}

        for symbol in all_symbols:
            try:
                url = f"https://financialmodelingprep.com/api/v3/quote/{symbol}?apikey={api_keys['FMP']}"
                with urllib.request.urlopen(url, context=self.ssl_context, timeout=10) as response:
                    data = json.loads(response.read().decode())

                if data and isinstance(data, list) and len(data) > 0:
                    quote = data[0]
                    market_data[symbol] = {
                        'price': quote.get('price', 0),
                        'change': quote.get('change', 0),
                        'change_pct': quote.get('changesPercentage', 0),
                        'volume': quote.get('volume', 0),
                        'avg_volume': quote.get('avgVolume', 0),
                        'day_high': quote.get('dayHigh', 0),
                        'day_low': quote.get('dayLow', 0),
                        'previous_close': quote.get('previousClose', 0)
                    }

                time.sleep(0.1)

            except Exception as e:
                print(f"Market data error for {symbol}: {e}")

        return market_data

    def get_overnight_news(self):
        """Get overnight news for portfolio stocks"""
        api_keys = self.load_api_keys()
        if 'NewsAPI' not in api_keys:
            return {}

        # Look for news from last 18 hours (overnight + pre-market)
        from_date = (datetime.now() - timedelta(hours=18)).strftime('%Y-%m-%dT%H:%M:%S')

        portfolio_news = {}
        all_symbols = list(self.current_portfolio.keys()) + self.watchlist

        for symbol in all_symbols:
            try:
                url = f"https://newsapi.org/v2/everything?q={symbol}&apiKey={api_keys['NewsAPI']}&sortBy=publishedAt&pageSize=3&language=en&from={from_date}"

                with urllib.request.urlopen(url, context=self.ssl_context, timeout=10) as response:
                    data = json.loads(response.read().decode())

                articles = data.get('articles', [])
                if articles:
                    portfolio_news[symbol] = articles[:2]  # Top 2 overnight articles

                time.sleep(0.1)

            except Exception as e:
                print(f"News error for {symbol}: {e}")

        return portfolio_news

    def check_position_alerts(self, market_data):
        """Check for any position alerts at market open"""
        alerts = []

        for symbol, position in self.current_portfolio.items():
            if symbol not in market_data:
                continue

            current_price = market_data[symbol]['price']
            entry_price = position['entry_price']
            change_pct = ((current_price - entry_price) / entry_price) * 100

            # Check for significant overnight moves
            daily_change_pct = market_data[symbol]['change_pct']

            # Emergency alert (down 20% from entry)
            if change_pct <= -20:
                alerts.append({
                    'type': 'EMERGENCY',
                    'symbol': symbol,
                    'message': f"🚨 {symbol} down {change_pct:.1f}% from entry - REVIEW POSITION"
                })

            # Stop loss alert (down 15% from entry)
            elif change_pct <= -15:
                alerts.append({
                    'type': 'STOP_LOSS',
                    'symbol': symbol,
                    'message': f"⚠️ {symbol} at stop-loss level ({change_pct:.1f}% from entry)"
                })

            # Big overnight move (up or down 5%+)
            elif abs(daily_change_pct) >= 5:
                direction = "📈" if daily_change_pct > 0 else "📉"
                alerts.append({
                    'type': 'BIG_MOVE',
                    'symbol': symbol,
                    'message': f"{direction} {symbol} moved {daily_change_pct:+.1f}% overnight"
                })

            # Profit harvest (up 50% from entry)
            elif change_pct >= 50:
                alerts.append({
                    'type': 'PROFIT_HARVEST',
                    'symbol': symbol,
                    'message': f"🎯 {symbol} up {change_pct:.1f}% - consider profit taking"
                })

        return alerts

    def format_market_open_brief(self, market_data, overnight_news, alerts):
        """Format market open brief for Telegram"""

        message = f"""🌅 <b>MARKET OPEN BRIEF</b> 🌅
<b>{datetime.now().strftime('%B %d, %Y • 9:30 AM ET')}</b>

🚨 <b>POSITION ALERTS</b>"""

        if alerts:
            for alert in alerts:
                message += f"\n• {alert['message']}"
        else:
            message += f"\n• All positions stable - no immediate alerts"

        message += f"\n\n📊 <b>PORTFOLIO PRE-MARKET</b>"

        for symbol in self.current_portfolio.keys():
            if symbol in market_data:
                data = market_data[symbol]
                price = data['price']
                change_pct = data['change_pct']
                volume = data['volume']
                avg_volume = data['avg_volume']

                # Volume analysis
                volume_indicator = ""
                if avg_volume > 0:
                    volume_ratio = volume / avg_volume
                    if volume_ratio > 2:
                        volume_indicator = " 🔥 HIGH VOL"
                    elif volume_ratio > 1.5:
                        volume_indicator = " 📈 ABOVE AVG"

                emoji = "📈" if change_pct >= 0 else "📉"
                message += f"\n<b>{symbol}</b>: ${price:.2f} {emoji}{change_pct:+.1f}%{volume_indicator}"

        message += f"\n\n👀 <b>WATCHLIST</b>"

        for symbol in self.watchlist:
            if symbol in market_data:
                data = market_data[symbol]
                price = data['price']
                change_pct = data['change_pct']
                emoji = "📈" if change_pct >= 0 else "📉"
                message += f"\n<b>{symbol}</b>: ${price:.2f} {emoji}{change_pct:+.1f}%"

        # Overnight news highlights
        if overnight_news:
            message += f"\n\n📰 <b>OVERNIGHT NEWS</b>"
            news_count = 0
            for symbol, articles in overnight_news.items():
                for article in articles:
                    if news_count < 3:  # Limit to top 3 overnight stories
                        title = article.get('title', '')[:60] + ('...' if len(article.get('title', '')) > 60 else '')
                        message += f"\n• <b>{symbol}</b>: {title}"
                        news_count += 1

        # Market context
        message += f"\n\n🎯 <b>TRADING FOCUS</b>"

        # Find biggest movers
        big_movers = []
        for symbol, data in market_data.items():
            if abs(data['change_pct']) >= 3:
                big_movers.append((symbol, data['change_pct']))

        if big_movers:
            big_movers.sort(key=lambda x: abs(x[1]), reverse=True)
            message += f"\n• Biggest mover: {big_movers[0][0]} ({big_movers[0][1]:+.1f}%)"

        # Check for high volume stocks
        high_vol_stocks = []
        for symbol, data in market_data.items():
            if data['avg_volume'] > 0 and data['volume'] / data['avg_volume'] > 2:
                high_vol_stocks.append(symbol)

        if high_vol_stocks:
            message += f"\n• High volume: {', '.join(high_vol_stocks[:3])}"

        message += f"\n\n⏰ <b>Next Report:</b> 6:00 PM (Full EOD Analysis)"
        message += f"\n🎯 <b>Real-time alerts:</b> Active during trading hours"

        return message

    def send_telegram_message(self, message):
        """Send message via Telegram"""
        try:
            data = urllib.parse.urlencode({
                'chat_id': self.telegram_config['chat_id'],
                'text': message,
                'parse_mode': 'HTML'
            }).encode('utf-8')

            url = f"https://api.telegram.org/bot{self.telegram_config['bot_token']}/sendMessage"
            req = urllib.request.Request(url, data=data)

            with urllib.request.urlopen(req, context=self.ssl_context, timeout=10) as response:
                result = json.loads(response.read().decode())

            return result.get('ok', False)

        except Exception as e:
            print(f"Telegram message failed: {e}")
            return False

    def generate_market_open_brief(self):
        """Generate and send market open brief"""
        print("GENERATING MARKET OPEN INTELLIGENCE BRIEF")
        print("=" * 45)

        # Get pre-market data
        print("Fetching pre-market data...")
        market_data = self.get_pre_market_data()

        # Get overnight news
        print("Scanning overnight news...")
        overnight_news = self.get_overnight_news()

        # Check for alerts
        print("Checking position alerts...")
        alerts = self.check_position_alerts(market_data)

        # Format brief
        telegram_message = self.format_market_open_brief(market_data, overnight_news, alerts)

        # Send brief
        print("Sending market open brief to Telegram...")
        success = self.send_telegram_message(telegram_message)

        if success:
            print("SUCCESS: Market open brief sent to Kyle's Telegram!")

            # Save brief copy
            today_str = datetime.now().strftime('%Y%m%d_%H%M')
            brief_data = {
                'market_data': market_data,
                'overnight_news': overnight_news,
                'alerts': alerts,
                'generated_at': datetime.now().isoformat()
            }

            json_file = os.path.join(self.output_dir, f'Market_Open_Brief_{today_str}.json')
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(brief_data, f, indent=2, default=str)

            print(f"Brief data saved: {json_file}")
            return True
        else:
            print("FAILED: Could not send market open brief")
            return False

def main():
    """Main function"""
    brief = MarketOpenBrief()
    brief.generate_market_open_brief()

if __name__ == "__main__":
    main()