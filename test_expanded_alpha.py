# Test expanded alpha parameter range
from ga_optimizer import GeneticAlgorithm, TradingParameters
import pandas as pd
import numpy as np

print("Testing expanded alpha parameter range (0.5% to 99%)")
print("=" * 60)

# Create sample data
dates = pd.date_range('2020-01-01', periods=100, freq='D')
prices = 100 + np.cumsum(np.random.randn(100) * 0.5)
data = pd.DataFrame({
    'Date': dates,
    'Close': prices
})

# Create GA instance
ga = GeneticAlgorithm(data, population_size=10, generations=5)

print(f"Alpha parameter range: {ga.param_ranges['alpha']}")

# Test different alpha values across the new range
test_alphas = [0.5, 10.0, 25.0, 50.0, 75.0, 99.0]

for alpha in test_alphas:
    print(f"\nTesting alpha = {alpha}")
    
    # Calculate actual threshold
    alpha_threshold = alpha / 100.0
    print(f"  Actual threshold: {alpha_threshold:.4f} ({alpha_threshold*100:.1f}%)")
    
    # Check if alpha value is in range
    if ga.param_ranges['alpha'][0] <= alpha <= ga.param_ranges['alpha'][1]:
        print(f"  OK: Alpha value is within range")
    else:
        print(f"  ERROR: Alpha value exceeds range {ga.param_ranges['alpha']}")
    
    # Test trading logic impact
    if alpha_threshold < 0.5:
        print(f"  Note: Very sensitive threshold - many signals expected")
    elif alpha_threshold > 0.5:
        print(f"  Note: Very loose threshold - few signals expected")

# Test random individual generation
print(f"\nTesting random individual generation:")
for i in range(5):
    individual = ga.create_random_individual()
    print(f"Individual {i+1}: alpha = {individual.alpha:.1f}% (threshold: {individual.alpha/100:.3f})")

print(f"\nExpanded range test completed!")
