# Real database diagnostic tool
import pandas as pd
import numpy as np

print("🔬 真實數據庫診斷工具")
print("=" * 50)

try:
    from db_connector import DBConnector
    print("✅ 成功導入 DBConnector")
    
    # 嘗試連接數據庫
    try:
        db = DBConnector()
        print("✅ 數據庫連接成功")
        
        # 獲取股票列表
        try:
            tables = db.get_all_stock_tables()
            print(f"✅ 找到 {len(tables)} 個股票表格")
            
            if len(tables) > 0:
                # 選擇第一個表格進行測試
                test_table = tables[0]
                print(f"🧪 測試表格: {test_table}")
                
                # 讀取數據
                try:
                    data = db.read_stock_data(test_table)
                    print(f"✅ 成功讀取數據: {len(data)} 筆")
                    print(f"✅ 數據欄位: {list(data.columns)}")
                    
                    if not data.empty:
                        # 檢查Close欄位
                        if 'Close' in data.columns:
                            close_data = data['Close']
                            
                            # 檢查數據類型
                            print(f"✅ Close欄位數據類型: {close_data.dtype}")
                            
                            # 嘗試轉換為數值並檢查
                            try:
                                close_numeric = pd.to_numeric(close_data, errors='coerce')
                                valid_prices = close_numeric.dropna()
                                if len(valid_prices) > 0:
                                    print(f"✅ Close欄位範圍: {valid_prices.min():.2f} - {valid_prices.max():.2f}")
                                    
                                    # 計算價格變化率並檢查合理性
                                    if len(valid_prices) > 1:
                                        price_changes = valid_prices.pct_change().dropna()
                                        if len(price_changes) > 0:
                                            print(f"   平均日變化: {price_changes.mean():.2%}")
                                            print(f"   標準差: {price_changes.std():.2%}")
                                            print(f"   最大漲幅: {price_changes.max():.2%}")
                                            print(f"   最大跌幅: {price_changes.min():.2%}")
                                            
                                            # 檢查價格變化的合理性 (-100% 到 +100%)
                                            reasonable_changes = price_changes[(price_changes >= -1.0) & (price_changes <= 1.0)]
                                            extreme_changes = price_changes[(price_changes < -1.0) | (price_changes > 1.0)]
                                            
                                            reasonable_pct = len(reasonable_changes) / len(price_changes) * 100
                                            print(f"   合理變化比例: {reasonable_pct:.1f}% ({len(reasonable_changes)}/{len(price_changes)})")
                                            
                                            if len(extreme_changes) > 0:
                                                print(f"   ⚠️ 極端變化: {len(extreme_changes)} 筆")
                                                print(f"      極端範圍: {extreme_changes.min():.2%} - {extreme_changes.max():.2%}")
                                                
                                                # 數據質量評估
                                                if reasonable_pct >= 99:
                                                    print(f"   ✅ 數據質量: 優秀")
                                                elif reasonable_pct >= 95:
                                                    print(f"   ⚠️ 數據質量: 良好，但有少量極端值")
                                                else:
                                                    print(f"   ❌ 數據質量: 有問題，極端值過多")
                                            else:
                                                print(f"   ✅ 無極端變化，數據質量優秀")
                                    
                                    # 檢查NaN值
                                    nan_count = close_numeric.isna().sum()
                                    if nan_count > 0:
                                        print(f"⚠️ Close欄位有 {nan_count} 個NaN值或無效值")
                                    else:
                                        print(f"✅ Close欄位無NaN值")
                                else:
                                    print(f"❌ Close欄位全部為無效數值")
                            except Exception as e:
                                print(f"❌ Close欄位數值轉換失敗: {e}")
                                print(f"   前5個值: {list(close_data.head())}")
                        else:
                            print(f"❌ 未找到Close欄位")
                            print(f"   可用欄位: {list(data.columns)}")
                        
                        # 測試GA
                        try:
                            from ga_optimizer import GeneticAlgorithm, TradingParameters
                            
                            # 創建合理的測試參數
                            test_params = TradingParameters(
                                m_intervals=20,
                                hold_days=5,
                                target_profit_ratio=0.05,
                                alpha=2.0
                            )
                            
                            print(f"\n🧪 測試GA評估:")
                            print(f"   參數: intervals={test_params.m_intervals}, days={test_params.hold_days}")
                            print(f"         profit={test_params.target_profit_ratio:.1%}, alpha={test_params.alpha}%")
                            
                            ga = GeneticAlgorithm(data, population_size=5, generations=1)
                            result = ga.evaluate_fitness(test_params)
                            
                            print(f"   結果: fitness={result.fitness:.4f}")
                            print(f"         profit=${result.total_profit:.2f}")
                            print(f"         win_rate={result.win_rate:.1%}")
                            print(f"         drawdown={result.max_drawdown:.1%}")
                            
                            if result.fitness == -10:
                                print(f"   ❌ 發現-10.0000問題!")
                                print(f"   可能原因:")
                                print(f"   - 數據格式問題")
                                print(f"   - 價格欄位無效")
                                print(f"   - 系統異常")
                            elif result.fitness < -5:
                                print(f"   ⚠️ 適應度過低，可能有問題")
                            else:
                                print(f"   ✅ GA評估正常運行")
                                
                        except Exception as e:
                            print(f"❌ GA測試失敗: {e}")
                            import traceback
                            traceback.print_exc()
                    else:
                        print(f"❌ 數據為空")
                        
                except Exception as e:
                    print(f"❌ 讀取數據失敗: {e}")
            else:
                print(f"❌ 沒有找到股票表格")
                
        except Exception as e:
            print(f"❌ 獲取股票列表失敗: {e}")
            
    except Exception as e:
        print(f"❌ 數據庫連接失敗: {e}")
        print(f"請檢查:")
        print(f"1. 數據庫服務是否運行")
        print(f"2. 連接參數是否正確")
        print(f"3. db_connector.py是否存在且正確")
        
except ImportError as e:
    print(f"❌ 無法導入 DBConnector: {e}")
    print(f"請檢查 db_connector.py 是否存在")

print(f"\n🏁 真實數據庫診斷完成")

# 額外的系統資訊
print(f"\n📋 系統資訊:")
import sys
print(f"Python版本: {sys.version}")

try:
    import pandas as pd
    print(f"Pandas版本: {pd.__version__}")
except:
    print(f"❌ Pandas未安裝")

try:
    import numpy as np
    print(f"Numpy版本: {np.__version__}")
except:
    print(f"❌ Numpy未安裝")
