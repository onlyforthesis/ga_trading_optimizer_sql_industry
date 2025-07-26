"""
快速測試加速優化器修復
"""

def test_fast_optimizer():
    """測試加速優化器是否正常工作"""
    print("🧪 測試加速優化器修復...")
    
    try:
        from db_connector import DBConnector
        from fast_ga_optimizer import fast_optimize
        
        # 連接資料庫
        db = DBConnector()
        tables = db.get_all_stock_tables()
        
        if not tables:
            print("❌ 沒有可用的股票資料表")
            return False
        
        # 找一檔股票進行測試
        test_table = None
        test_stock_names = ['台積電', '鴻海', '聯發科']
        
        for table in tables:
            for stock_name in test_stock_names:
                if stock_name in table:
                    test_table = table
                    break
            if test_table:
                break
        
        if not test_table:
            test_table = tables[0]  # 使用第一檔可用股票
        
        print(f"📊 測試股票: {test_table}")
        
        # 載入資料
        data = db.read_stock_data(test_table)
        if data.empty:
            print("❌ 無法載入股票資料")
            return False
        
        print(f"📈 資料筆數: {len(data)}")
        
        # 測試超高速模式
        print("⚡ 測試超高速模式...")
        result = fast_optimize(data, 'ultra_fast')
        
        print(f"✅ 測試成功!")
        print(f"   適應度: {result.fitness:.4f}")
        print(f"   總收益: {result.total_profit:.2f}%")
        print(f"   勝率: {result.win_rate:.1%}")
        
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_batch_single_stock():
    """測試批次處理單一股票"""
    print("\n🎯 測試批次處理單一股票...")
    
    try:
        from fast_batch_optimizer import optimize_single_stock_fast
        from db_connector import DBConnector
        
        db = DBConnector()
        tables = db.get_all_stock_tables()
        
        # 找一檔測試股票
        test_table = None
        for table in tables:
            if '台積電' in table:
                test_table = table
                break
        
        if not test_table and tables:
            test_table = tables[0]
        
        if not test_table:
            print("❌ 沒有可用的測試股票")
            return False
        
        print(f"📊 測試股票: {test_table}")
        
        # 測試單一股票批次處理函數
        args = (test_table, 'ultra_fast', {'name': '測試股票'})
        result = optimize_single_stock_fast(args)
        
        print(f"✅ 批次處理測試結果:")
        print(f"   狀態: {result['status']}")
        print(f"   股票: {result['stock_name']}")
        
        if result['status'] == 'success':
            print(f"   適應度: {result['fitness']:.4f}")
            print(f"   收益: {result['total_profit']:.2f}%")
        elif result['status'] == 'error':
            print(f"   錯誤: {result['reason']}")
        
        return result['status'] == 'success'
        
    except Exception as e:
        print(f"❌ 批次處理測試失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 加速優化器修復測試")
    print("=" * 50)
    
    # 測試1: 基本優化功能
    test1_result = test_fast_optimizer()
    
    # 測試2: 批次處理功能
    test2_result = test_batch_single_stock()
    
    print("\n" + "=" * 50)
    print("📊 測試結果摘要:")
    print(f"基本優化功能: {'✅ 通過' if test1_result else '❌ 失敗'}")
    print(f"批次處理功能: {'✅ 通過' if test2_result else '❌ 失敗'}")
    
    if test1_result and test2_result:
        print("\n🎉 所有測試通過！加速優化器已修復")
        print("💡 現在可以使用以下方式執行批次優化:")
        print("   python fast_batch_optimizer.py")
        print("   或使用 GUI: python main.py")
    else:
        print("\n⚠️  部分測試失敗，請檢查錯誤訊息")
