import yfinance as yf

def get_stock_data(ticker="2330.TW", period="3y"):
    data = yf.download(ticker, period=period)
    data.reset_index(inplace=True)
    return data
