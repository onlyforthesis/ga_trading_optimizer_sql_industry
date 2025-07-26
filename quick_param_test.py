#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
快速參數測試
"""

from ga_optimizer import TradingParameters

def test_parameters():
    print("🔧 參數創建測試")
    print("=" * 30)
    
    # 測試參數創建
    params1 = TradingParameters(
        m_intervals=20,
        hold_days=5,
        target_profit_ratio=0.05,  # 5%
        alpha=2.0  # 2%
    )
    
    print(f"參數1:")
    print(f"  intervals: {params1.m_intervals}")
    print(f"  days: {params1.hold_days}")
    print(f"  profit: {params1.target_profit_ratio:.1%}")
    print(f"  alpha: {params1.alpha:.1f}%")  # α已經是百分比值
    
    params2 = TradingParameters(
        m_intervals=10,
        hold_days=3,
        target_profit_ratio=0.02,  # 2%
        alpha=1.0  # 1%
    )
    
    print(f"\n參數2:")
    print(f"  intervals: {params2.m_intervals}")
    print(f"  days: {params2.hold_days}")
    print(f"  profit: {params2.target_profit_ratio:.1%}")
    print(f"  alpha: {params2.alpha:.1f}%")  # α已經是百分比值

if __name__ == "__main__":
    test_parameters()
