import pandas as pd
import xml.etree.ElementTree as ET
from datetime import datetime
import os

def parse_portfolio():
    """Parse portfolio data from CSV or XML"""
    
    # Try CSV first
    if os.path.exists('portfolio_data.csv'):
        print("✅ Using CSV file...")
        df = pd.read_csv('portfolio_data.csv')
        
        # Debug: print column names
        print(f"CSV columns: {df.columns.tolist()}")
        print(f"First row: {df.iloc[0].to_dict()}")
        
        # Parse holdings from CSV
        holdings = []
        for _, row in df.iterrows():
            try:
                holdings.append({
                    'symbol': str(row['Symbol']),
                    'quantity': float(row['Quantity']),
                    'costBasis': float(row['Cost Basis']),
                    'marketValue': float(row['Market Value']),
                    'unrealizedPL': float(row['Unrealized P&L']),
                    'currency': row.get('Currency', 'USD')
                })
            except Exception as e:
                print(f"Error parsing row: {e}")
                print(f"Row data: {row.to_dict()}")
        
        print(f"✅ Parsed {len(holdings)} holdings from CSV")
        return holdings
    
    # Otherwise try XML
    elif os.path.exists('portfolio_data.xml'):
        print("✅ Using XML file...")
        tree = ET.parse('portfolio_data.xml')
        root = tree.getroot()
        
        holdings = []
        for position in root.findall('.//OpenPosition'):
            holdings.append({
                'symbol': position.get('symbol'),
                'quantity': float(position.get('position', 0)),
                'costBasis': float(position.get('costBasisMoney', 0)),
                'marketValue': float(position.get('markValue', 0)),
                'unrealizedPL': float(position.get('fifoPnlUnrealized', 0)),
                'currency': position.get('currency', 'USD')
            })
        
        print(f"✅ Parsed {len(holdings)} holdings from XML")
        return holdings
    
    else:
        raise FileNotFoundError("No portfolio_data.csv or portfolio_data.xml found!")

def generate_dashboard(holdings):
    """Generate HTML dashboard"""
    
    # Calculate totals
    total_value = sum(h['marketValue'] for h in holdings)
    total_pl = sum(h['unrealizedPL'] for h in holdings)
    total_return_pct = (total_pl / (total_value - total_pl)) * 100 if total_value > total_pl else 0
    
    # Sort by market value
    holdings.sort(key=lambda x: x['marketValue'], reverse=True)
    
    # Generate HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Portfolio Dashboard</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        .header {{
            background: white;
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }}
        
        .header h1 {{
            color: #333;
            margin-bottom: 10px;
            font-size: 2.5em;
        }}
        
        .header .date {{
            color: #666;
            font-size: 0.9em;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        
        .stat-card {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }}
        
        .stat-card .label {{
            color: #666;
            font-size: 0.9em;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .stat-card .value {{
            color: #333;
            font-size: 2em;
            font-weight: bold;
        }}
        
        .stat-card.positive .value {{
            color: #10b981;
        }}
        
        .stat-card.negative .value {{
            color: #ef4444;
        }}
        
        .holdings {{
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }}
        
        .holdings h2 {{
            color: #333;
            margin-bottom: 20px;
            font-size: 1.8em;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        
        th {{
            background: #f8fafc;
            padding: 15px;
            text-align: left;
            color: #666;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.85em;
            letter-spacing: 0.5px;
        }}
        
        td {{
            padding: 15px;
            border-bottom: 1px solid #f1f5f9;
            color: #333;
        }}
        
        tr:hover {{
            background: #f8fafc;
        }}
        
        .symbol {{
            font-weight: bold;
            color: #667eea;
            font-size: 1.1em;
        }}
        
        .positive {{
            color: #10b981;
            font-weight: 600;
        }}
        
        .negative {{
            color: #ef4444;
            font-weight: 600;
        }}
        
        @media (max-width: 768px) {{
            table {{
                font-size: 0.9em;
            }}
            
            th, td {{
                padding: 10px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Portfolio Dashboard</h1>
            <div class="date">Last updated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</div>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="label">Total Value</div>
                <div class="value">${total_value:,.2f}</div>
            </div>
            
            <div class="stat-card {'positive' if total_pl >= 0 else 'negative'}">
                <div class="label">Unrealized P&L</div>
                <div class="value">${total_pl:+,.2f}</div>
            </div>
            
            <div class="stat-card {'positive' if total_return_pct >= 0 else 'negative'}">
                <div class="label">Total Return</div>
                <div class="value">{total_return_pct:+.2f}%</div>
            </div>
            
            <div class="stat-card">
                <div class="label">Positions</div>
                <div class="value">{len(holdings)}</div>
            </div>
        </div>
        
        <div class="holdings">
            <h2>Holdings</h2>
            <table>
                <thead>
                    <tr>
                        <th>Symbol</th>
                        <th>Quantity</th>
                        <th>Cost Basis</th>
                        <th>Market Value</th>
                        <th>Unrealized P&L</th>
                        <th>Return %</th>
                    </tr>
                </thead>
                <tbody>
"""
    
    for holding in holdings:
        return_pct = (holding['unrealizedPL'] / holding['costBasis'] * 100) if holding['costBasis'] != 0 else 0
        pl_class = 'positive' if holding['unrealizedPL'] >= 0 else 'negative'
        
        html += f"""
                    <tr>
                        <td class="symbol">{holding['symbol']}</td>
                        <td>{holding['quantity']:.2f}</td>
                        <td>${holding['costBasis']:,.2f}</td>
                        <td>${holding['marketValue']:,.2f}</td>
                        <td class="{pl_class}">${holding['unrealizedPL']:+,.2f}</td>
                        <td class="{pl_class}">{return_pct:+.2f}%</td>
                    </tr>
"""
    
    html += """
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
"""
    
    return html

if __name__ == "__main__":
    print("Starting dashboard generation...")
    holdings = parse_portfolio()
    html = generate_dashboard(holdings)
    
    with open('index.html', 'w') as f:
        f.write(html)
    
    print("✅ Dashboard generated successfully!")
    print(f"   - Total holdings: {len(holdings)}")
    print(f"   - Output: index.html")
