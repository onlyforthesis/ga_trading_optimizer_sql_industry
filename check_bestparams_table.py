from db_connector import DBConnector
import pyodbc

try:
    db = DBConnector()
    cursor = db.conn.cursor()
    
    # 檢查 BestParameters 資料表的欄位結構
    print('=== BestParameters 資料表結構 ===')
    cursor.execute("""
    SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, CHARACTER_MAXIMUM_LENGTH
    FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_NAME = 'BestParameters'
    ORDER BY ORDINAL_POSITION
    """)
    
    columns = cursor.fetchall()
    if columns:
        for col in columns:
            print(f'欄位名稱: {col[0]}, 資料型別: {col[1]}, 可空值: {col[2]}, 最大長度: {col[3]}')
    else:
        print('找不到 BestParameters 資料表')
        
    # 檢查資料表是否真的存在
    print('\n=== 檢查資料表是否存在 ===')
    cursor.execute("""
    SELECT COUNT(*) as table_count 
    FROM INFORMATION_SCHEMA.TABLES 
    WHERE TABLE_NAME = 'BestParameters'
    """)
    result = cursor.fetchone()
    print(f'BestParameters 資料表數量: {result[0]}')
        
except Exception as e:
    print(f'錯誤: {e}')
    import traceback
    traceback.print_exc()
