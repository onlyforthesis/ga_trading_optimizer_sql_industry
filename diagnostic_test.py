# Diagnostic test for fitness evaluation issues
from ga_optimizer import GeneticAlgorithm, TradingParameters
import pandas as pd
import numpy as np

print("Diagnostic test for fitness evaluation")
print("=" * 50)

# Create more realistic sample data
np.random.seed(42)  # For reproducible results
dates = pd.date_range('2019-01-01', periods=500, freq='D')
initial_price = 100
prices = [initial_price]

# Generate more realistic price movements
for i in range(1, 500):
    # Random walk with slight upward trend
    change = np.random.normal(0.001, 0.02)  # 0.1% daily trend, 2% volatility
    new_price = prices[-1] * (1 + change)
    prices.append(max(new_price, 1))  # Ensure price doesn't go negative

data = pd.DataFrame({
    'Date': dates,
    'Close': prices
})

print(f"Created data: {len(data)} rows")
print(f"Price range: ${min(prices):.2f} - ${max(prices):.2f}")
print(f"Data columns: {list(data.columns)}")

# Test with reasonable parameters
test_params = TradingParameters(
    m_intervals=20,
    hold_days=5,
    target_profit_ratio=0.05,  # 5%
    alpha=2.0  # 2%
)

print(f"\nTesting with parameters:")
print(f"  m_intervals: {test_params.m_intervals}")
print(f"  hold_days: {test_params.hold_days}")
print(f"  target_profit_ratio: {test_params.target_profit_ratio:.1%}")
print(f"  alpha: {test_params.alpha}%")

# Create GA and test
ga = GeneticAlgorithm(data, population_size=5, generations=1)

print(f"\nData after GA initialization:")
print(f"  Train data: {len(ga.train_data)} rows")
print(f"  Test data: {len(ga.test_data)} rows")

try:
    result = ga.evaluate_fitness(test_params)
    print(f"\n🎯 FITNESS EVALUATION RESULT:")
    print(f"  Fitness: {result.fitness:.4f}")
    print(f"  Total profit: ${result.total_profit:.2f}")
    print(f"  Win rate: {result.win_rate:.1%}")
    print(f"  Max drawdown: {result.max_drawdown:.1%}")
    
    if result.fitness == -10:
        print(f"  ❌ PROBLEM: Fitness is -10, indicating error condition")
    elif result.fitness < 0:
        print(f"  ⚠️ WARNING: Negative fitness, may indicate poor performance")
    else:
        print(f"  ✅ SUCCESS: Positive fitness indicates working evaluation")
        
except Exception as e:
    print(f"❌ EXCEPTION during fitness evaluation: {e}")
    import traceback
    traceback.print_exc()

print(f"\nDiagnostic test completed!")
