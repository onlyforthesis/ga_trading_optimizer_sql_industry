# Alpha parameter test
from ga_optimizer import GeneticAlgorithm, TradingParameters
import pandas as pd
import numpy as np

print("Testing alpha parameter behavior")
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

print(f"Alpha parameter range: {ga.param_ranges['alpha']}")

# Test different alpha values
test_alphas = [0.5, 1.0, 2.5, 5.0]

for alpha in test_alphas:
    print(f"\nTesting alpha = {alpha}")
    
    # Calculate actual threshold
    alpha_threshold = alpha / 100.0
    print(f"  Actual threshold: {alpha_threshold:.4f} ({alpha_threshold*100:.2f}%)")
    
    # Check if alpha value is in range
    if ga.param_ranges['alpha'][0] <= alpha <= ga.param_ranges['alpha'][1]:
        print(f"  OK: Alpha value is within range")
    else:
        print(f"  ERROR: Alpha value exceeds range {ga.param_ranges['alpha']}")

print(f"\nTest completed!")
