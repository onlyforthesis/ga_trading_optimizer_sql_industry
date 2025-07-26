from db_connector import DBConnector

try:
    db = DBConnector()
    
    print('=== 全面功能測試 ===')
    
    # 1. 測試取得產業列表
    print('1. 測試取得產業列表...')
    industries = db.get_industry_list()
    print(f'   ✅ 共找到 {len(industries)} 個產業')
    
    # 2. 測試根據產業取得股票
    if industries:
        test_industry = industries[0]
        print(f'2. 測試取得 "{test_industry}" 產業的股票...')
        stocks = db.get_stocks_by_industry(test_industry)
        print(f'   ✅ 共找到 {len(stocks)} 檔股票')
        
        # 3. 測試讀取股票資料
        if stocks:
            test_stock = stocks[0]
            print(f'3. 測試讀取 "{test_stock}" 的股票資料...')
            try:
                data = db.read_stock_data(test_stock)
                print(f'   ✅ 成功讀取 {len(data)} 筆資料')
            except Exception as e:
                print(f'   ❌ 讀取股票資料失敗: {e}')
            
            # 4. 測試提取股票代碼
            print(f'4. 測試從 "{test_stock}" 提取股票代碼...')
            extracted_code = db.extract_stock_code_from_table_name(test_stock)
            print(f'   ✅ 提取的代碼: {extracted_code}')
            
            # 5. 測試查詢股票資訊
            print(f'5. 測試查詢股票資訊...')
            info = db.get_stock_info(extracted_code)
            if info:
                print(f'   ✅ 股票資訊: {info}')
            else:
                print(f'   ❌ 找不到股票資訊')
    
    print('\n🎉 所有基本功能測試完成！')
    
except Exception as e:
    print(f'❌ 測試失敗: {e}')
    import traceback
    traceback.print_exc()
