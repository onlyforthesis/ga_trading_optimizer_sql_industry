"""
指定股票批次優化腳本
專門處理指定的49檔台股
"""

from db_connector import DBConnector
from ga_optimizer import GeneticAlgorithm
import time

def optimize_specific_stocks():
    """批次優化指定的49檔股票"""
    
    # 指定的股票清單（股票名稱）
    target_stocks = [
        '台積電', '鴻海', '聯發科', '台達電', '廣達', '富邦金', '國泰金', '中信金', '兆豐金', '玉山金',
        '台塑', '南亞', '統一', '台泥', '亞泥', '華新', '日月光投控', '華碩', '聯詠', '和碩',
        '元大金', '中鋼', '開發金', '大成', '中租-KY', '遠東新', '台塑化', '研華', '華南金', '台新金',
        '新光金', '台灣大', '豐泰', '合庫金', '寶成', '和泰車', '大聯大', '陽明', '萬海', '永豐餘',
        '統一超', '國票金', '卜蜂', '美利達', '南電', '中保科', '上海商銀', '緯創', '第一金'
    ]
    
    db = DBConnector()
    db.create_best_params_table()
    
    # 取得所有股票表格
    all_tables = db.get_all_stock_tables()
    
    # 篩選出目標股票的表格
    target_tables = []
    for table in all_tables:
        for stock_name in target_stocks:
            if stock_name in table:
                target_tables.append(table)
                break
    
    log = [f"🎯 開始批次分析指定的 {len(target_stocks)} 檔股票"]
    log.append(f"📊 在資料庫中找到 {len(target_tables)} 個匹配的股票表格")
    log.append(f"⏰ 開始時間: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    log.append("-" * 60)
    
    processed = 0
    skipped = 0
    found_stocks = []
    missing_stocks = []
    
    for table in target_tables:
        try:
            # 驗證表格是否有效
            if not db.validate_stock_table(table):
                log.append(f"⚠️  跳過 {table}: 不是有效的股票資料表")
                skipped += 1
                continue
                
            data = db.read_stock_data(table)
            if data.empty or len(data) < 50:
                log.append(f"⚠️  跳過 {table}: 資料不足 ({len(data)} 筆)")
                skipped += 1
                continue
                
            # 從表名稱中提取股票代碼來查詢資訊
            stock_code = db.extract_stock_code_from_table_name(table)
            info = db.get_stock_info(stock_code)
            industry = info['Industry'] if info else "未知"
            stock_name = info['StockName'] if info else "未知"
            
            found_stocks.append(stock_name)
            
            log.append(f"🔄 正在處理: {table} ({stock_name}, {industry})")
            
            # 設定遺傳演算法參數
            ga = GeneticAlgorithm(
                data, 
                population_size=50,  # 增加族群大小以獲得更好結果
                generations=100,     # 增加世代數
                max_time_minutes=5.0,  # 每檔股票最多5分鐘
                convergence_threshold=0.001,
                convergence_generations=10
            )
            
            best_result = ga.evolve()
            db.save_best_params(table, best_result, industry)
            
            processed += 1
            log.append(f"✅ {table} 完成!")
            log.append(f"   📈 適應度: {best_result.fitness:.4f}")
            log.append(f"   💰 總收益: {best_result.total_profit:.2f}%")
            log.append(f"   🎯 勝率: {best_result.win_rate:.2f}%")
            log.append(f"   📊 夏普比率: {best_result.sharpe_ratio:.4f}")
            log.append("")
            
        except Exception as e:
            log.append(f"❌ {table} 失敗: {str(e)}")
            skipped += 1
    
    # 檢查哪些股票沒有找到
    for stock_name in target_stocks:
        if stock_name not in found_stocks:
            missing_stocks.append(stock_name)
    
    # 輸出總結
    log.append("=" * 60)
    log.append(f"📊 批次分析完成！")
    log.append(f"⏰ 結束時間: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    log.append(f"✅ 成功處理: {processed} 檔")
    log.append(f"⚠️  跳過: {skipped} 檔")
    log.append(f"🔍 找到的股票: {len(found_stocks)} 檔")
    
    if found_stocks:
        log.append(f"📋 成功處理的股票:")
        for stock in found_stocks:
            log.append(f"   • {stock}")
    
    if missing_stocks:
        log.append(f"⚠️  未找到的股票 ({len(missing_stocks)} 檔):")
        for stock in missing_stocks:
            log.append(f"   • {stock}")
    
    return "\n".join(log)

def check_available_stocks():
    """檢查資料庫中有哪些目標股票可用"""
    
    target_stocks = [
        '台積電', '鴻海', '聯發科', '台達電', '廣達', '富邦金', '國泰金', '中信金', '兆豐金', '玉山金',
        '台塑', '南亞', '統一', '台泥', '亞泥', '華新', '日月光投控', '華碩', '聯詠', '和碩',
        '元大金', '中鋼', '開發金', '大成', '中租-KY', '遠東新', '台塑化', '研華', '華南金', '台新金',
        '新光金', '台灣大', '豐泰', '合庫金', '寶成', '和泰車', '大聯大', '陽明', '萬海', '永豐餘',
        '統一超', '國票金', '卜蜂', '美利達', '南電', '中保科', '上海商銀', '緯創', '第一金'
    ]
    
    db = DBConnector()
    all_tables = db.get_all_stock_tables()
    
    available = []
    missing = []
    
    for stock_name in target_stocks:
        found = False
        for table in all_tables:
            if stock_name in table:
                available.append((stock_name, table))
                found = True
                break
        if not found:
            missing.append(stock_name)
    
    log = [f"🔍 目標股票可用性檢查"]
    log.append(f"📋 目標股票總數: {len(target_stocks)}")
    log.append(f"✅ 可用股票: {len(available)}")
    log.append(f"❌ 缺少股票: {len(missing)}")
    log.append("")
    
    if available:
        log.append("✅ 可用的股票:")
        for stock_name, table_name in available:
            log.append(f"   • {stock_name} -> {table_name}")
        log.append("")
    
    if missing:
        log.append("❌ 缺少的股票:")
        for stock_name in missing:
            log.append(f"   • {stock_name}")
    
    return "\n".join(log)

if __name__ == "__main__":
    print("=== 指定股票批次優化工具 ===")
    print("1. 檢查可用股票")
    print("2. 開始批次優化")
    
    choice = input("\n請選擇功能 (1/2): ").strip()
    
    if choice == "1":
        result = check_available_stocks()
        print(result)
    elif choice == "2":
        print("\n開始批次優化...")
        result = optimize_specific_stocks()
        print(result)
    else:
        print("無效選擇")
