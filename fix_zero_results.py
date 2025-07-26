#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
零結果問題修復工具
提供更好的預設參數和策略改進
"""

import pandas as pd
import numpy as np

def create_better_default_params():
    """創建更好的預設參數"""
    print("🔧 創建更好的預設參數")
    print("=" * 40)
    
    try:
        from db_connector import DBConnector
        from ga_optimizer import GeneticAlgorithm, TradingParameters
        
        # 連接數據庫
        db = DBConnector()
        tables = db.get_all_stock_tables()
        test_table = tables[0]
        data = db.read_stock_data(test_table)
        
        print(f"📊 測試股票: {test_table}")
        
        # 創建GA實例
        ga = GeneticAlgorithm(data)
        
        # 測試多組改進的參數
        improved_params = [
            {
                "name": "保守但有效策略",
                "params": TradingParameters(
                    m_intervals=15,    # 中等移動平均
                    hold_days=3,       # 短期持有
                    target_profit_ratio=0.02,  # 2%目標利潤
                    alpha=0.8         # 0.8%門檻
                )
            },
            {
                "name": "平衡策略",
                "params": TradingParameters(
                    m_intervals=12,    # 較短移動平均
                    hold_days=2,       # 很短持有
                    target_profit_ratio=0.015, # 1.5%目標利潤
                    alpha=0.6         # 0.6%門檻
                )
            },
            {
                "name": "積極但謹慎策略",
                "params": TradingParameters(
                    m_intervals=8,     # 短移動平均
                    hold_days=2,       # 短期持有
                    target_profit_ratio=0.025, # 2.5%目標利潤
                    alpha=1.0         # 1.0%門檻
                )
            }
        ]
        
        best_params = None
        best_fitness = -float('inf')
        
        for i, test_case in enumerate(improved_params):
            print(f"\n🧪 測試 {i+1}: {test_case['name']}")
            params = test_case['params']
            
            print(f"   參數: intervals={params.m_intervals}, days={params.hold_days}")
            print(f"         profit={params.target_profit_ratio:.1%}, alpha={params.alpha:.1f}%")
            
            try:
                result = ga.evaluate_fitness(params)
                
                print(f"   結果: fitness={result.fitness:.4f}")
                print(f"         profit=${result.total_profit:.2f}")
                print(f"         win_rate={result.win_rate:.1%}")
                print(f"         drawdown={result.max_drawdown:.1%}")
                
                if result.fitness > best_fitness:
                    best_fitness = result.fitness
                    best_params = params
                    print(f"   ✅ 新的最佳參數！")
                
                # 評估結果
                if result.total_profit > 0 and result.win_rate > 0:
                    print(f"   ✅ 正面結果：有利潤且有勝率")
                elif result.total_profit == 0 and result.win_rate == 0:
                    print(f"   ❌ 零結果問題")
                else:
                    print(f"   ⚠️ 部分正面結果")
                    
            except Exception as e:
                print(f"   ❌ 評估失敗: {e}")
        
        if best_params:
            print(f"\n🏆 推薦的最佳參數:")
            print(f"   移動平均間隔: {best_params.m_intervals}")
            print(f"   持有天數: {best_params.hold_days}")
            print(f"   目標利潤比: {best_params.target_profit_ratio:.1%}")
            print(f"   α門檻: {best_params.alpha:.1f}%")
            print(f"   預期適應度: {best_fitness:.4f}")
            
            # 生成GUI預設值更新代碼
            print(f"\n💻 GUI預設值更新建議:")
            print(f"在 full_gui.py 中將預設值改為:")
            print(f"   m_intervals: {best_params.m_intervals}")
            print(f"   hold_days: {best_params.hold_days}")
            print(f"   target_profit_ratio: {best_params.target_profit_ratio}")
            print(f"   alpha: {best_params.alpha}")
        
        print(f"\n📋 避免零結果的要點:")
        print(f"1. ✅ α值不要太高（建議0.5-1.5%）")
        print(f"2. ✅ 目標利潤比要現實（建議1.5-3%）")
        print(f"3. ✅ 移動平均不要太長（建議8-20）")
        print(f"4. ✅ 持有天數要短（建議1-5天）")
        print(f"5. ✅ 優先選擇有波動的股票")
        
    except Exception as e:
        print(f"❌ 修復工具失敗: {e}")

if __name__ == "__main__":
    create_better_default_params()
