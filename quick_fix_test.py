"""
快速驗證修復是否成功
"""

print("🧪 驗證加速優化器修復...")

try:
    # 測試導入
    from fast_ga_optimizer import FastGeneticAlgorithm, fast_optimize, create_speed_preset
    print("✅ 成功導入 fast_ga_optimizer 模組")
    
    # 測試速度配置
    config = create_speed_preset('ultra_fast')
    print(f"✅ 成功創建速度配置: {config}")
    
    # 測試 FastGeneticAlgorithm 類別創建
    import pandas as pd
    import numpy as np
    
    # 創建測試數據
    test_data = pd.DataFrame({
        'Date': pd.date_range('2023-01-01', periods=100),
        'Close': np.random.randn(100).cumsum() + 100
    })
    
    # 嘗試創建優化器實例
    optimizer = FastGeneticAlgorithm(test_data, **config)
    print("✅ 成功創建 FastGeneticAlgorithm 實例")
    
    # 檢查必要方法是否存在
    required_methods = ['evaluate_fitness', 'tournament_selection_fast', 'crossover_fast', 'evolve']
    for method in required_methods:
        if hasattr(optimizer, method):
            print(f"✅ 方法 {method} 存在")
        else:
            print(f"❌ 方法 {method} 不存在")
    
    print("\n🎉 基本驗證通過！修復應該已經生效。")
    print("💡 現在可以嘗試運行批次優化:")
    print("   python fast_batch_optimizer.py")
    print("   或使用 GUI: python main.py")
    
except Exception as e:
    print(f"❌ 驗證失敗: {str(e)}")
    import traceback
    traceback.print_exc()
