#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 買進持有策略報酬測試腳本
"""

import sys
import os

# 添加當前目錄到路徑
sys.path.append(os.getcwd())

def test_buy_hold_return():
    """測試買進持有策略報酬計算"""
    print("🧪 測試買進持有策略報酬計算")
    print("=" * 50)
    
    try:
        # 測試資料庫連接
        from db_connector import DatabaseConnector
        db_obj = DatabaseConnector()
        
        if not db_obj.connection:
            print("❌ 資料庫連接失敗")
            return
        
        print("✅ 資料庫連接成功")
        
        # 測試買進持有報酬計算函數
        from full_gui import calculate_buy_and_hold_return
        
        # 獲取一些股票進行測試
        industries = db_obj.get_industry_list()
        test_stocks = []
        
        for industry in industries[:2]:  # 測試前2個產業
            stocks = db_obj.get_stocks_by_industry(industry)
            if stocks:
                test_stocks.extend(stocks[:2])  # 每個產業取2檔股票
        
        print(f"\n🔍 測試 {len(test_stocks)} 檔股票的買進持有報酬:")
        print("-" * 80)
        print(f"{'股票名稱':<20} {'買進持有報酬':<15} {'狀態':<10}")
        print("-" * 80)
        
        success_count = 0
        for stock_name in test_stocks[:10]:  # 限制測試數量
            try:
                buy_hold_return = calculate_buy_and_hold_return(db_obj, stock_name)
                status = "✅ 成功" if buy_hold_return != "N/A" else "⚠️  無數據"
                if buy_hold_return != "N/A":
                    success_count += 1
                
                print(f"{stock_name:<20} {buy_hold_return:<15} {status:<10}")
                
            except Exception as e:
                print(f"{stock_name:<20} {'錯誤':<15} {'❌ 失敗':<10}")
                print(f"   錯誤詳情: {e}")
        
        print("-" * 80)
        print(f"📊 測試摘要: 成功 {success_count}/{len(test_stocks[:10])} 檔股票")
        
        # 測試結果查詢函數
        print("\n📋 測試結果查詢功能:")
        from full_gui import get_analysis_results
        
        results = get_analysis_results(db_obj, "全部")
        print(f"   • 查詢到 {len(results)} 筆分析結果")
        
        if results:
            print("   • 前3筆結果預覽:")
            for i, result in enumerate(results[:3]):
                stock_name = result[0]
                buy_hold_return = result[1]
                total_profit = result[2]
                print(f"     {i+1}. {stock_name}: 買進持有={buy_hold_return}, 策略報酬={total_profit}")
        
        print("\n🎉 買進持有策略報酬測試完成!")
        
    except ImportError as e:
        print(f"❌ 匯入錯誤: {e}")
    except Exception as e:
        print(f"❌ 測試錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_buy_hold_return()
