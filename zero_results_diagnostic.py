#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
零結果問題診斷工具
專門用於診斷總利潤$0.00、勝率0.0%、最大回撤10.0%的問題
"""

import pandas as pd
import numpy as np

def diagnose_zero_results():
    """診斷導致零結果的可能原因"""
    print("🔍 零結果問題診斷")
    print("=" * 50)
    
    try:
        from db_connector import DBConnector
        from ga_optimizer import GeneticAlgorithm, TradingParameters
        
        print("✅ 成功導入必要模組")
        
        # 連接數據庫並取得一個股票表格
        db = DBConnector()
        tables = db.get_all_stock_tables()
        test_table = tables[0] if tables else None
        
        if not test_table:
            print("❌ 沒有找到股票表格")
            return
        
        print(f"📊 測試股票: {test_table}")
        
        # 讀取數據
        data = db.read_stock_data(test_table)
        print(f"✅ 讀取數據: {len(data)} 筆")
        
        # 檢查數據結構
        print(f"📋 數據欄位: {list(data.columns)}")
        
        # 處理BOM字符
        data.columns = data.columns.str.replace('\ufeff', '', regex=False)
        
        # 檢查Close欄位
        if 'Close' in data.columns:
            close_data = pd.to_numeric(data['Close'], errors='coerce')
            valid_count = close_data.count()
            print(f"✅ Close欄位有效數據: {valid_count} 筆")
            print(f"   價格範圍: ${close_data.min():.2f} - ${close_data.max():.2f}")
        else:
            print("❌ 沒有找到Close欄位")
            return
        
        # 測試不同的參數組合
        test_cases = [
            {
                "name": "預設參數",
                "params": TradingParameters(
                    m_intervals=20,
                    hold_days=5,
                    target_profit_ratio=0.05,
                    alpha=2.0
                )
            },
            {
                "name": "低門檻參數",
                "params": TradingParameters(
                    m_intervals=10,
                    hold_days=3,
                    target_profit_ratio=0.02,
                    alpha=1.0
                )
            },
            {
                "name": "極低門檻參數",
                "params": TradingParameters(
                    m_intervals=5,
                    hold_days=1,
                    target_profit_ratio=0.01,
                    alpha=0.5
                )
            }
        ]
        
        ga = GeneticAlgorithm(data)  # 傳入數據參數
        
        for i, test_case in enumerate(test_cases):
            print(f"\n🧪 測試案例 {i+1}: {test_case['name']}")
            params = test_case['params']
            
            print(f"   參數: intervals={params.m_intervals}, days={params.hold_days}")
            print(f"         profit={params.target_profit_ratio:.1%}, alpha={params.alpha:.1f}%")
            
            try:
                # 評估參數
                result = ga.evaluate_fitness(params)
                
                print(f"   結果: fitness={result.fitness:.4f}")
                print(f"         profit=${result.total_profit:.2f}")
                print(f"         win_rate={result.win_rate:.1%}")
                print(f"         drawdown={result.max_drawdown:.1%}")
                
                # 診斷結果
                if result.total_profit == 0 and result.win_rate == 0:
                    print(f"   ❌ 零結果問題！原因分析:")
                    
                    # 詳細分析
                    try:
                        # 手動執行策略邏輯來找出問題
                        close_prices = pd.to_numeric(data['Close'], errors='coerce').dropna()
                        
                        if len(close_prices) < params.m_intervals:
                            print(f"      - 數據不足: 需要{params.m_intervals}筆，只有{len(close_prices)}筆")
                        
                        # 計算移動平均
                        ma = close_prices.rolling(window=params.m_intervals).mean()
                        valid_ma = ma.dropna()
                        
                        if len(valid_ma) == 0:
                            print(f"      - 無法計算移動平均")
                        else:
                            print(f"      - 移動平均計算成功: {len(valid_ma)} 筆")
                        
                        # 檢查買入信號
                        buy_signals = 0
                        sell_signals = 0
                        
                        for j in range(len(close_prices) - 1):
                            if j < params.m_intervals:
                                continue
                                
                            current_price = close_prices.iloc[j]
                            ma_value = ma.iloc[j]
                            
                            if pd.isna(ma_value):
                                continue
                            
                            # 計算價格變化率
                            price_change = (current_price - ma_value) / ma_value
                            
                            # 檢查買入條件
                            if price_change > params.alpha / 100:
                                buy_signals += 1
                            elif price_change < -params.alpha / 100:
                                sell_signals += 1
                        
                        print(f"      - 買入信號: {buy_signals} 個")
                        print(f"      - 賣出信號: {sell_signals} 個")
                        
                        if buy_signals == 0:
                            print(f"      - ❌ 主要問題: 沒有買入信號")
                            print(f"        可能原因: α值({params.alpha:.1%})過高")
                            print(f"        建議: 降低α值到 0.5% - 2.0%")
                        
                    except Exception as detail_error:
                        print(f"      - 詳細分析失敗: {detail_error}")
                        
                elif result.fitness < -5:
                    print(f"   ⚠️ 系統錯誤 (fitness < -5)")
                elif result.fitness < 0:
                    print(f"   ⚠️ 策略表現差但正常運作")
                else:
                    print(f"   ✅ 正常運作")
                    
            except Exception as e:
                print(f"   ❌ 評估失敗: {e}")
        
        # 提供解決方案
        print(f"\n💡 零結果問題解決方案:")
        print(f"1. ✅ 降低α門檻值 (建議: 0.5% - 2.0%)")
        print(f"2. ✅ 降低目標利潤比 (建議: 1% - 3%)")
        print(f"3. ✅ 減少移動平均間隔 (建議: 5 - 15)")
        print(f"4. ✅ 減少持有天數 (建議: 1 - 5)")
        print(f"5. ✅ 確認數據有足夠的波動性")
        
    except ImportError as e:
        print(f"❌ 導入模組失敗: {e}")
    except Exception as e:
        print(f"❌ 診斷失敗: {e}")

if __name__ == "__main__":
    diagnose_zero_results()
