from db_connector import DBConnector
import pyodbc

try:
    db = DBConnector()
    cursor = db.conn.cursor()
    
    print('正在修正 BestParameters 資料表結構...')
    
    # 添加 StockCode 欄位
    try:
        cursor.execute("ALTER TABLE BestParameters ADD StockCode NVARCHAR(50)")
        print('✅ 已添加 StockCode 欄位')
    except Exception as e:
        print(f'StockCode 欄位可能已存在: {e}')
    
    # 添加 Industry 欄位
    try:
        cursor.execute("ALTER TABLE BestParameters ADD Industry NVARCHAR(50)")
        print('✅ 已添加 Industry 欄位')
    except Exception as e:
        print(f'Industry 欄位可能已存在: {e}')
    
    # 提交變更
    db.conn.commit()
    
    # 再次檢查資料表結構
    print('\n=== 修正後的 BestParameters 資料表結構 ===')
    cursor.execute("""
    SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, CHARACTER_MAXIMUM_LENGTH
    FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_NAME = 'BestParameters'
    ORDER BY ORDINAL_POSITION
    """)
    
    columns = cursor.fetchall()
    for col in columns:
        print(f'欄位名稱: {col[0]}, 資料型別: {col[1]}, 可空值: {col[2]}, 最大長度: {col[3]}')
    
    print('\n✅ 資料表結構修正完成！')
        
except Exception as e:
    print(f'錯誤: {e}')
    import traceback
    traceback.print_exc()
