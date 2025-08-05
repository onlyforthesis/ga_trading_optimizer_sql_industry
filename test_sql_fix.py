#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 SQL語法修復測試腳本
"""

import sys
import os

# 添加當前目錄到路徑
sys.path.append(os.getcwd())

def test_sql_syntax_fix():
    """測試SQL語法修復"""
    print("🔧 測試SQL語法修復")
    print("=" * 50)
    
    try:
        # 1. 測試資料庫連接
        from db_connector import DBConnector
        db_obj = DBConnector()
        
        if not db_obj.conn:
            print("❌ 資料庫連接失敗")
            return
        
        print("✅ 資料庫連接成功")
        
        # 2. 獲取股票表進行測試
        tables = db_obj.get_all_stock_tables()
        
        if not tables:
            print("❌ 沒有找到股票表")
            return
        
        test_stock = tables[0]
        print(f"📊 測試股票表: {test_stock}")
        
        # 3. 檢查表格結構  
        print("\n🔍 檢查表格結構:")
        try:
            schema_query = f"""
            SELECT COLUMN_NAME, DATA_TYPE 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = '{test_stock}'
            ORDER BY ORDINAL_POSITION
            """
            
            columns = db_obj.execute_query(schema_query)
            
            if columns:
                print("   📋 表格欄位:")
                close_found = False
                date_found = False
                
                for col in columns[:10]:  # 只顯示前10個欄位
                    col_name = col[0]
                    col_type = col[1]
                    print(f"      • {col_name} ({col_type})")
                    
                    if 'close' in col_name.lower() or '收盤' in col_name:
                        close_found = True
                        print(f"        ↳ 找到收盤價欄位: {col_name}")
                    
                    if 'date' in col_name.lower() or '日期' in col_name:
                        date_found = True
                        print(f"        ↳ 找到日期欄位: {col_name}")
                
                if close_found and date_found:
                    print("   ✅ 找到必要的價格和日期欄位")
                else:
                    print("   ⚠️  缺少必要的價格或日期欄位")
            
        except Exception as e:
            print(f"   ❌ 檢查表格結構錯誤: {e}")
        
        # 4. 測試修復後的買進持有報酬計算
        print("\n💰 測試買進持有報酬計算:")
        try:
            from full_gui import calculate_buy_and_hold_return
            
            print(f"   📈 計算 {test_stock} 的買進持有報酬...")
            buy_hold_return = calculate_buy_and_hold_return(db_obj, test_stock)
            
            print(f"   💹 結果: {buy_hold_return}")
            
            if buy_hold_return != "N/A":
                print("   ✅ 買進持有報酬計算成功！")
                try:
                    # 嘗試解析百分比
                    if '%' in buy_hold_return:
                        percentage = float(buy_hold_return.replace('%', ''))
                        print(f"   📊 報酬率數值: {percentage:.2f}%")
                        
                        if -100 <= percentage <= 1000:  # 合理的報酬率範圍
                            print("   ✅ 報酬率數值在合理範圍內")
                        else:
                            print("   ⚠️  報酬率數值可能異常")
                except:
                    pass
            else:
                print("   ⚠️  買進持有報酬為 N/A")
                print("   💡 可能原因:")
                print("      - 表格中沒有2024年的數據")
                print("      - 欄位名稱不匹配")
                print("      - 數據格式問題")
        
        except Exception as e:
            print(f"   ❌ 買進持有報酬計算錯誤: {e}")
            import traceback
            traceback.print_exc()
        
        # 5. 測試結果查詢功能
        print("\n📊 測試結果查詢功能:")
        try:
            from full_gui import get_analysis_results
            
            results = get_analysis_results(db_obj, "全部")
            print(f"   📋 查詢到 {len(results)} 筆分析結果")
            
            if results:
                print("   ✅ 結果查詢功能正常")
                
                # 檢查第一筆結果的買進持有報酬
                first_result = results[0]
                if len(first_result) >= 2:
                    stock_name = first_result[0]
                    buy_hold_return = first_result[1]
                    print(f"   📈 {stock_name} 的買進持有報酬: {buy_hold_return}")
            else:
                print("   ℹ️  目前沒有分析結果")
        
        except Exception as e:
            print(f"   ❌ 結果查詢功能錯誤: {e}")
        
        print("\n🎉 SQL語法修復測試完成！")
        print("\n📋 測試摘要:")
        print("✅ 如果買進持有報酬計算成功，說明SQL語法已修復")
        print("✅ 如果結果查詢正常，說明整體功能運作良好")
        print("🌐 GUI 應該已在 http://127.0.0.1:7860 正常運行")
        
    except ImportError as e:
        print(f"❌ 匯入錯誤: {e}")
    except Exception as e:
        print(f"❌ 測試錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_sql_syntax_fix()
