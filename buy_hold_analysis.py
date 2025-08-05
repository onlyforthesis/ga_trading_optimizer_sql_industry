#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📊 買進持有策略深度分析模組
提供詳細的買進持有策略報酬分析功能
"""

import sys
import os
import pandas as pd
from datetime import datetime, timedelta

# 添加當前目錄到路徑
sys.path.append(os.getcwd())

class BuyAndHoldAnalyzer:
    """買進持有策略分析器"""
    
    def __init__(self, db_obj):
        self.db_obj = db_obj
    
    def get_stock_column_names(self, stock_name):
        """動態獲取股票表的欄位名稱"""
        try:
            # 查詢收盤價欄位
            close_query = f"""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = '{stock_name}'
            AND (COLUMN_NAME LIKE '%close%' OR COLUMN_NAME LIKE '%收盤%' OR COLUMN_NAME LIKE '%Close%')
            """
            
            close_columns = self.db_obj.execute_query(close_query)
            close_col = close_columns[0][0] if close_columns else 'Close'
            
            # 查詢日期欄位
            date_query = f"""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = '{stock_name}'
            AND (COLUMN_NAME LIKE '%date%' OR COLUMN_NAME LIKE '%日期%' OR COLUMN_NAME LIKE '%Date%')
            """
            
            date_columns = self.db_obj.execute_query(date_query)
            date_col = date_columns[0][0] if date_columns else 'Date'
            
            return close_col, date_col
            
        except Exception as e:
            print(f"獲取欄位名稱錯誤: {e}")
            return 'Close', 'Date'
    
    def calculate_buy_hold_return_detailed(self, stock_name, start_date, end_date):
        """計算指定期間的買進持有報酬（詳細版）"""
        try:
            close_col, date_col = self.get_stock_column_names(stock_name)
            
            # 獲取期間內的所有數據
            query = f"""
            SELECT [{date_col}], [{close_col}]
            FROM [{stock_name}]
            WHERE [{date_col}] >= '{start_date}' AND [{date_col}] <= '{end_date}'
            ORDER BY [{date_col}] ASC
            """
            
            results = self.db_obj.execute_query(query)
            
            if not results or len(results) < 2:
                return None
            
            # 第一天和最後一天的價格
            first_price = results[0][1]
            last_price = results[-1][1]
            first_date = results[0][0]
            last_date = results[-1][0]
            
            # 計算報酬率
            if first_price and last_price and first_price > 0:
                return_rate = (last_price - first_price) / first_price
                
                # 計算持有天數
                if isinstance(first_date, str):
                    first_date = datetime.strptime(first_date[:10], '%Y-%m-%d')
                if isinstance(last_date, str):
                    last_date = datetime.strptime(last_date[:10], '%Y-%m-%d')
                
                hold_days = (last_date - first_date).days
                
                # 計算年化報酬率
                annual_return = (1 + return_rate) ** (365 / hold_days) - 1 if hold_days > 0 else 0
                
                return {
                    'stock_name': stock_name,
                    'start_date': first_date.strftime('%Y-%m-%d'),
                    'end_date': last_date.strftime('%Y-%m-%d'),
                    'start_price': first_price,
                    'end_price': last_price,
                    'total_return': return_rate,
                    'annual_return': annual_return,
                    'hold_days': hold_days,
                    'data_points': len(results)
                }
            
            return None
            
        except Exception as e:
            print(f"計算詳細買進持有報酬錯誤 ({stock_name}): {e}")
            return None
    
    def analyze_multiple_periods(self, stock_name):
        """分析多個時間區間的買進持有報酬"""
        periods = [
            ('2024年全年', '2024-01-01', '2024-12-31'),
            ('2024年上半年', '2024-01-01', '2024-06-30'),
            ('2024年下半年', '2024-07-01', '2024-12-31'),
            ('2024年Q1', '2024-01-01', '2024-03-31'),
            ('2024年Q2', '2024-04-01', '2024-06-30'),
            ('2024年Q3', '2024-07-01', '2024-09-30'),
            ('2024年Q4', '2024-10-01', '2024-12-31'),
            ('近6個月', '2024-07-01', '2024-12-31'),
            ('近3個月', '2024-10-01', '2024-12-31')
        ]
        
        results = []
        
        for period_name, start_date, end_date in periods:
            result = self.calculate_buy_hold_return_detailed(stock_name, start_date, end_date)
            if result:
                result['period_name'] = period_name
                results.append(result)
        
        return results
    
    def get_stock_basic_info(self, stock_name):
        """獲取股票基本資料"""
        try:
            stock_code = self.db_obj.extract_stock_code_from_table_name(stock_name)
            info = self.db_obj.get_stock_info(stock_code)
            
            return {
                'stock_code': stock_code,
                'stock_name': info['StockName'] if info else stock_name,
                'industry': info['Industry'] if info else '未知'
            }
        except:
            return {
                'stock_code': 'Unknown',
                'stock_name': stock_name,
                'industry': '未知'
            }
    
    def generate_comprehensive_report(self, stock_name):
        """生成綜合分析報告"""
        try:
            # 獲取基本資料
            basic_info = self.get_stock_basic_info(stock_name)
            
            # 分析多個時間區間
            period_results = self.analyze_multiple_periods(stock_name)
            
            if not period_results:
                return f"❌ 無法獲取股票 {stock_name} 的價格數據"
            
            # 生成報告
            report = f"""
📊 **買進持有策略深度分析報告**
================================================

📈 **股票基本資料**
• 股票代號: {basic_info['stock_code']}
• 股票名稱: {basic_info['stock_name']}
• 所屬產業: {basic_info['industry']}

💰 **各時間區間買進持有報酬分析**
------------------------------------------------
"""
            
            # 按時間區間排序（全年優先）
            sorted_results = sorted(period_results, key=lambda x: x['hold_days'], reverse=True)
            
            for result in sorted_results:
                report += f"""
🗓️  **{result['period_name']}**
   • 期間: {result['start_date']} ~ {result['end_date']}
   • 起始價格: ${result['start_price']:.2f}
   • 結束價格: ${result['end_price']:.2f}
   • 總報酬率: {result['total_return']*100:.2f}%
   • 年化報酬率: {result['annual_return']*100:.2f}%
   • 持有天數: {result['hold_days']} 天
   • 數據點數: {result['data_points']} 筆
"""
            
            # 績效摘要
            best_period = max(sorted_results, key=lambda x: x['total_return'])
            worst_period = min(sorted_results, key=lambda x: x['total_return'])
            
            report += f"""
📊 **績效摘要**
------------------------------------------------
🏆 最佳表現期間: {best_period['period_name']} ({best_period['total_return']*100:.2f}%)
📉 最差表現期間: {worst_period['period_name']} ({worst_period['total_return']*100:.2f}%)

📈 **投資建議**
------------------------------------------------
• 如果選擇2024年全年買進持有：
"""
            
            yearly_result = next((r for r in sorted_results if '全年' in r['period_name']), None)
            if yearly_result:
                if yearly_result['total_return'] > 0:
                    report += f"  ✅ 獲利 {yearly_result['total_return']*100:.2f}% (年化 {yearly_result['annual_return']*100:.2f}%)\n"
                else:
                    report += f"  ❌ 虧損 {abs(yearly_result['total_return'])*100:.2f}% (年化 {abs(yearly_result['annual_return'])*100:.2f}%)\n"
            
            report += f"""
• 波動性分析: 不同季度表現差異為 {(best_period['total_return'] - worst_period['total_return'])*100:.2f}%
• 建議持有期間: 根據歷史數據，{best_period['period_name']} 表現最佳

⚠️  **風險提醒**
------------------------------------------------
• 過去績效不代表未來表現
• 買進持有策略適合長期投資
• 建議搭配基本面分析進行投資決策
• 考慮分散投資降低風險

📅 報告生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            
            return report
            
        except Exception as e:
            return f"❌ 生成分析報告錯誤: {str(e)}"

def analyze_buy_hold_strategy():
    """買進持有策略分析主函數"""
    print("📊 買進持有策略深度分析")
    print("=" * 60)
    
    try:
        # 連接資料庫
        from db_connector import DBConnector
        db_obj = DBConnector()
        
        if not db_obj.conn:
            print("❌ 資料庫連接失敗")
            return
        
        print("✅ 資料庫連接成功")
        
        # 創建分析器
        analyzer = BuyAndHoldAnalyzer(db_obj)
        
        # 獲取股票列表
        tables = db_obj.get_all_stock_tables()
        
        if not tables:
            print("❌ 沒有找到股票表")
            return
        
        print(f"📋 找到 {len(tables)} 檔股票")
        
        # 分析前幾檔股票作為示例
        print("\n🔍 開始分析買進持有策略...")
        
        for i, stock_name in enumerate(tables[:5]):  # 分析前5檔
            print(f"\n📈 分析第 {i+1} 檔股票: {stock_name}")
            print("-" * 40)
            
            report = analyzer.generate_comprehensive_report(stock_name)
            print(report)
            
            if i < 4:  # 不是最後一個
                input("\n按 Enter 繼續下一檔股票分析...")
        
        print("\n🎉 買進持有策略深度分析完成！")
        
    except ImportError as e:
        print(f"❌ 匯入錯誤: {e}")
    except Exception as e:
        print(f"❌ 分析錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_buy_hold_strategy()
