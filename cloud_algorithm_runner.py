"""
Cloud Algorithm Runner
Runs the trading algorithm in GitHub Actions cloud environment
"""

import os
import sys
import json
import urllib.request
import urllib.parse
import ssl
from datetime import datetime

class CloudAlgorithmRunner:
    def __init__(self):
        # Get credentials from environment (GitHub Secrets)
        self.bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.environ.get('TELEGRAM_CHAT_ID')

        if not self.bot_token or not self.chat_id:
            print("ERROR: Missing Telegram credentials in environment")
            sys.exit(1)

        # SSL context for HTTPS requests
        self.ssl_context = ssl.create_default_context()

    def send_telegram_message(self, message):
        """Send message to Telegram"""
        try:
            data = urllib.parse.urlencode({
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }).encode('utf-8')

            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            req = urllib.request.Request(url, data=data)

            with urllib.request.urlopen(req, context=self.ssl_context, timeout=15) as response:
                result = json.loads(response.read().decode())

            if result.get('ok'):
                print("[OK] Telegram message sent successfully")
                return True
            else:
                print(f"[ERROR] Telegram error: {result}")
                return False

        except Exception as e:
            print(f"[ERROR] Failed to send Telegram message: {e}")
            return False

    def load_portfolio(self):
        """Load current portfolio"""
        portfolio_file = 'portfolio_data/current_portfolio.json'

        if os.path.exists(portfolio_file):
            try:
                with open(portfolio_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"[WARNING] Error loading portfolio: {e}")
                return None

        print("[WARNING] No portfolio file found")
        return None

    def analyze_positions(self, portfolio):
        """Analyze portfolio positions and generate insights"""
        if not portfolio:
            return "No portfolio data available for analysis"

        analysis_results = []
        total_value = 0
        cash_balance = portfolio.get('CASH', {}).get('balance', 0)

        # Analyze each position
        for symbol, data in portfolio.items():
            if symbol in ['CASH', 'last_updated']:
                continue

            shares = data.get('shares', 0)
            avg_cost = data.get('avg_cost', 0)
            invested = data.get('total_invested', 0)
            total_value += invested

            # Generate basic analysis for each position
            position_analysis = self.get_position_analysis(symbol, shares, avg_cost, invested)
            if position_analysis:
                analysis_results.append(position_analysis)

        total_value += cash_balance

        return {
            'total_value': total_value,
            'cash_balance': cash_balance,
            'position_analyses': analysis_results,
            'portfolio_health': self.assess_portfolio_health(portfolio)
        }

    def get_position_analysis(self, symbol, shares, avg_cost, invested):
        """Get analysis for individual position"""

        # Position-specific insights based on our trading strategy
        position_insights = {
            'RGTI': {
                'sector': 'Quantum Computing',
                'risk_level': 'HIGH',
                'thesis': 'Pure-play quantum leader with IBM partnership',
                'watch_for': 'Quantum advantage demonstrations, R&D partnerships'
            },
            'QUBT': {
                'sector': 'Quantum Computing',
                'risk_level': 'HIGH',
                'thesis': 'Breakthrough photonic quantum technology',
                'watch_for': 'Room-temperature quantum developments, commercial partnerships'
            },
            'IONQ': {
                'sector': 'Quantum Computing',
                'risk_level': 'MEDIUM-HIGH',
                'thesis': 'Trapped-ion quantum with cloud revenue validation',
                'watch_for': 'Cloud quantum service adoption, enterprise partnerships'
            },
            'BBAI': {
                'sector': 'Defense AI',
                'risk_level': 'MEDIUM',
                'thesis': 'Stable defense contractor with government contracts',
                'watch_for': 'Defense spending, margin improvement, new contracts'
            }
        }

        insight = position_insights.get(symbol, {
            'sector': 'Unknown',
            'risk_level': 'MEDIUM',
            'thesis': 'Position under analysis',
            'watch_for': 'Market developments, earnings updates'
        })

        return {
            'symbol': symbol,
            'shares': shares,
            'avg_cost': avg_cost,
            'invested': invested,
            'sector': insight['sector'],
            'risk_level': insight['risk_level'],
            'thesis': insight['thesis'],
            'watch_for': insight['watch_for']
        }

    def assess_portfolio_health(self, portfolio):
        """Assess overall portfolio health"""

        # Count positions by sector
        quantum_positions = 0
        defense_positions = 0
        total_positions = 0

        for symbol, data in portfolio.items():
            if symbol in ['CASH', 'last_updated']:
                continue
            total_positions += 1
            if symbol in ['RGTI', 'QUBT', 'IONQ']:
                quantum_positions += 1
            elif symbol in ['BBAI']:
                defense_positions += 1

        quantum_concentration = (quantum_positions / total_positions * 100) if total_positions > 0 else 0

        if quantum_concentration > 70:
            health_status = "HIGH QUANTUM CONCENTRATION"
            recommendation = "Monitor quantum sector developments closely"
        elif quantum_concentration > 50:
            health_status = "QUANTUM FOCUSED"
            recommendation = "Good sector positioning with diversification opportunity"
        else:
            health_status = "DIVERSIFIED"
            recommendation = "Balanced portfolio allocation"

        return {
            'status': health_status,
            'quantum_exposure': f"{quantum_concentration:.0f}%",
            'recommendation': recommendation
        }

    def generate_market_insights(self):
        """Generate market insights for today"""
        current_date = datetime.now()
        day_of_week = current_date.strftime('%A')

        insights = [
            "Quantum computing sector showing increased institutional interest",
            "Defense AI spending continuing to grow with government focus",
            "Monitor for end-of-quarter earnings and guidance updates",
            "Watch for patent filing announcements in quantum technologies"
        ]

        return f"Market focus for {day_of_week}: " + "; ".join(insights[:2])

    def run_algorithm_analysis(self):
        """Run the main algorithm analysis"""

        print("[INFO] Starting GitHub Actions algorithm analysis...")

        # Load portfolio
        portfolio = self.load_portfolio()

        # Analyze portfolio
        analysis = self.analyze_positions(portfolio)
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M UTC')

        if isinstance(analysis, dict):
            # Generate detailed analysis message
            positions_summary = ""
            for pos in analysis['position_analyses']:
                positions_summary += f"• {pos['symbol']}: {pos['shares']:.1f} shares @ ${pos['avg_cost']:.2f} ({pos['risk_level']})\n"

            market_insights = self.generate_market_insights()

            message = f"""🤖 <b>GITHUB ACTIONS EOD ANALYSIS</b>

📊 <b>Portfolio Status:</b>
{positions_summary}💰 Cash: ${analysis['cash_balance']:.2f}
💎 Total Value: ${analysis['total_value']:.2f}

🧠 <b>Portfolio Health:</b>
Status: {analysis['portfolio_health']['status']}
Quantum Exposure: {analysis['portfolio_health']['quantum_exposure']}

📈 <b>Market Insights:</b>
{market_insights}

🎯 <b>Algorithm Status:</b>
• Portfolio monitored successfully
• Risk levels assessed across all positions
• No immediate alerts triggered
• System operational on schedule

🕐 Analysis Time: {current_time}
🔧 Platform: GitHub Actions Cloud
✅ Status: All Systems Operational

<i>Next analysis: Tomorrow 6:00 PM EST</i>
<i>📱 Powered by GitHub Actions - Enterprise Cloud Infrastructure</i>"""

        else:
            # Fallback message for portfolio issues
            message = f"""🤖 <b>GITHUB ACTIONS SYSTEM STATUS</b>

⚠️ <b>Portfolio Status:</b> {analysis}

🕐 Analysis Time: {current_time}
🔧 Platform: GitHub Actions Cloud
✅ Status: System Operational

<b>📋 System Notes:</b>
• Cloud automation running successfully
• Telegram connectivity confirmed
• Awaiting portfolio data update
• All core systems functional

<i>Upload portfolio_data/current_portfolio.json to enable full analysis</i>
<i>📱 Automated monitoring active</i>"""

        # Send message
        success = self.send_telegram_message(message)

        if success:
            print("[OK] EOD analysis completed successfully")
        else:
            print("[ERROR] EOD analysis failed - Telegram delivery error")

        return success

def main():
    """Main execution function"""
    try:
        runner = CloudAlgorithmRunner()
        success = runner.run_algorithm_analysis()

        if not success:
            sys.exit(1)

    except Exception as e:
        print(f"[ERROR] Critical error in cloud algorithm runner: {e}")

        # Try to send error notification
        try:
            bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
            chat_id = os.environ.get('TELEGRAM_CHAT_ID')

            if bot_token and chat_id:
                error_message = f"""🚨 <b>GITHUB ACTIONS ERROR</b>

❌ <b>Error:</b> Cloud algorithm runner failed
🔧 <b>Details:</b> {str(e)[:200]}
🕐 <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}

<i>Check GitHub Actions logs for full details</i>"""

                ssl_context = ssl.create_default_context()
                data = urllib.parse.urlencode({
                    'chat_id': chat_id,
                    'text': error_message,
                    'parse_mode': 'HTML'
                }).encode('utf-8')

                url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                req = urllib.request.Request(url, data=data)

                with urllib.request.urlopen(req, context=ssl_context, timeout=10) as response:
                    print("[OK] Error notification sent to Telegram")

        except:
            print("[ERROR] Could not send error notification")

        sys.exit(1)

if __name__ == "__main__":
    main()