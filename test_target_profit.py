# Test target profit ratio behavior
from ga_optimizer import GeneticAlgorithm, TradingParameters
import pandas as pd
import numpy as np

print("Testing target_profit_ratio parameter")
print("=" * 50)

# Create sample data
dates = pd.date_range('2020-01-01', periods=100, freq='D')
prices = 100 + np.cumsum(np.random.randn(100) * 0.5)
data = pd.DataFrame({
    'Date': dates,
    'Close': prices
})

# Create GA instance
ga = GeneticAlgorithm(data, population_size=10, generations=5)

print(f"Target profit ratio range: {ga.param_ranges['target_profit_ratio']}")

# Test different target profit ratios (including high values for unlimited range)
test_ratios = [0.02, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0]

for ratio in test_ratios:
    print(f"\nTesting target_profit_ratio = {ratio}")
    print(f"  Percentage: {ratio*100:.1f}%")
    
    # Example calculation
    entry_price = 100.0
    target_price = entry_price * (1 + ratio)
    profit_needed = target_price - entry_price
    
    print(f"  If entry price = ${entry_price:.2f}")
    print(f"  Target price = ${target_price:.2f}")
    print(f"  Profit needed = ${profit_needed:.2f}")
    
    # Check reasonableness
    if ratio < 0.02:
        print(f"  Note: Below minimum range")
    elif ratio < 0.05:
        print(f"  Note: Small profit target - may exit positions quickly")
    elif ratio < 0.2:
        print(f"  Note: Reasonable profit target")
    elif ratio < 0.5:
        print(f"  Note: High profit target - positions may hold longer")
    else:
        print(f"  Note: Very high profit target - positions may rarely reach target")

# Test random individual generation
print(f"\nTesting random individual generation:")
for i in range(5):
    individual = ga.create_random_individual()
    print(f"Individual {i+1}: target_profit_ratio = {individual.target_profit_ratio:.4f} ({individual.target_profit_ratio*100:.2f}%)")

print(f"\nTarget profit ratio test completed!")
