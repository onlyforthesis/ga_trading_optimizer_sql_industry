#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
檢查股票表結構
"""

try:
    from db_connector import DBConnector
    
    db = DBConnector()
    print("✅ 資料庫連接成功")
    
    # 獲取股票表
    tables = db.get_all_stock_tables()
    print(f"找到 {len(tables)} 個股票表")
    
    if tables:
        # 檢查第一個表的結構
        table_name = tables[0]
        print(f"\n檢查表格: {table_name}")
        
        # 查看表格欄位
        query = f"""
        SELECT COLUMN_NAME, DATA_TYPE 
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_NAME = '{table_name}'
        ORDER BY ORDINAL_POSITION
        """
        
        cursor = db.conn.cursor()
        cursor.execute(query)
        columns = cursor.fetchall()
        
        print("表格欄位:")
        for col in columns:
            print(f"  - {col[0]} ({col[1]})")
        
        # 查看前幾筆資料
        query = f"SELECT TOP 3 * FROM [{table_name}]"
        cursor.execute(query)
        rows = cursor.fetchall()
        
        print(f"\n前3筆資料:")
        for i, row in enumerate(rows):
            print(f"  第{i+1}筆: {row}")
            
    else:
        print("沒有找到股票表")
        
except Exception as e:
    print(f"錯誤: {e}")
    import traceback
    traceback.print_exc()
