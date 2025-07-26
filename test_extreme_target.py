# Test extreme target profit ratios
from ga_optimizer import GeneticAlgorithm, TradingParameters
import pandas as pd
import numpy as np

print("Testing extreme target_profit_ratio values")
print("=" * 50)

# Create sample data
dates = pd.date_range('2020-01-01', periods=50, freq='D')
prices = 100 + np.cumsum(np.random.randn(50) * 0.5)
data = pd.DataFrame({
    'Date': dates,
    'Close': prices
})

# Test extreme target profit ratios
extreme_ratios = [5.0, 10.0, 50.0, 100.0]

for ratio in extreme_ratios:
    print(f"\nTesting extreme target_profit_ratio = {ratio} ({ratio*100:.0f}%)")
    
    # Create test parameters
    params = TradingParameters(
        m_intervals=10,
        hold_days=5,
        target_profit_ratio=ratio,
        alpha=5.0
    )
    
    # Create GA and test fitness evaluation
    ga = GeneticAlgorithm(data, population_size=5, generations=1)
    
    try:
        result = ga.evaluate_fitness(params)
        print(f"  Fitness evaluation: SUCCESS")
        print(f"  Fitness score: {result.fitness:.2f}")
        print(f"  Total trades: {result.total_profit:.0f}")
        print(f"  Win rate: {result.win_rate:.1%}")
    except Exception as e:
        print(f"  Fitness evaluation: FAILED - {e}")

print(f"\nExtreme values test completed!")
