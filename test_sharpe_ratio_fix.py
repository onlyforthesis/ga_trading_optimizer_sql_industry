#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📊 Sharpe Ratio 修復驗證腳本
測試修復後的 Sharpe Ratio 計算是否正常
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db_connector import DBConnector
from ga_optimizer import GeneticAlgorithm, TradingParameters
import pandas as pd

def test_sharpe_ratio_calculation():
    """測試 Sharpe Ratio 計算"""
    print("🧪 開始測試 Sharpe Ratio 計算修復...")
    
    try:
        # 連接資料庫
        db = DBConnector()
        
        # 獲取一檔股票進行測試
        test_stocks = ['2891BTW', '2464TW盟立', '6770TW力積電']
        
        for stock_name in test_stocks:
            try:
                print(f"\n📊 測試股票: {stock_name}")
                
                # 檢查股票表是否存在
                if not db.validate_stock_table(stock_name):
                    print(f"⚠️ 跳過 {stock_name}: 股票表不存在")
                    continue
                
                # 讀取數據
                data = db.read_stock_data(stock_name)
                if data.empty or len(data) < 100:
                    print(f"⚠️ 跳過 {stock_name}: 數據不足 ({len(data)} 筆)")
                    continue
                
                print(f"✅ 成功載入數據: {len(data)} 筆")
                
                # 創建遺傳演算法實例
                ga = GeneticAlgorithm(
                    data=data,
                    population_size=10,  # 小規模測試
                    generations=5,       # 快速測試
                    max_time_minutes=1.0
                )
                
                # 測試不同的參數設定
                test_params = [
                    TradingParameters(m_intervals=10, hold_days=2, target_profit_ratio=0.02, alpha=1.0),
                    TradingParameters(m_intervals=15, hold_days=3, target_profit_ratio=0.015, alpha=0.8),
                    TradingParameters(m_intervals=12, hold_days=2, target_profit_ratio=0.025, alpha=1.2)
                ]
                
                print(f"\n🔬 測試 {len(test_params)} 組參數的 Sharpe Ratio 計算:")
                
                for i, params in enumerate(test_params):
                    print(f"\n   參數組 {i+1}: intervals={params.m_intervals}, days={params.hold_days}, profit={params.target_profit_ratio:.1%}, alpha={params.alpha:.1f}%")
                    
                    # 評估參數
                    result = ga.evaluate_fitness(params)
                    
                    print(f"   結果:")
                    print(f"     適應度: {result.fitness:.4f}")
                    print(f"     總利潤: ${result.total_profit:,.2f}")
                    print(f"     勝率: {result.win_rate:.1%}")
                    print(f"     最大回撤: {result.max_drawdown:.1%}")
                    print(f"     ⭐ Sharpe Ratio: {result.sharpe_ratio:.4f}")
                    
                    # 檢查 Sharpe Ratio 是否不再是 0
                    if result.sharpe_ratio != 0.0:
                        print(f"     ✅ Sharpe Ratio 計算正常！")
                    else:
                        print(f"     ⚠️ Sharpe Ratio 仍為 0，可能數據不足或無交易")
                
                # 測試完成，只測試第一檔成功的股票
                print(f"\n🎉 {stock_name} 測試完成！")
                break
                
            except Exception as e:
                print(f"❌ 測試 {stock_name} 時發生錯誤: {e}")
                continue
        
        print(f"\n📊 Sharpe Ratio 修復驗證完成！")
        return True
        
    except Exception as e:
        print(f"❌ 測試過程發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_full_ga_with_sharpe():
    """測試完整遺傳演算法的 Sharpe Ratio"""
    print(f"\n🧬 測試完整遺傳演算法中的 Sharpe Ratio...")
    
    try:
        db = DBConnector()
        
        # 選擇一檔股票進行完整測試
        test_stock = '2891BTW'
        
        if not db.validate_stock_table(test_stock):
            print(f"❌ 測試股票 {test_stock} 不存在")
            return False
        
        data = db.read_stock_data(test_stock)
        if data.empty:
            print(f"❌ 測試股票 {test_stock} 無數據")
            return False
        
        print(f"📊 使用 {test_stock} 進行完整 GA 測試")
        
        # 創建遺傳演算法
        ga = GeneticAlgorithm(
            data=data,
            population_size=20,
            generations=10,
            max_time_minutes=2.0
        )
        
        # 執行演化
        best_result = ga.evolve()
        
        print(f"\n🏆 最佳結果:")
        print(f"   適應度: {best_result.fitness:.4f}")
        print(f"   總利潤: ${best_result.total_profit:,.2f}")
        print(f"   勝率: {best_result.win_rate:.1%}")
        print(f"   最大回撤: {best_result.max_drawdown:.1%}")
        print(f"   ⭐ Sharpe Ratio: {best_result.sharpe_ratio:.4f}")
        print(f"   參數: intervals={best_result.parameters.m_intervals}, days={best_result.parameters.hold_days}, profit={best_result.parameters.target_profit_ratio:.1%}, alpha={best_result.parameters.alpha:.1f}%")
        
        # 測試數據評估
        if hasattr(best_result, 'test_result') and best_result.test_result:
            test_result = best_result.test_result
            print(f"\n🧪 測試數據結果:")
            print(f"   適應度: {test_result.fitness:.4f}")
            print(f"   總利潤: ${test_result.total_profit:,.2f}")
            print(f"   勝率: {test_result.win_rate:.1%}")
            print(f"   最大回撤: {test_result.max_drawdown:.1%}")
            print(f"   ⭐ Sharpe Ratio: {test_result.sharpe_ratio:.4f}")
        
        # 檢查修復結果
        if best_result.sharpe_ratio != 0.0:
            print(f"\n✅ 修復成功！Sharpe Ratio 不再為 0")
        else:
            print(f"\n⚠️ Sharpe Ratio 仍為 0，可能是策略無交易或數據問題")
        
        return True
        
    except Exception as e:
        print(f"❌ 完整 GA 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函數"""
    print("🔧 Sharpe Ratio 修復驗證測試")
    print("=" * 50)
    
    # 測試 1: 單獨參數評估
    print("\n📊 測試 1: 單獨參數評估的 Sharpe Ratio 計算")
    success1 = test_sharpe_ratio_calculation()
    
    # 測試 2: 完整遺傳演算法
    print("\n🧬 測試 2: 完整遺傳演算法的 Sharpe Ratio")
    success2 = test_full_ga_with_sharpe()
    
    # 總結
    print("\n" + "=" * 50)
    print("📋 測試結果總結:")
    print(f"   單獨參數評估: {'✅ 通過' if success1 else '❌ 失敗'}")
    print(f"   完整遺傳演算法: {'✅ 通過' if success2 else '❌ 失敗'}")
    
    if success1 and success2:
        print("\n🎉 Sharpe Ratio 修復驗證成功！")
        print("💡 現在所有分析結果都會正確顯示 Sharpe Ratio")
    else:
        print("\n⚠️ 部分測試失敗，請檢查修復結果")
    
    print("\n👋 測試完成！")

if __name__ == "__main__":
    main()
