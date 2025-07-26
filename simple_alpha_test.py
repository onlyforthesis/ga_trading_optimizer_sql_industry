#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡化的α參數測試
"""

try:
    from ga_optimizer import GeneticAlgorithm, TradingParameters
    import pandas as pd
    import numpy as np
    
    print("🧪 測試α參數的行為")
    print("=" * 50)
    
    # 創建一些模擬數據
    dates = pd.date_range('2020-01-01', periods=100, freq='D')
    prices = 100 + np.cumsum(np.random.randn(100) * 0.5)
    data = pd.DataFrame({
        'Date': dates,
        'Close': prices
    })
    
    # 創建GA實例
    ga = GeneticAlgorithm(data, population_size=10, generations=5)
    
    print(f"α參數範圍: {ga.param_ranges['alpha']}")
    
    # 測試不同的α值
    test_alphas = [0.5, 1.0, 2.5, 5.0]
    
    for alpha in test_alphas:
        print(f"\n測試α = {alpha}")
        
        # 計算實際的閾值
        alpha_threshold = alpha / 100.0
        print(f"  實際閾值: {alpha_threshold:.4f} ({alpha_threshold*100:.2f}%)")
        
        # 檢查α值是否在範圍內
        if ga.param_ranges['alpha'][0] <= alpha <= ga.param_ranges['alpha'][1]:
            print(f"  ✅ α值在合理範圍內")
        else:
            print(f"  ❌ α值超出範圍 {ga.param_ranges['alpha']}")
    
    print(f"\n✅ 測試完成！")
    
except Exception as e:
    print(f"❌ 測試失敗: {e}")
    import traceback
    traceback.print_exc()
