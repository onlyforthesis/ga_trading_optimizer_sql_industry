# Debug trading signal generation
from ga_optimizer import GeneticAlgorithm, TradingParameters
import pandas as pd
import numpy as np

print("Debugging trading signal generation")
print("=" * 50)

# Create data with more obvious trends
np.random.seed(42)
dates = pd.date_range('2019-01-01', periods=100, freq='D')
prices = []
base_price = 100

# Create data with clear up and down movements
for i in range(100):
    if i < 30:
        # Upward trend
        change = np.random.normal(0.02, 0.01)  # 2% daily up trend
    elif i < 60:
        # Downward trend  
        change = np.random.normal(-0.02, 0.01)  # 2% daily down trend
    else:
        # Sideways
        change = np.random.normal(0.005, 0.02)  # Small trend with volatility
    
    base_price *= (1 + change)
    prices.append(base_price)

data = pd.DataFrame({
    'Date': dates,
    'Close': prices
})

print(f"Price range: ${min(prices):.2f} - ${max(prices):.2f}")

# Test parameters
params = TradingParameters(
    m_intervals=10,  # Shorter MA for quicker signals
    hold_days=5,
    target_profit_ratio=0.05,
    alpha=1.0  # Lower threshold for easier signals
)

print(f"\nTesting parameters:")
print(f"  m_intervals: {params.m_intervals}")
print(f"  alpha: {params.alpha}% (threshold: {params.alpha/100:.3f})")

# Manual calculation to debug
window = params.m_intervals
alpha_threshold = params.alpha / 100.0

# Calculate MA
ma_values = pd.Series(prices).rolling(window=window).mean()

print(f"\nSignal generation analysis:")
print(f"  MA window: {window}")
print(f"  Alpha threshold: {alpha_threshold:.3f}")

# Check a few data points
for i in range(window, min(window+10, len(prices))):
    price = prices[i]
    ma = ma_values.iloc[i]
    if pd.notna(ma):
        buy_threshold = ma * (1 + alpha_threshold)
        sell_threshold = ma * (1 - alpha_threshold)
        
        buy_signal = price > buy_threshold
        sell_signal = price < sell_threshold
        
        print(f"  Day {i}: Price=${price:.2f}, MA=${ma:.2f}")
        print(f"         Buy threshold=${buy_threshold:.2f}, Sell threshold=${sell_threshold:.2f}")
        print(f"         Buy signal={buy_signal}, Sell signal={sell_signal}")

# Now test with GA
ga = GeneticAlgorithm(data, population_size=5, generations=1)
result = ga.evaluate_fitness(params)

print(f"\nGA result:")
print(f"  Fitness: {result.fitness:.2f}")
print(f"  Total profit: ${result.total_profit:.2f}")

print(f"\nDebugging completed!")
