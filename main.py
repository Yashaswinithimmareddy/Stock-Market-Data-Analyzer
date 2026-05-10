import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime, timedelta

# Set up seaborn style for better visuals
sns.set_theme(style="darkgrid")
plt.rcParams['figure.figsize'] = (12, 6)

# Create required directories if they don't exist
DIRS = ['data', 'images', 'outputs']
for d in DIRS:
    os.makedirs(d, exist_ok=True)

def fetch_stock_data(ticker, start_date, end_date):
    """
    Fetches stock data from Yahoo Finance.
    If it fails, generates a fallback synthetic dataset for demonstration.
    """
    print(f"Fetching data for {ticker} from {start_date} to {end_date}...")
    try:
        df = yf.download(ticker, start=start_date, end=end_date)
        if df.empty:
            raise ValueError("No data returned from yfinance.")
        # Ensure we only have a single level column index if yf returns multi-level
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        df.reset_index(inplace=True)
        # Rename 'Date' if needed
        if 'Date' in df.columns:
            df.rename(columns={'Date': 'Date'}, inplace=True)
            
        print("Data fetched successfully from Yahoo Finance.")
        return df
    except Exception as e:
        print(f"Warning: Failed to fetch data from Yahoo Finance. Error: {e}")
        print("Generating realistic synthetic fallback data for demonstration purposes...")
        # Fallback to synthetic data
        dates = pd.date_range(start=start_date, end=end_date, freq='B')
        np.random.seed(42)
        price_changes = np.random.normal(loc=0.0005, scale=0.02, size=len(dates))
        prices = 150 * np.exp(np.cumsum(price_changes))
        
        df = pd.DataFrame({
            'Date': dates,
            'Open': prices * np.random.normal(1, 0.005, len(dates)),
            'High': prices * np.random.normal(1.01, 0.005, len(dates)),
            'Low': prices * np.random.normal(0.99, 0.005, len(dates)),
            'Close': prices,
            'Adj Close': prices,
            'Volume': np.random.randint(1000000, 50000000, len(dates))
        })
        return df

def clean_data(df):
    """
    Cleans the dataset by handling missing values.
    """
    print("Cleaning data...")
    # Drop rows where 'Close' price is missing
    df = df.dropna(subset=['Close'])
    # Fill other missing values with forward fill
    df = df.ffill()
    return df

def calculate_metrics(df):
    """
    Calculates Daily Returns, Moving Averages (50 & 200 days), and Volatility.
    """
    print("Calculating technical indicators...")
    # Daily Returns
    df['Daily_Return'] = df['Close'].pct_change()
    
    # Moving Averages
    df['MA_50'] = df['Close'].rolling(window=50).mean()
    df['MA_200'] = df['Close'].rolling(window=200).mean()
    
    # Volatility (Standard deviation of daily returns over 252 trading days)
    volatility = df['Daily_Return'].std() * np.sqrt(252)
    
    return df, volatility

def plot_stock_trend(df, ticker):
    """
    Plots the closing price trend along with moving averages.
    """
    print("Generating Trend Chart...")
    plt.figure()
    plt.plot(df['Date'], df['Close'], label='Close Price', color='blue', alpha=0.6)
    plt.plot(df['Date'], df['MA_50'], label='50-Day MA', color='orange', alpha=0.8)
    plt.plot(df['Date'], df['MA_200'], label='200-Day MA', color='red', alpha=0.8)
    plt.title(f"{ticker} Stock Price & Moving Averages")
    plt.xlabel('Date')
    plt.ylabel('Price (USD)')
    plt.legend()
    plt.tight_layout()
    plt.savefig(f'images/{ticker}_trend_chart.png')
    plt.close()

def plot_daily_returns(df, ticker):
    """
    Plots the distribution of daily returns.
    """
    print("Generating Daily Returns Chart...")
    plt.figure()
    sns.histplot(df['Daily_Return'].dropna(), bins=50, kde=True, color='purple')
    plt.title(f"{ticker} Daily Return Distribution")
    plt.xlabel('Daily Return')
    plt.ylabel('Frequency')
    plt.tight_layout()
    plt.savefig(f'images/{ticker}_daily_returns.png')
    plt.close()

def generate_report(df, ticker, volatility):
    """
    Generates a textual summary report of the stock analysis.
    """
    print("Generating summary report...")
    start_date = df['Date'].iloc[0].strftime('%Y-%m-%d')
    end_date = df['Date'].iloc[-1].strftime('%Y-%m-%d')
    max_price = df['Close'].max()
    min_price = df['Close'].min()
    current_price = df['Close'].iloc[-1]
    
    # Trend Analysis
    if df['MA_50'].iloc[-1] > df['MA_200'].iloc[-1]:
        trend = "Bullish (50-Day MA > 200-Day MA)"
    else:
        trend = "Bearish (50-Day MA < 200-Day MA)"
        
    report = f"""
===================================================
        STOCK MARKET DATA ANALYSIS REPORT
===================================================
Ticker Symbol : {ticker}
Date Range    : {start_date} to {end_date}

--- PRICE SUMMARY ---
Highest Price : ${max_price:.2f}
Lowest Price  : ${min_price:.2f}
Closing Price : ${current_price:.2f}

--- RISK & PERFORMANCE ---
Annualized Volatility : {volatility * 100:.2f}%
Current Market Trend  : {trend}

--- INSIGHTS ---
1. Volatility indicates the risk associated with this stock. 
   A value around {volatility * 100:.2f}% suggests its historical price fluctuation.
2. The current trend is {trend}, which analysts use to gauge momentum.

Disclaimer: This report is generated for educational purposes 
as a Python course project and is NOT financial advice.
===================================================
"""
    with open(f'outputs/{ticker}_analysis_report.txt', 'w') as f:
        f.write(report)
    print("Report saved successfully.")

def main():
    ticker = "AAPL" # Apple Inc.
    end_date = datetime.today()
    start_date = end_date - timedelta(days=365 * 2) # Last 2 years
    
    # 1. Fetch Data
    df = fetch_stock_data(ticker, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
    
    # 2. Clean Data
    df = clean_data(df)
    
    # 3. Calculate Metrics
    df, volatility = calculate_metrics(df)
    
    # 4. Save Processed Data
    df.to_csv(f'data/{ticker}_historical_data.csv', index=False)
    print(f"Dataset saved to data/{ticker}_historical_data.csv")
    
    # 5. Visualizations
    plot_stock_trend(df, ticker)
    plot_daily_returns(df, ticker)
    
    # 6. Report Generation
    generate_report(df, ticker, volatility)
    
    print("\n--- ANALYSIS COMPLETE ---")
    print("Check the 'data', 'images', and 'outputs' folders for your results.")

if __name__ == "__main__":
    main()
