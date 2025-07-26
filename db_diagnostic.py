#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
資料庫連接診斷工具
"""

import pyodbc
import sys

def test_odbc_drivers():
    """測試可用的ODBC驅動程式"""
    print("=== ODBC 驅動程式檢查 ===")
    drivers = pyodbc.drivers()
    print(f"可用的驅動程式: {len(drivers)} 個")
    
    sql_drivers = [d for d in drivers if 'SQL Server' in d]
    if sql_drivers:
        print("✅ 找到 SQL Server 驅動程式:")
        for driver in sql_drivers:
            print(f"   - {driver}")
        return sql_drivers[0]  # 返回第一個可用的驅動程式
    else:
        print("❌ 未找到 SQL Server 驅動程式")
        print("請安裝 ODBC Driver for SQL Server")
        return None

def test_db_connection(server_name, database_name, driver_name):
    """測試資料庫連接"""
    print(f"\n=== 資料庫連接測試 ===")
    print(f"伺服器: {server_name}")
    print(f"資料庫: {database_name}")
    print(f"驅動程式: {driver_name}")
    
    conn_str = f"DRIVER={{{driver_name}}};SERVER={server_name};DATABASE={database_name};Trusted_Connection=yes;"
    print(f"連接字串: {conn_str}")
    
    try:
        print("嘗試連接...")
        conn = pyodbc.connect(conn_str)
        print("✅ 資料庫連接成功!")
        
        # 測試基本查詢
        cursor = conn.cursor()
        cursor.execute("SELECT @@VERSION")
        version = cursor.fetchone()[0]
        print(f"SQL Server 版本: {version}")
        
        # 檢查資料表
        cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE'")
        tables = cursor.fetchall()
        print(f"資料表數量: {len(tables)}")
        
        if len(tables) > 0:
            print("前幾個資料表:")
            for i, table in enumerate(tables[:5]):
                print(f"   - {table[0]}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 資料庫連接失敗: {e}")
        return False

def suggest_solutions():
    """提供解決方案建議"""
    print(f"\n=== 解決方案建議 ===")
    print("1. 確認 SQL Server 服務是否啟動:")
    print("   - 開啟 Windows 服務管理員")
    print("   - 尋找 'SQL Server' 相關服務")
    print("   - 確認服務狀態為 '執行中'")
    
    print("\n2. 確認伺服器名稱:")
    print("   - 在 SQL Server Management Studio 中查看伺服器名稱")
    print("   - 或在命令提示字元執行: sqlcmd -L")
    
    print("\n3. 確認資料庫是否存在:")
    print("   - 使用 SQL Server Management Studio 連接")
    print("   - 檢查是否有 'StockDB' 資料庫")
    
    print("\n4. 檢查驅動程式:")
    print("   - 下載並安裝 Microsoft ODBC Driver for SQL Server")
    print("   - 網址: https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server")

def main():
    print("股票交易系統 - 資料庫診斷工具")
    print("=" * 50)
    
    # 測試驅動程式
    driver = test_odbc_drivers()
    if not driver:
        suggest_solutions()
        return
    
    # 測試連接
    server_name = "DESKTOP-TOB09L9"  # 目前設定的伺服器名稱
    database_name = "StockDB"       # 目前設定的資料庫名稱
    
    success = test_db_connection(server_name, database_name, driver)
    
    if not success:
        print(f"\n是否要嘗試其他伺服器名稱? (目前: {server_name})")
        print("常見的伺服器名稱格式:")
        print("- localhost")
        print("- .\\SQLEXPRESS")
        print("- (local)\\SQLEXPRESS")
        print("- 電腦名稱\\SQLEXPRESS")
        
        suggest_solutions()

if __name__ == "__main__":
    main()
