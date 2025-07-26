# Data quality checker for reasonable price change ranges
import pandas as pd
import numpy as np

def check_price_data_quality():
    """檢查真實股票數據的價格變化是否在合理範圍內"""
    print("🔍 股票數據質量檢查 - 合理變化範圍分析")
    print("=" * 60)
    
    try:
        from db_connector import DBConnector
        db = DBConnector()
        tables = db.get_all_stock_tables()
        
        print(f"✅ 找到 {len(tables)} 個股票表格")
        
        # 檢查前5個表格
        sample_tables = tables[:5]
        
        for i, table in enumerate(sample_tables):
            print(f"\n📊 檢查表格 {i+1}/5: {table}")
            try:
                data = db.read_stock_data(table)
                
                if data.empty:
                    print(f"❌ 數據為空")
                    continue
                
                # 處理BOM字符
                data.columns = data.columns.str.replace('\ufeff', '', regex=False)
                
                if 'Close' not in data.columns:
                    print(f"❌ 未找到Close欄位")
                    continue
                
                # 轉換為數值型
                close_prices = pd.to_numeric(data['Close'], errors='coerce')
                valid_prices = close_prices.dropna()
                
                if len(valid_prices) < 2:
                    print(f"❌ 有效價格數據不足")
                    continue
                
                print(f"   數據筆數: {len(valid_prices)}")
                print(f"   價格範圍: ${valid_prices.min():.2f} - ${valid_prices.max():.2f}")
                
                # 計算價格變化率
                price_changes = valid_prices.pct_change().dropna()
                
                if len(price_changes) == 0:
                    print(f"❌ 無法計算價格變化")
                    continue
                
                # 統計價格變化
                print(f"   變化筆數: {len(price_changes)}")
                print(f"   變化範圍: {price_changes.min():.2%} - {price_changes.max():.2%}")
                print(f"   變化均值: {price_changes.mean():.2%}")
                print(f"   變化標準差: {price_changes.std():.2%}")
                
                # 檢查合理性 (-100% 到 +100%)
                reasonable_changes = price_changes[(price_changes >= -1.0) & (price_changes <= 1.0)]
                extreme_changes = price_changes[(price_changes < -1.0) | (price_changes > 1.0)]
                
                reasonable_pct = len(reasonable_changes) / len(price_changes) * 100
                
                print(f"   合理變化: {len(reasonable_changes)} 筆 ({reasonable_pct:.1f}%)")
                
                if len(extreme_changes) > 0:
                    print(f"   ⚠️ 極端變化: {len(extreme_changes)} 筆")
                    print(f"      極端範圍: {extreme_changes.min():.2%} - {extreme_changes.max():.2%}")
                    
                    # 顯示前幾個極端變化的詳細信息
                    if len(extreme_changes) <= 5:
                        print(f"      極端變化值: {[f'{x:.2%}' for x in extreme_changes]}")
                else:
                    print(f"   ✅ 無極端變化")
                
                # 檢查連續大幅變化
                large_changes = price_changes[abs(price_changes) > 0.1]  # 超過10%的變化
                if len(large_changes) > 0:
                    large_pct = len(large_changes) / len(price_changes) * 100
                    print(f"   大幅變化(>10%): {len(large_changes)} 筆 ({large_pct:.1f}%)")
                
                # 數據質量評估
                if reasonable_pct >= 99:
                    print(f"   ✅ 數據質量: 優秀")
                elif reasonable_pct >= 95:
                    print(f"   ✅ 數據質量: 良好")
                elif reasonable_pct >= 90:
                    print(f"   ⚠️ 數據質量: 尚可")
                else:
                    print(f"   ❌ 數據質量: 有問題")
                    
            except Exception as e:
                print(f"❌ 處理失敗: {e}")
        
        print(f"\n📋 總結:")
        print(f"✅ 合理的日報酬率範圍: -100% 至 +100%")
        print(f"⚠️ 如果有極端變化，可能原因:")
        print(f"   1. 股票分割或合併")
        print(f"   2. 除權除息")
        print(f"   3. 數據錯誤")
        print(f"   4. 市場異常事件")
        print(f"💡 建議:")
        print(f"   1. 極端變化<1%: 數據質量優秀")
        print(f"   2. 極端變化1-5%: 數據質量良好")
        print(f"   3. 極端變化>5%: 需要數據清理")
        
    except ImportError:
        print(f"❌ 無法導入DBConnector，請確認db_connector.py存在")
    except Exception as e:
        print(f"❌ 檢查失敗: {e}")

if __name__ == "__main__":
    check_price_data_quality()
