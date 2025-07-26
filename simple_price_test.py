#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np

def test_price_data():
    """簡單的價格數據測試"""
    print("🔍 價格數據測試")
    print("="*40)
    
    # 創建測試數據
    np.random.seed(42)
    n_days = 100
    initial_price = 100.0
    
    # 生成正常的價格變化 (日報酬率約-5%到+5%)
    daily_returns = np.random.normal(0, 0.02, n_days)  # 均值0, 標準差2%
    
    # 添加一些極端值來測試
    daily_returns[10] = -1.5  # -150% (不合理)
    daily_returns[20] = 2.0   # +200% (不合理)
    daily_returns[30] = -0.8  # -80% (極端但可能)
    daily_returns[40] = 0.5   # +50% (極端但可能)
    
    # 計算累積價格
    prices = [initial_price]
    for ret in daily_returns:
        new_price = prices[-1] * (1 + ret)
        prices.append(max(new_price, 0.01))  # 防止負價格
    
    prices = np.array(prices[1:])  # 移除初始價格
    
    print(f"✅ 生成了 {len(prices)} 天的價格數據")
    print(f"   價格範圍: ${prices.min():.2f} - ${prices.max():.2f}")
    
    # 計算實際的價格變化率
    actual_returns = pd.Series(prices).pct_change().dropna()
    
    print(f"   實際變化數: {len(actual_returns)}")
    print(f"   平均日變化: {actual_returns.mean():.2%}")
    print(f"   標準差: {actual_returns.std():.2%}")
    print(f"   最大漲幅: {actual_returns.max():.2%}")
    print(f"   最大跌幅: {actual_returns.min():.2%}")
    
    # 檢查合理性 (-100% 到 +100%)
    reasonable_changes = actual_returns[(actual_returns >= -1.0) & (actual_returns <= 1.0)]
    extreme_changes = actual_returns[(actual_returns < -1.0) | (actual_returns > 1.0)]
    
    reasonable_pct = len(reasonable_changes) / len(actual_returns) * 100
    
    print(f"   合理變化: {len(reasonable_changes)} 筆 ({reasonable_pct:.1f}%)")
    
    if len(extreme_changes) > 0:
        print(f"   ⚠️ 極端變化: {len(extreme_changes)} 筆")
        print(f"      極端範圍: {extreme_changes.min():.2%} - {extreme_changes.max():.2%}")
        print(f"      極端值: {[f'{x:.1%}' for x in extreme_changes.head(5)]}")
        
        # 數據質量評估
        if reasonable_pct >= 99:
            print(f"   ✅ 數據質量: 優秀")
        elif reasonable_pct >= 95:
            print(f"   ⚠️ 數據質量: 良好，但有少量極端值")
        else:
            print(f"   ❌ 數據質量: 有問題，極端值過多")
    else:
        print(f"   ✅ 無極端變化，數據質量優秀")
    
    # 檢查大幅變化 (>10%)
    large_changes = actual_returns[abs(actual_returns) > 0.1]
    if len(large_changes) > 0:
        large_pct = len(large_changes) / len(actual_returns) * 100
        print(f"   大幅變化(>10%): {len(large_changes)} 筆 ({large_pct:.1f}%)")
    
    print(f"\n📋 合理範圍說明:")
    print(f"✅ 正常日報酬率: -10% 至 +10%")
    print(f"⚠️ 極端但可能: -100% 至 +100%")
    print(f"❌ 不合理變化: <-100% 或 >+100%")

if __name__ == "__main__":
    test_price_data()
