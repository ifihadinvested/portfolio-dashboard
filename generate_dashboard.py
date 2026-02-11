import xml.etree.ElementTree as ET
import json
from datetime import datetime

def parse_portfolio():
    """Parse IBKR XML to JSON"""
    tree = ET.parse('portfolio_data.xml')
    root = tree.getroot()
    
    holdings = []
    
    # Find OpenPositions section
    for position in root.findall('.//OpenPosition'):
        symbol = position.get('symbol', 'N/A')
        quantity = float(position.get('position', 0))
        price = float(position.get('markPrice', 0))
        value = float(position.get('positionValue', 0))
        pnl = float(position.get('fifoPnlUnrealized', 0))
        
        if value != 0:  # Only include non-zero positions
            holdings.append({
                'symbol': symbol,
                'quantity': int(quantity),
                'price': round(price, 2),
                'value': round(value, 2),
                'pnl': round(pnl, 2)
            })
    
    # Sort by value (largest first)
    holdings.sort(key=lambda x: abs(x['value']), reverse=True)
    
    return holdings

def generate_html(holdings):
    """Generate dashboard HTML"""
    
    total_value = sum(abs(h['value']) for h in holdings)
    total_pnl = sum(h['pnl'] for h in holdings)
    update_time = datetime.now().strftime('%Y-%m-%d %H:%M UTC')
    
    # Top 10 holdings
    top_holdings = holdings[:10]
    
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Portfolio Dashboard | ifihadinvested.com</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
            background: #0a0a0a;
            color: #e0e0e0;
            padding: 20px;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        h1 {{ 
            font-size: 2.5rem; 
            margin-bottom: 10px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .subtitle {{ color: #888; margin-bottom: 30px; font-size: 0.9rem; }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        .stat-card {{
            background: #1a1a1a;
            padding: 25px;
            border-radius: 12px;
            border: 1px solid #2a2a2a;
        }}
        .stat-label {{ color: #888; font-size: 0.85rem; margin-bottom: 8px; }}
        .stat-value {{ font-size: 2rem; font-weight: 600; }}
        .positive {{ color: #22c55e; }}
        .negative {{ color: #ef4444; }}
        table {{
            width: 100%;
            background: #1a1a1a;
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid #2a2a2a;
        }}
        th, td {{
            padding: 16px;
            text-align: left;
        }}
        th {{
            background: #2a2a2a;
            font-weight: 600;
            font-size: 0.9rem;
            color: #aaa;
        }}
        tr:not(:last-child) {{ border-bottom: 1px solid #2a2a2a; }}
        .symbol {{ font-weight: 600; font-size: 1.1rem; }}
        .value {{ font-family: 'Courier New', monospace; }}
        footer {{
            margin-top: 60px;
            text-align: center;
            color: #666;
            font-size: 0.85rem;
        }}
        a {{ color: #667eea; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Live Portfolio Dashboard</h1>
        <div class="subtitle">Auto-synced from Interactive Brokers | Last update: {update_time}</div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-label">Total Portfolio Value</div>
                <div class="stat-value">${total_value:,.0f}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Total P&L</div>
                <div class="stat-value {'positive' if total_pnl >= 0 else 'negative'}">${total_pnl:+,.0f}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Positions</div>
                <div class="stat-value">{len(holdings)}</div>
            </div>
        </div>
        
        <h2 style="margin-bottom: 20px; color: #ccc;">Top 10 Holdings</h2>
        <table>
            <thead>
                <tr>
                    <th>Symbol</th>
                    <th>Quantity</th>
                    <th>Price</th>
                    <th>Value</th>
                    <th>P&L</th>
                </tr>
            </thead>
            <tbody>
"""
    
    for h in top_holdings:
        pnl_class = 'positive' if h['pnl'] >= 0 else 'negative'
        html += f"""
                <tr>
                    <td class="symbol">{h['symbol']}</td>
                    <td class="value">{h['quantity']:,}</td>
                    <td class="value">${h['price']:,.2f}</td>
                    <td class="value">${h['value']:,.0f}</td>
                    <td class="value {pnl_class}">${h['pnl']:+,.0f}</td>
                </tr>
"""
    
    html += """
            </tbody>
        </table>
        
        <footer>
            <p>Data from IBKR Flex Query | <a href="https://ifihadinvested.substack.com" target="_blank">Read my Substack</a></p>
            <p style="margin-top: 10px;">Disclaimer: Educational content. Not financial advice.</p>
        </footer>
    </div>
</body>
</html>
"""
    
    with open('index.html', 'w') as f:
        f.write(html)
    
    print(f"✅ Dashboard generated! {len(holdings)} positions, ${total_value:,.0f} total value")

if __name__ == "__main__":
    holdings = parse_portfolio()
    generate_html(holdings)
