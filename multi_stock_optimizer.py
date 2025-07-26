from db_connector import DBConnector
from ga_optimizer import GeneticAlgorithm

def optimize_all_stocks():
    db = DBConnector()
    db.create_best_params_table()
    tables = db.get_all_stock_tables()
    log = [f"開始批次分析，找到 {len(tables)} 個股票表格"]
    
    processed = 0
    skipped = 0
    
    for table in tables:
        try:
            # 驗證表格是否有效
            if not db.validate_stock_table(table):
                log.append(f"⚠️ 跳過 {table}: 不是有效的股票資料表")
                skipped += 1
                continue
                
            data = db.read_stock_data(table)
            if data.empty or len(data) < 50:
                log.append(f"⚠️ 跳過 {table}: 資料不足 ({len(data)} 筆)")
                skipped += 1
                continue
                
            # 從表名稱中提取股票代碼來查詢資訊
            stock_code = db.extract_stock_code_from_table_name(table)
            info = db.get_stock_info(stock_code)
            industry = info['Industry'] if info else "未知"
            
            ga = GeneticAlgorithm(
                data, 
                population_size=30, 
                generations=50,
                max_time_minutes=3.0,  # 批次分析用較短時間
                convergence_threshold=0.001,
                convergence_generations=5
            )
            best_result = ga.evolve()
            db.save_best_params(table, best_result, industry)
            
            processed += 1
            log.append(f"✅ {table} 完成 (產業: {industry}, 適應度: {best_result.fitness:.4f})")
            
        except Exception as e:
            log.append(f"❌ {table} 失敗: {str(e)}")
            skipped += 1
    
    log.append(f"\n📊 批次分析完成！處理: {processed} 個, 跳過: {skipped} 個")
    return "\n".join(log)

def optimize_by_industry(industry):
    db = DBConnector()
    db.create_best_params_table()
    stocks = db.get_stocks_by_industry(industry)
    log = [f"開始分析產業 '{industry}'，找到 {len(stocks)} 隻股票"]
    
    processed = 0
    skipped = 0
    
    for stock in stocks:
        try:
            # 驗證表格是否有效
            if not db.validate_stock_table(stock):
                log.append(f"⚠️ 跳過 {stock}: 不是有效的股票資料表")
                skipped += 1
                continue
                
            data = db.read_stock_data(stock)
            if data.empty or len(data) < 50:
                log.append(f"⚠️ 跳過 {stock}: 資料不足 ({len(data)} 筆)")
                skipped += 1
                continue
                
            ga = GeneticAlgorithm(
                data, 
                population_size=30, 
                generations=50,
                max_time_minutes=3.0,  # 批次分析用較短時間
                convergence_threshold=0.001,
                convergence_generations=5
            )
            best_result = ga.evolve()
            db.save_best_params(stock, best_result, industry)
            
            processed += 1
            log.append(f"✅ {stock} 完成 (適應度: {best_result.fitness:.4f})")
            
        except Exception as e:
            log.append(f"❌ {stock} 失敗: {str(e)}")
            skipped += 1
    
    log.append(f"\n📊 產業分析完成！處理: {processed} 個, 跳過: {skipped} 個")
    return "\n".join(log)
