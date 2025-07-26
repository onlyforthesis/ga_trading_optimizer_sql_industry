from db_connector import DBConnector
from ga_optimizer import TradingParameters, TradingResult

try:
    db = DBConnector()
    
    # 建立測試資料
    test_params = TradingParameters(
        m_intervals=20,
        hold_days=5,
        target_profit_ratio=0.08,  # 調整為8%的目標利潤，更合理
        alpha=15.0  # 代表15%的門檻值，在新範圍內更合理
    )
    
    test_result = TradingResult(
        parameters=test_params,
        fitness=0.75,
        total_profit=0.15,
        win_rate=0.6,
        max_drawdown=0.1,
        sharpe_ratio=1.2
    )
    
    # 測試儲存功能
    test_table_name = "1101TW台泥"
    test_industry = "水泥"
    
    print(f'正在測試儲存功能...')
    print(f'表名稱: {test_table_name}')
    print(f'產業: {test_industry}')
    
    db.save_best_params(test_table_name, test_result, test_industry)
    
    print('✅ 儲存測試成功！')
    
    # 查詢剛才插入的資料
    cursor = db.conn.cursor()
    cursor.execute("SELECT TOP 1 * FROM BestParameters ORDER BY Id DESC")
    row = cursor.fetchone()
    
    if row:
        print('\n=== 最新插入的資料 ===')
        print(f'ID: {row[0]}')
        print(f'股票名稱: {row[1]}')
        print(f'最佳區間: {row[2]}')
        print(f'持有天數: {row[3]}')
        print(f'適應度: {row[10]}')
        print(f'股票代碼: {row[12]}')
        print(f'產業: {row[13]}')
    
except Exception as e:
    print(f'錯誤: {e}')
    import traceback
    traceback.print_exc()
