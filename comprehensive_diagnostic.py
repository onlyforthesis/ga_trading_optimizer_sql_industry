# Comprehensive diagnostic tool for GA trading optimizer
from ga_optimizer import GeneticAlgorithm, TradingParameters
import pandas as pd
import numpy as np

def check_data_quality(data):
    """檢查數據質量"""
    print("🔍 數據質量檢查")
    print("=" * 30)
    
    if data.empty:
        print("❌ 數據為空!")
        return False
    
    print(f"✅ 數據行數: {len(data)}")
    print(f"✅ 數據欄位: {list(data.columns)}")
    
    # 檢查是否有價格欄位
    price_columns = ['Close', 'close', '收盤價', 'CLOSE', 'Close Price']
    found_price_col = None
    for col in price_columns:
        if col in data.columns:
            found_price_col = col
            break
    
    if found_price_col:
        print(f"✅ 找到價格欄位: {found_price_col}")
        
        # 檢查價格數據
        prices = data[found_price_col]
        print(f"✅ 價格範圍: ${prices.min():.2f} - ${prices.max():.2f}")
        print(f"✅ 價格均值: ${prices.mean():.2f}")
        
        # 檢查價格變化率是否在合理範圍內
        if len(prices) > 1:
            price_changes = prices.pct_change().dropna()
            if len(price_changes) > 0:
                max_change = price_changes.max()
                min_change = price_changes.min()
                print(f"✅ 價格變化範圍: {min_change:.1%} - {max_change:.1%}")
                
                # 檢查是否有異常的價格變化（超過合理範圍 -100% 到 +100%）
                extreme_changes = price_changes[(price_changes < -1.0) | (price_changes > 1.0)]
                if len(extreme_changes) > 0:
                    print(f"⚠️ 警告: 有 {len(extreme_changes)} 個極端價格變化 (超過±100%)")
                    print(f"   極端變化範圍: {extreme_changes.min():.1%} - {extreme_changes.max():.1%}")
                else:
                    print(f"✅ 價格變化在合理範圍內 (-100% 至 +100%)")
        
        # 檢查NaN值
        nan_count = prices.isna().sum()
        if nan_count > 0:
            print(f"⚠️ 警告: 有 {nan_count} 個NaN價格值")
        else:
            print(f"✅ 無NaN價格值")
            
        # 檢查零值或負值
        invalid_prices = (prices <= 0).sum()
        if invalid_prices > 0:
            print(f"⚠️ 警告: 有 {invalid_prices} 個零值或負值價格")
        else:
            print(f"✅ 無零值或負值價格")
            
    else:
        print("❌ 未找到價格欄位!")
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            print(f"⚠️ 可用數值欄位: {list(numeric_cols)}")
        return False
    
    # 檢查日期欄位
    date_columns = ['Date', 'date', '日期', 'DATE', 'DateTime', 'Time']
    found_date_col = None
    for col in date_columns:
        if col in data.columns:
            found_date_col = col
            break
    
    if found_date_col:
        print(f"✅ 找到日期欄位: {found_date_col}")
        try:
            dates = pd.to_datetime(data[found_date_col])
            print(f"✅ 日期範圍: {dates.min()} 到 {dates.max()}")
        except:
            print(f"⚠️ 警告: 日期格式可能有問題")
    else:
        print("⚠️ 警告: 未找到日期欄位")
    
    return True

def test_parameter_ranges():
    """測試參數範圍"""
    print("\n🔧 參數範圍測試")
    print("=" * 30)
    
    # 創建簡單測試數據
    test_data = pd.DataFrame({
        'Date': pd.date_range('2019-01-01', periods=100),
        'Close': 100 + np.cumsum(np.random.randn(100) * 0.01)
    })
    
    ga = GeneticAlgorithm(test_data, population_size=5, generations=1)
    print(f"✅ GA參數範圍:")
    for param, range_val in ga.param_ranges.items():
        print(f"   {param}: {range_val}")
    
    # 測試隨機個體生成
    print(f"\n🎲 隨機個體生成測試:")
    for i in range(3):
        individual = ga.create_random_individual()
        print(f"   個體{i+1}: m_intervals={individual.m_intervals}, hold_days={individual.hold_days}")
        print(f"          target_profit_ratio={individual.target_profit_ratio:.4f}, alpha={individual.alpha:.2f}")
        
        # 檢查參數是否合理
        issues = []
        if individual.m_intervals <= 0:
            issues.append("m_intervals <= 0")
        if individual.hold_days <= 0:
            issues.append("hold_days <= 0")
        if individual.target_profit_ratio <= 0:
            issues.append("target_profit_ratio <= 0")
        if individual.alpha <= 0:
            issues.append("alpha <= 0")
            
        if issues:
            print(f"   ❌ 問題: {', '.join(issues)}")
        else:
            print(f"   ✅ 參數正常")

def test_fitness_evaluation_with_real_scenario():
    """使用真實場景測試適應度評估"""
    print("\n📊 適應度評估測試")
    print("=" * 30)
    
    # 創建更真實的股票數據
    np.random.seed(123)
    dates = pd.date_range('2019-01-01', periods=500, freq='D')
    
    # 模擬真實股票價格走勢
    initial_price = 50.0
    prices = [initial_price]
    
    for i in range(1, 500):
        # 加入一些真實性：週末效應、趨勢、波動
        daily_return = np.random.normal(0.0002, 0.02)  # 年化約5%報酬，年化20%波動
        
        # 偶爾加入較大波動（模擬市場事件）
        if np.random.random() < 0.05:  # 5%機率
            daily_return += np.random.normal(0, 0.05)
            
        new_price = prices[-1] * (1 + daily_return)
        prices.append(max(new_price, 1))  # 確保價格不會變負數
    
    data = pd.DataFrame({
        'Date': dates,
        'Close': prices
    })
    
    print(f"📈 模擬股票數據:")
    print(f"   價格範圍: ${min(prices):.2f} - ${max(prices):.2f}")
    print(f"   總報酬: {(prices[-1]/prices[0]-1)*100:.1f}%")
    
    # 測試不同參數組合
    test_cases = [
        {
            'name': '保守策略',
            'params': TradingParameters(20, 5, 0.03, 1.0)
        },
        {
            'name': '積極策略', 
            'params': TradingParameters(10, 3, 0.08, 0.5)
        },
        {
            'name': '極端保守',
            'params': TradingParameters(50, 20, 0.02, 0.5)
        },
        {
            'name': '可能問題參數',
            'params': TradingParameters(5, 1, 2.0, 50.0)
        }
    ]
    
    ga = GeneticAlgorithm(data, population_size=5, generations=1)
    
    for case in test_cases:
        print(f"\n🧪 測試: {case['name']}")
        params = case['params']
        print(f"   參數: intervals={params.m_intervals}, days={params.hold_days}")
        print(f"         profit={params.target_profit_ratio:.1%}, alpha={params.alpha}%")
        
        try:
            result = ga.evaluate_fitness(params)
            print(f"   結果: fitness={result.fitness:.2f}")
            print(f"         profit=${result.total_profit:.2f}, win_rate={result.win_rate:.1%}")
            print(f"         drawdown={result.max_drawdown:.1%}")
            
            # 分析結果
            if result.fitness == -10:
                print(f"   ❌ 嚴重錯誤: 系統評估失敗")
            elif result.fitness <= -8:
                print(f"   ❌ 參數錯誤: 參數不合理")
            elif result.fitness <= -3:
                print(f"   ⚠️ 無交易: 參數設置導致無法交易")
            elif result.fitness < 0:
                print(f"   ⚠️ 負面績效: 策略表現不佳")
            else:
                print(f"   ✅ 正常運作: 策略產生了交易")
                
        except Exception as e:
            print(f"   ❌ 異常: {str(e)}")
            import traceback
            traceback.print_exc()

def run_full_diagnostic():
    """運行完整診斷"""
    print("🔬 GA交易優化器完整診斷")
    print("=" * 50)
    
    # 1. 測試基本功能
    test_parameter_ranges()
    
    # 2. 測試適應度評估
    test_fitness_evaluation_with_real_scenario()
    
    print(f"\n✅ 診斷完成!")
    print(f"\n💡 如果您看到-10.0000適應度，請檢查:")
    print(f"   1. 數據是否有Close欄位且包含有效價格")
    print(f"   2. 數據是否有足夠的行數(建議>100)")
    print(f"   3. 參數是否都是正數")
    print(f"   4. α值是否過高導致無法產生交易信號")

if __name__ == "__main__":
    run_full_diagnostic()
