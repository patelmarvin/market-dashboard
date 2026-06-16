# Market Data & Visualization Dashboard

A Python-based financial analytics dashboard built with live market data.

## Projects

### 1. Sector Rotation Dashboard
Tracks all 10 S&P 500 sector ETFs (XLF, XLE, XLV, etc.) and calculates 1-week, 1-month, and 3-month returns using live price data. Visualized as an annotated heatmap and ranked horizontal bar chart.

### 2. Earnings Surprise Tracker
Pulls real EPS estimate vs. reported data for 10 major equities (GOOGL, AMZN, NVDA, JPM, etc.) and ranks them by surprise %. Visualized as a side-by-side grouped bar chart and surprise % ranking.

## Tech Stack
- Python 3.14
- yfinance — live market data
- pandas / NumPy — data manipulation
- matplotlib / seaborn — visualization

## How to Run
```bash
pip install yfinance pandas numpy matplotlib seaborn requests lxml
jupyter notebook market_dashboard.ipynb
```

## Author
Marvin Patel — Finance, Rutgers Business School  
[LinkedIn](https://www.linkedin.com/in/patelmarvin/)
