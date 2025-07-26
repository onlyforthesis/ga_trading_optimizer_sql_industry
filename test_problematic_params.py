# Test problematic parameter combinations
from ga_optimizer import GeneticAlgorithm, TradingParameters
import pandas as pd
import numpy as np

print("Testing problematic parameter combinations")
print("=" * 50)

# Create sample data
np.random.seed(42)
dates = pd.date_range('2019-01-01', periods=200, freq='D')
prices = 100 + np.cumsum(np.random.randn(200) * 0.01)
data = pd.DataFrame({
    'Date': dates,
    'Close': prices
})

# Test cases that might cause -10 fitness
test_cases = [
    {
        'name': '極高α值',
        'params': TradingParameters(20, 5, 0.05, 95.0)  # 95% threshold
    },
    {
        'name': '極高目標利潤',
        'params': TradingParameters(20, 5, 10.0, 5.0)  # 1000% profit target
    },
    {
        'name': '極小區間數',
        'params': TradingParameters(2, 5, 0.05, 5.0)  # Very small intervals
    },
    {
        'name': '正常參數',
        'params': TradingParameters(20, 5, 0.05, 2.0)  # Normal parameters
    }
]

ga = GeneticAlgorithm(data, population_size=5, generations=1)

for test_case in test_cases:
    print(f"\n🧪 測試: {test_case['name']}")
    params = test_case['params']
    print(f"   參數: m_intervals={params.m_intervals}, hold_days={params.hold_days}")
    print(f"         target_profit_ratio={params.target_profit_ratio:.1%}, alpha={params.alpha}%")
    
    try:
        result = ga.evaluate_fitness(params)
        print(f"   結果: fitness={result.fitness:.2f}, profit=${result.total_profit:.2f}")
        print(f"         win_rate={result.win_rate:.1%}, drawdown={result.max_drawdown:.1%}")
        
        if result.fitness <= -10:
            print(f"   ❌ 嚴重問題: fitness為-10，表示評估失敗")
        elif result.fitness < -5:
            print(f"   ⚠️ 問題: fitness為負且較低")
        elif result.fitness < 0:
            print(f"   ⚠️ 輕微問題: fitness為負")
        else:
            print(f"   ✅ 正常: fitness為正")
            
    except Exception as e:
        print(f"   ❌ 異常: {e}")

print(f"\nProblematic parameters test completed!")
