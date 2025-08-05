#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 修復驗證測試腳本
"""

import sys
import os

# 添加當前目錄到路徑
sys.path.append(os.getcwd())

def test_fixes():
    """測試修復是否成功"""
    print("🔧 驗證修復功能")
    print("=" * 50)
    
    try:
        # 1. 測試資料庫連接
        from db_connector import DBConnector
        db_obj = DBConnector()
        
        if not db_obj.conn:
            print("❌ 資料庫連接失敗")
            return
        
        print("✅ 資料庫連接成功")
        
        # 2. 測試 execute_query 方法
        print("\n🔍 測試 execute_query 方法:")
        try:
            # 測試簡單查詢
            query = "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE'"
            result = db_obj.execute_query(query)
            
            if result:
                print(f"   ✅ execute_query 方法正常，找到 {len(result)} 個表格")
            else:
                print("   ⚠️  execute_query 返回空結果")
        except Exception as e:
            print(f"   ❌ execute_query 方法錯誤: {e}")
        
        # 3. 測試 BestParameters 表創建
        print("\n📊 測試 BestParameters 表:")
        try:
            db_obj.create_best_params_table()
            print("   ✅ BestParameters 表創建/檢查成功")
            
            # 檢查表是否存在
            query = "SELECT COUNT(*) FROM BestParameters"
            result = db_obj.execute_query(query)
            
            if result:
                count = result[0][0]
                print(f"   📋 BestParameters 表中有 {count} 筆記錄")
            
        except Exception as e:
            print(f"   ❌ BestParameters 表錯誤: {e}")
        
        # 4. 測試結果查詢函數
        print("\n🔎 測試結果查詢函數:")
        try:
            from full_gui import get_analysis_results
            
            results = get_analysis_results(db_obj, "全部")
            print(f"   📊 查詢到 {len(results)} 筆分析結果")
            
            if results:
                print("   📋 結果表格欄位:")
                headers = ["股票名稱", "買進持有策略報酬", "總報酬率", "年化報酬率", "最大回撤", "夏普比率", "勝率", "所屬產業"]
                for i, header in enumerate(headers):
                    print(f"      {i+1}. {header}")
                
                print("   📈 第一筆結果預覽:")
                first_result = results[0]
                for i, value in enumerate(first_result):
                    print(f"      {headers[i]}: {value}")
            else:
                print("   ℹ️  目前沒有分析結果（這是正常的，需要先進行分析）")
        
        except Exception as e:
            print(f"   ❌ 結果查詢函數錯誤: {e}")
            import traceback
            traceback.print_exc()
        
        # 5. 測試買進持有報酬計算
        print("\n💰 測試買進持有報酬計算:")
        try:
            from full_gui import calculate_buy_and_hold_return
            
            # 獲取一個股票表進行測試
            tables = db_obj.get_all_stock_tables()
            
            if tables:
                test_stock = tables[0]
                print(f"   📊 測試股票: {test_stock}")
                
                buy_hold_return = calculate_buy_and_hold_return(db_obj, test_stock)
                print(f"   💹 買進持有報酬: {buy_hold_return}")
                
                if buy_hold_return != "N/A":
                    print("   ✅ 買進持有報酬計算成功")
                else:
                    print("   ⚠️  買進持有報酬為 N/A（可能是數據問題或日期範圍問題）")
            else:
                print("   ❌ 沒有找到股票表")
        
        except Exception as e:
            print(f"   ❌ 買進持有報酬計算錯誤: {e}")
        
        print("\n🎉 修復驗證測試完成!")
        print("✅ 如果上述測試大部分通過，則修復成功")
        print("🌐 GUI 應該已在 http://127.0.0.1:7860 正常運行")
        
    except ImportError as e:
        print(f"❌ 匯入錯誤: {e}")
    except Exception as e:
        print(f"❌ 測試錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_fixes()
