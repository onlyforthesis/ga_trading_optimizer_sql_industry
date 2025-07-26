#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試α參數的行為和範圍
"""

from ga_optimizer import GeneticAlgorithm, TradingParameters
import pandas as pd
import numpy as np

def test_alpha_parameter():
    """測試α參數的行為"""
    print("🧪 測試α參數的行為")
    print("=" * 50)
    
    # 創建一些模擬數據
    dates = pd.date_range('2020-01-01', periods=100, freq='D')
    prices = 100 + np.cumsum(np.random.randn(100) * 0.5)  # 隨機遊走價格
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
        
        # 創建測試參數
        params = TradingParameters(
            m_intervals=20,
            hold_days=5,
            target_profit_ratio=0.05,
            alpha=alpha
        )
        
        # 計算實際的閾值
        alpha_threshold = params.alpha / 100.0
        print(f"  實際閾值: {alpha_threshold:.4f} ({alpha_threshold*100:.2f}%)")
        
        # 測試交易信號
        test_data = data.copy()
        test_data['MA'] = test_data['Close'].rolling(window=20).mean()
        
        buy_condition = test_data['Close'] > test_data['MA'] * (1 + alpha_threshold)
        sell_condition = test_data['Close'] < test_data['MA'] * (1 - alpha_threshold)
        
        buy_signals = buy_condition.sum()
        sell_signals = sell_condition.sum()
        
        print(f"  買入信號數量: {buy_signals}")
        print(f"  賣出信號數量: {sell_signals}")
        
        # 檢查α值是否在範圍內
        if ga.param_ranges['alpha'][0] <= alpha <= ga.param_ranges['alpha'][1]:
            print(f"  ✅ α值在合理範圍內")
        else:
            print(f"  ❌ α值超出範圍 {ga.param_ranges['alpha']}")

def test_alpha_validation():
    """測試α值的驗證機制"""
    print(f"\n🔍 測試α值驗證機制")
    print("=" * 50)
    
    # 創建測試數據
    data = pd.DataFrame({
        'Date': pd.date_range('2020-01-01', periods=50),
        'Close': np.random.randn(50) + 100
    })
    
    ga = GeneticAlgorithm(data, population_size=5, generations=3)
    
    # 測試隨機個體生成
    for i in range(5):
        individual = ga.create_random_individual()
        print(f"個體 {i+1}: α = {individual.alpha:.2f}")
        
        if individual.alpha > 5.0:
            print(f"  ❌ 警告：α值 {individual.alpha} 超過上限 5.0")
        elif individual.alpha < 0.5:
            print(f"  ❌ 警告：α值 {individual.alpha} 低於下限 0.5")
        else:
            print(f"  ✅ α值在合理範圍內")

if __name__ == "__main__":
    test_alpha_parameter()
    test_alpha_validation()
    print(f"\n✅ 測試完成！")
