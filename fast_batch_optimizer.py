"""
加速版指定股票批次優化器
使用多種加速策略來大幅縮短處理時間
"""

from db_connector import DBConnector
from fast_ga_optimizer import FastGeneticAlgorithm, fast_optimize, create_speed_preset
import time
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, as_completed
import sys

def optimize_single_stock_fast(args):
    """單一股票快速優化 - 用於並行處理"""
    table, speed_mode, stock_info = args
    
    try:
        # 建立資料庫連接（每個進程需要獨立連接）
        db = DBConnector()
        
        # 驗證表格
        if not db.validate_stock_table(table):
            return {
                'table': table,
                'status': 'skip',
                'reason': '不是有效的股票資料表',
                'stock_name': stock_info.get('name', '未知')
            }
        
        # 讀取數據
        data = db.read_stock_data(table)
        if data.empty or len(data) < 50:
            return {
                'table': table,
                'status': 'skip',
                'reason': f'資料不足 ({len(data)} 筆)',
                'stock_name': stock_info.get('name', '未知')
            }
        
        # 快速優化
        result = fast_optimize(data, speed_mode)
        
        # 保存結果
        stock_code = db.extract_stock_code_from_table_name(table)
        info = db.get_stock_info(stock_code)
        industry = info['Industry'] if info else "未知"
        
        db.save_best_params(table, result, industry)
        
        return {
            'table': table,
            'status': 'success',
            'stock_name': stock_info.get('name', info.get('StockName', '未知')),
            'industry': industry,
            'fitness': result.fitness,
            'total_profit': result.total_profit,
            'win_rate': result.win_rate,
            'sharpe_ratio': result.sharpe_ratio
        }
        
    except Exception as e:
        return {
            'table': table,
            'status': 'error',
            'reason': str(e),
            'stock_name': stock_info.get('name', '未知')
        }

def optimize_specific_stocks_fast(speed_mode='fast', max_workers=None, use_multiprocessing=True):
    """加速版批次優化指定股票"""
    
    target_stocks = [
        '台積電', '鴻海', '聯發科', '台達電', '廣達', '富邦金', '國泰金', '中信金', '兆豐金', '玉山金',
        '台塑', '南亞', '統一', '台泥', '亞泥', '華新', '日月光投控', '華碩', '聯詠', '和碩',
        '元大金', '中鋼', '開發金', '大成', '中租-KY', '遠東新', '台塑化', '研華', '華南金', '台新金',
        '新光金', '台灣大', '豐泰', '合庫金', '寶成', '和泰車', '大聯大', '陽明', '萬海', '永豐餘',
        '統一超', '國票金', '卜蜂', '美利達', '南電', '中保科', '上海商銀', '緯創', '第一金'
    ]
    
    # 速度模式說明
    speed_info = {
        'ultra_fast': '⚡ 超高速模式 (每檔約30秒)',
        'fast': '🚀 快速模式 (每檔約1分鐘)', 
        'balanced': '⚖️ 平衡模式 (每檔約2分鐘)',
        'quality': '🎯 品質模式 (每檔約3分鐘)'
    }
    
    db = DBConnector()
    db.create_best_params_table()
    
    # 取得目標股票表格
    all_tables = db.get_all_stock_tables()
    target_tables = []
    stock_mapping = {}
    
    for table in all_tables:
        for stock_name in target_stocks:
            if stock_name in table:
                target_tables.append(table)
                stock_mapping[table] = {'name': stock_name}
                break
    
    if max_workers is None:
        max_workers = min(4, mp.cpu_count())  # 限制最大進程數
    
    log = [f"🚀 加速版批次優化 - {speed_info.get(speed_mode, speed_mode)}"]
    log.append(f"🎯 目標股票: {len(target_stocks)} 檔")
    log.append(f"📊 找到匹配表格: {len(target_tables)} 個")
    log.append(f"⚡ 並行處理: {'是' if use_multiprocessing else '否'} (工作進程: {max_workers})")
    log.append(f"⏰ 開始時間: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    log.append("-" * 70)
    
    start_time = time.time()
    results = []
    
    if use_multiprocessing and len(target_tables) > 1:
        # 並行處理
        log.append(f"🔄 啟動並行處理 ({max_workers} 個工作進程)...")
        
        # 準備參數
        task_args = [(table, speed_mode, stock_mapping[table]) for table in target_tables]
        
        try:
            with ProcessPoolExecutor(max_workers=max_workers) as executor:
                # 提交所有任務
                future_to_table = {executor.submit(optimize_single_stock_fast, args): args[0] 
                                 for args in task_args}
                
                # 收集結果
                for future in as_completed(future_to_table):
                    table = future_to_table[future]
                    try:
                        result = future.result()
                        results.append(result)
                        
                        # 即時顯示進度
                        if result['status'] == 'success':
                            log.append(f"✅ {result['stock_name']} ({result['table']})")
                            log.append(f"   適應度: {result['fitness']:.4f}, 收益: {result['total_profit']:.2f}%")
                        elif result['status'] == 'skip':
                            log.append(f"⚠️  {result['stock_name']}: {result['reason']}")
                        else:
                            log.append(f"❌ {result['stock_name']}: {result['reason']}")
                        
                        print(f"已完成: {len(results)}/{len(target_tables)}")
                        
                    except Exception as e:
                        log.append(f"❌ {table} 處理失敗: {str(e)}")
                        results.append({
                            'table': table,
                            'status': 'error',
                            'reason': str(e),
                            'stock_name': stock_mapping.get(table, {}).get('name', '未知')
                        })
        
        except Exception as e:
            log.append(f"❌ 並行處理失敗: {str(e)}")
            log.append("🔄 回退到串行處理...")
            use_multiprocessing = False
    
    if not use_multiprocessing:
        # 串行處理
        log.append("🔄 使用串行處理...")
        for i, table in enumerate(target_tables, 1):
            log.append(f"🔄 ({i}/{len(target_tables)}) 處理 {stock_mapping[table]['name']}...")
            
            result = optimize_single_stock_fast((table, speed_mode, stock_mapping[table]))
            results.append(result)
            
            if result['status'] == 'success':
                log.append(f"✅ 完成! 適應度: {result['fitness']:.4f}")
            elif result['status'] == 'skip':
                log.append(f"⚠️  跳過: {result['reason']}")
            else:
                log.append(f"❌ 失敗: {result['reason']}")
    
    # 統計結果
    successful = [r for r in results if r['status'] == 'success']
    skipped = [r for r in results if r['status'] == 'skip']
    failed = [r for r in results if r['status'] == 'error']
    
    total_time = (time.time() - start_time) / 60
    avg_time_per_stock = total_time / len(results) if results else 0
    
    # 輸出總結
    log.append("=" * 70)
    log.append(f"📊 加速批次優化完成！")
    log.append(f"⏰ 總耗時: {total_time:.1f} 分鐘")
    log.append(f"⚡ 平均每檔: {avg_time_per_stock:.1f} 分鐘")
    log.append(f"✅ 成功: {len(successful)} 檔")
    log.append(f"⚠️  跳過: {len(skipped)} 檔")
    log.append(f"❌ 失敗: {len(failed)} 檔")
    
    if successful:
        log.append(f"\n🏆 成功處理的股票:")
        avg_fitness = sum(r['fitness'] for r in successful) / len(successful)
        avg_profit = sum(r['total_profit'] for r in successful) / len(successful)
        for r in successful:
            log.append(f"   • {r['stock_name']}: 適應度={r['fitness']:.4f}, 收益={r['total_profit']:.2f}%")
        log.append(f"\n📈 平均績效: 適應度={avg_fitness:.4f}, 收益={avg_profit:.2f}%")
    
    if skipped:
        log.append(f"\n⚠️  跳過的股票:")
        for r in skipped:
            log.append(f"   • {r['stock_name']}: {r['reason']}")
    
    if failed:
        log.append(f"\n❌ 失敗的股票:")
        for r in failed:
            log.append(f"   • {r['stock_name']}: {r['reason']}")
    
    return "\n".join(log)

def compare_speed_modes(sample_stock_table):
    """比較不同速度模式的效果"""
    db = DBConnector()
    data = db.read_stock_data(sample_stock_table)
    
    if data.empty:
        return "❌ 無法讀取股票資料進行比較"
    
    modes = ['ultra_fast', 'fast', 'balanced', 'quality']
    results = {}
    
    print("🧪 比較不同速度模式...")
    
    for mode in modes:
        print(f"\n測試 {mode} 模式...")
        start_time = time.time()
        
        try:
            result = fast_optimize(data, mode)
            elapsed = time.time() - start_time
            
            results[mode] = {
                'time': elapsed,
                'fitness': result.fitness,
                'profit': result.total_profit,
                'win_rate': result.win_rate
            }
            
            print(f"✅ {mode}: {elapsed:.1f}秒, 適應度={result.fitness:.4f}")
            
        except Exception as e:
            results[mode] = {'error': str(e)}
            print(f"❌ {mode}: {str(e)}")
    
    # 輸出比較結果
    report = [f"📊 速度模式比較報告 (股票: {sample_stock_table})"]
    report.append("-" * 50)
    
    for mode in modes:
        if 'error' not in results[mode]:
            r = results[mode]
            report.append(f"{mode:12}: {r['time']:6.1f}秒, 適應度={r['fitness']:7.4f}, "
                         f"收益={r['profit']:6.2f}%, 勝率={r['win_rate']:6.2f}%")
        else:
            report.append(f"{mode:12}: ❌ {results[mode]['error']}")
    
    return "\n".join(report)

if __name__ == "__main__":
    print("🚀 加速版指定股票批次優化工具")
    print("=" * 50)
    print("速度模式說明:")
    print("⚡ ultra_fast: 超高速 (約30秒/檔)")
    print("🚀 fast:       快速   (約1分鐘/檔)")
    print("⚖️ balanced:   平衡   (約2分鐘/檔)")
    print("🎯 quality:    品質   (約3分鐘/檔)")
    print("=" * 50)
    
    print("\n選項:")
    print("1. 超高速批次優化 (推薦用於快速測試)")
    print("2. 快速批次優化 (推薦用於日常使用)")
    print("3. 平衡批次優化")
    print("4. 品質批次優化")
    print("5. 速度模式比較測試")
    print("6. 退出")
    
    while True:
        try:
            choice = input("\n請選擇 (1-6): ").strip()
            
            if choice == "1":
                print("\n⚡ 啟動超高速批次優化...")
                result = optimize_specific_stocks_fast('ultra_fast', max_workers=4)
                print(result)
                
            elif choice == "2":
                print("\n🚀 啟動快速批次優化...")
                result = optimize_specific_stocks_fast('fast', max_workers=4)
                print(result)
                
            elif choice == "3":
                print("\n⚖️ 啟動平衡批次優化...")
                result = optimize_specific_stocks_fast('balanced', max_workers=3)
                print(result)
                
            elif choice == "4":
                print("\n🎯 啟動品質批次優化...")
                result = optimize_specific_stocks_fast('quality', max_workers=2)
                print(result)
                
            elif choice == "5":
                # 找一個樣本股票進行測試
                db = DBConnector()
                tables = db.get_all_stock_tables()
                sample_table = None
                for table in tables:
                    if '台積電' in table:
                        sample_table = table
                        break
                
                if sample_table:
                    result = compare_speed_modes(sample_table)
                    print(result)
                else:
                    print("❌ 找不到適合的測試股票")
                
            elif choice == "6":
                print("👋 再見！")
                break
                
            else:
                print("❌ 無效選擇")
                
        except KeyboardInterrupt:
            print("\n\n👋 用戶中斷")
            break
        except Exception as e:
            print(f"\n❌ 錯誤: {str(e)}")
