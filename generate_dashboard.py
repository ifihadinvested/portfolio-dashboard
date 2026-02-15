import pandas as pd
import os
from datetime import datetime

def generate_dashboard_html():
    """Generate enhanced portfolio dashboard with stocks, options, and performance"""

    print("="*60)
    print("  PORTFOLIO DASHBOARD GENERATOR v2.0")
    print("="*60)
    print()

    # Read data files
    stocks_df = pd.read_csv('portfolio_data.csv')

    # Try to read optional files
    try:
        options_df = pd.read_csv('options_data.csv')
        has_options = True
    except:
        options_df = pd.DataFrame()
        has_options = False

    try:
        performance_df = pd.read_csv('performance_data.csv')
        has_performance = True
    except:
        performance_df = pd.DataFrame()
        has_performance = False

    try:
        annual_df = pd.read_csv('annual_returns.csv')
        has_annual = True
    except:
        annual_df = pd.DataFrame()
        has_annual = False

    print(f"✅ Loaded {len(stocks_df)} stocks")
    if has_options:
        print(f"✅ Loaded {len(options_df)} options")
    if has_performance:
        print(f"✅ Loaded {len(performance_df)} months of performance data")
    if has_annual:
        print(f"✅ Loaded {len(annual_df)} years of annual returns")
    print()

    # Calculate summary stats
    total_value = stocks_df['Market Value'].sum()
    total_pl = stocks_df['Unrealized P&L'].sum()
    total_cost = total_value - total_pl
    total_return_pct = (total_pl / total_cost * 100) if total_cost > 0 else 0
    num_positions = len(stocks_df)

    # Options stats
    if has_options:
        options_premium = abs(options_df['Cost Basis'].sum())
        options_value = abs(options_df['Market Value'].sum())
        options_pl = options_df['Unrealized P&L'].sum()
        num_options = len(options_df)

    # Performance stats
    if has_performance and not performance_df.empty:
        inception_return = performance_df['Portfolio_Cumulative'].iloc[-1]
        sp500_return = performance_df['SP500_Cumulative'].iloc[-1]
        outperformance = inception_return - sp500_return
        inception_date = pd.to_datetime(performance_df['Date'].iloc[0]).strftime('%B %Y')

    # Generate HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Portfolio Dashboard - Denis Lecchi</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            color: #333;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}

        .header {{
            background: white;
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}

        .header h1 {{
            font-size: 2em;
            margin-bottom: 5px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .header .subtitle {{
            color: #666;
            font-size: 0.9em;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}

        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}

        .stat-card .label {{
            font-size: 0.85em;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
        }}

        .stat-card .value {{
            font-size: 1.8em;
            font-weight: bold;
            color: #333;
        }}

        .stat-card .value.positive {{
            color: #10b981;
        }}

        .stat-card .value.negative {{
            color: #ef4444;
        }}

        .section {{
            background: white;
            padding: 25px;
            border-radius: 12px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}

        .section h2 {{
            font-size: 1.5em;
            margin-bottom: 20px;
            color: #333;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
        }}

        th {{
            background: #f9fafb;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            color: #666;
            font-size: 0.85em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border-bottom: 2px solid #e5e7eb;
        }}

        td {{
            padding: 12px;
            border-bottom: 1px solid #f3f4f6;
        }}

        tr:hover {{
            background: #f9fafb;
        }}

        .symbol {{
            font-weight: bold;
            color: #667eea;
            font-size: 1.1em;
        }}

        .positive {{
            color: #10b981;
        }}

        .negative {{
            color: #ef4444;
        }}

        .chart-container {{
            width: 100%;
            height: 400px;
            margin: 20px 0;
        }}

        @media (max-width: 768px) {{
            .stats-grid {{
                grid-template-columns: 1fr;
            }}

            table {{
                font-size: 0.9em;
            }}

            th, td {{
                padding: 8px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Portfolio Dashboard</h1>
            <p class="subtitle">Last updated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
        </div>
"""

    # Performance Since Inception Section
    if has_performance and not performance_df.empty:
        html += f"""
        <div class="stats-grid">
            <div class="stat-card">
                <div class="label">Since Inception</div>
                <div class="value positive">+{inception_return:.2f}%</div>
                <div class="subtitle" style="margin-top: 5px; font-size: 0.85em; color: #666;">Started {inception_date}</div>
            </div>
            <div class="stat-card">
                <div class="label">S&P 500</div>
                <div class="value">+{sp500_return:.2f}%</div>
            </div>
            <div class="stat-card">
                <div class="label">Outperformance</div>
                <div class="value positive">+{outperformance:.2f}%</div>
            </div>
        </div>
"""

    # Current Portfolio Stats
    html += f"""
        <div class="stats-grid">
            <div class="stat-card">
                <div class="label">Total Value</div>
                <div class="value">${total_value:,.2f}</div>
            </div>
            <div class="stat-card">
                <div class="label">Unrealized P&L</div>
                <div class="value {'positive' if total_pl >= 0 else 'negative'}">${total_pl:+,.2f}</div>
            </div>
            <div class="stat-card">
                <div class="label">Total Return</div>
                <div class="value {'positive' if total_return_pct >= 0 else 'negative'}">+{total_return_pct:.2f}%</div>
            </div>
            <div class="stat-card">
                <div class="label">Positions</div>
                <div class="value">{num_positions}</div>
            </div>
        </div>
"""

    # Performance Chart
    if has_performance and not performance_df.empty:
        # Prepare chart data
        dates = performance_df['Date'].tolist()
        portfolio_cumulative = performance_df['Portfolio_Cumulative'].tolist()
        sp500_cumulative = performance_df['SP500_Cumulative'].tolist()

        html += f"""
        <div class="section">
            <h2>📈 Performance vs S&P 500 (Since Inception)</h2>
            <div id="performanceChart" class="chart-container"></div>
        </div>

        <script>
            var dates = {dates};
            var portfolioReturns = {portfolio_cumulative};
            var sp500Returns = {sp500_cumulative};

            var trace1 = {{
                x: dates,
                y: portfolioReturns,
                type: 'scatter',
                mode: 'lines',
                name: 'Your Portfolio',
                line: {{color: '#667eea', width: 3}}
            }};

            var trace2 = {{
                x: dates,
                y: sp500Returns,
                type: 'scatter',
                mode: 'lines',
                name: 'S&P 500',
                line: {{color: '#10b981', width: 2, dash: 'dot'}}
            }};

            var layout = {{
                xaxis: {{title: 'Date'}},
                yaxis: {{title: 'Cumulative Return (%)', tickformat: '.1f'}},
                hovermode: 'x unified',
                margin: {{t: 20, b: 40, l: 60, r: 20}},
                legend: {{x: 0.02, y: 0.98}}
            }};

            Plotly.newPlot('performanceChart', [trace1, trace2], layout, {{responsive: true}});
        </script>
"""

    # Annual Returns Table
    if has_annual and not annual_df.empty:
        html += """
        <div class="section">
            <h2>📅 Annual Returns</h2>
            <table>
                <thead>
                    <tr>
                        <th>Year</th>
                        <th>Your Return</th>
                        <th>S&P 500</th>
                        <th>Outperformance</th>
                    </tr>
                </thead>
                <tbody>
"""

        for _, row in annual_df.sort_values('Year', ascending=False).iterrows():
            year = int(row['Year'])
            port_ret = row['Portfolio_Return']
            sp_ret = row['SP500_Return']
            outperf = port_ret - sp_ret

            html += f"""
                    <tr>
                        <td><strong>{year}</strong></td>
                        <td class="{'positive' if port_ret >= 0 else 'negative'}">{port_ret:+.2f}%</td>
                        <td class="{'positive' if sp_ret >= 0 else 'negative'}">{sp_ret:+.2f}%</td>
                        <td class="{'positive' if outperf >= 0 else 'negative'}">{outperf:+.2f}%</td>
                    </tr>
"""

        html += """
                </tbody>
            </table>
        </div>
"""

    # Stock Holdings Table
    html += """
        <div class="section">
            <h2>📋 Stock Holdings</h2>
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

    for _, row in stocks_df.sort_values('Market Value', ascending=False).iterrows():
        return_pct = (row['Unrealized P&L'] / (row['Market Value'] - row['Unrealized P&L']) * 100) if (row['Market Value'] - row['Unrealized P&L']) > 0 else 0

        html += f"""
                    <tr>
                        <td class="symbol">{row['Symbol']}</td>
                        <td>{row['Quantity']:.0f}</td>
                        <td>${row['Cost Basis']:,.2f}</td>
                        <td>${row['Market Value']:,.2f}</td>
                        <td class="{'positive' if row['Unrealized P&L'] >= 0 else 'negative'}">${row['Unrealized P&L']:+,.2f}</td>
                        <td class="{'positive' if return_pct >= 0 else 'negative'}">{return_pct:+.2f}%</td>
                    </tr>
"""

    html += """
                </tbody>
            </table>
        </div>
"""

    # Options Section
    if has_options and not options_df.empty:
        html += f"""
        <div class="section">
            <h2>💰 Options Portfolio</h2>
            <div class="stats-grid" style="margin-bottom: 20px;">
                <div class="stat-card">
                    <div class="label">Total Contracts</div>
                    <div class="value">{num_options}</div>
                </div>
                <div class="stat-card">
                    <div class="label">Premium Collected</div>
                    <div class="value">${options_premium:,.2f}</div>
                </div>
                <div class="stat-card">
                    <div class="label">Current Value</div>
                    <div class="value">${options_value:,.2f}</div>
                </div>
                <div class="stat-card">
                    <div class="label">Unrealized P&L</div>
                    <div class="value {'positive' if options_pl >= 0 else 'negative'}">${options_pl:+,.2f}</div>
                </div>
            </div>

            <table>
                <thead>
                    <tr>
                        <th>Underlying</th>
                        <th>Strategy</th>
                        <th>Strike</th>
                        <th>Expiry</th>
                        <th>Contracts</th>
                        <th>Premium</th>
                        <th>Current Value</th>
                        <th>P&L</th>
                    </tr>
                </thead>
                <tbody>
"""

        for _, row in options_df.sort_values('Unrealized P&L', ascending=False).iterrows():
            contracts = abs(int(row['Quantity']))

            html += f"""
                    <tr>
                        <td class="symbol">{row['Underlying']}</td>
                        <td>{row['Strategy']}</td>
                        <td>{row['Strike']}</td>
                        <td>{row['Expiry']}</td>
                        <td>{contracts}</td>
                        <td>${abs(row['Cost Basis']):,.2f}</td>
                        <td>${abs(row['Market Value']):,.2f}</td>
                        <td class="{'positive' if row['Unrealized P&L'] >= 0 else 'negative'}">${row['Unrealized P&L']:+,.2f}</td>
                    </tr>
"""

        html += """
                </tbody>
            </table>
        </div>
"""

    # Footer
    html += """
    </div>
</body>
</html>
"""

    # Write HTML file
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)

    print("✅ Generated: index.html")
    print("\n" + "="*60)
    print("SUCCESS! Dashboard created.")
    print("="*60)
    print("\nOpen index.html in your browser to view the dashboard!")

if __name__ == "__main__":
    generate_dashboard_html()
