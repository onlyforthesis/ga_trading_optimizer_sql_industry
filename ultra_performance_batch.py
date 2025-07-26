"""
超高性能批次處理器
針對多核心系統優化，最大化利用硬體資源
"""

import multiprocessing as mp
import time
import os
import sys
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from db_connector import DBConnector
from fast_ga_optimizer import fast_optimize, create_speed_preset

# 系統優化設定
def optimize_system_settings():
    """優化系統設定以獲得最佳性能"""
    # 設定環境變數優化數值計算
    cpu_count = mp.cpu_count()
    
    env_settings = {
        'OMP_NUM_THREADS': str(cpu_count),
        'NUMBA_NUM_THREADS': str(cpu_count),
        'MKL_NUM_THREADS': str(cpu_count),
        'OPENBLAS_NUM_THREADS': str(cpu_count),
        'PYTHONHASHSEED': '0',  # 確保可重現性
    }
    
    for var, value in env_settings.items():
        os.environ[var] = value
    
    return cpu_count

class UltraHighPerformanceBatch:
    def __init__(self):
        self.cpu_count = optimize_system_settings()
        self.max_workers = self.calculate_optimal_workers()
        self.target_stocks = [
            '台積電', '鴻海', '聯發科', '台達電', '廣達', '富邦金', '國泰金', '中信金', '兆豐金', '玉山金',
            '台塑', '南亞', '統一', '台泥', '亞泥', '華新', '日月光投控', '華碩', '聯詠', '和碩',
            '元大金', '中鋼', '開發金', '大成', '中租-KY', '遠東新', '台塑化', '研華', '華南金', '台新金',
            '新光金', '台灣大', '豐泰', '合庫金', '寶成', '和泰車', '大聯大', '陽明', '萬海', '永豐餘',
            '統一超', '國票金', '卜蜂', '美利達', '南電', '中保科', '上海商銀', '緯創', '第一金'
        ]
    
    def calculate_optimal_workers(self):
        """計算最佳工作進程數"""
        # 基於 CPU 核心數和系統資源
        if self.cpu_count >= 16:
            return min(12, self.cpu_count - 2)  # 高端系統
        elif self.cpu_count >= 8:
            return min(8, self.cpu_count - 1)   # 中高端系統
        elif self.cpu_count >= 4:
            return min(4, self.cpu_count)       # 中端系統
        else:
            return max(2, self.cpu_count)       # 低端系統
    
    def get_system_info(self):
        """獲取系統信息（不依賴 psutil）"""
        try:
            # 嘗試獲取記憶體信息
            if sys.platform == "win32":
                import ctypes
                class MEMORYSTATUSEX(ctypes.Structure):
                    _fields_ = [
                        ("dwLength", ctypes.c_ulong),
                        ("dwMemoryLoad", ctypes.c_ulong),
                        ("ullTotalPhys", ctypes.c_ulonglong),
                        ("ullAvailPhys", ctypes.c_ulonglong),
                        ("ullTotalPageFile", ctypes.c_ulonglong),
                        ("ullAvailPageFile", ctypes.c_ulonglong),
                        ("ullTotalVirtual", ctypes.c_ulonglong),
                        ("ullAvailVirtual", ctypes.c_ulonglong),
                        ("sullAvailExtendedVirtual", ctypes.c_ulonglong),
                    ]
                
                memory_status = MEMORYSTATUSEX()
                memory_status.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
                ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(memory_status))
                
                total_memory_gb = memory_status.ullTotalPhys / (1024**3)
                available_memory_gb = memory_status.ullAvailPhys / (1024**3)
                
                return {
                    'cpu_count': self.cpu_count,
                    'total_memory_gb': round(total_memory_gb, 1),
                    'available_memory_gb': round(available_memory_gb, 1),
                    'memory_usage_percent': round((1 - available_memory_gb/total_memory_gb) * 100, 1)
                }
        except:
            pass
        
        # 回退方案
        return {
            'cpu_count': self.cpu_count,
            'total_memory_gb': 'Unknown',
            'available_memory_gb': 'Unknown',
            'memory_usage_percent': 'Unknown'
        }
    
    def print_system_analysis(self):
        """顯示系統分析結果"""
        info = self.get_system_info()
        
        print("🖥️  系統性能分析")
        print("=" * 70)
        print(f"CPU 核心數: {info['cpu_count']}")
        print(f"記憶體總量: {info['total_memory_gb']} GB")
        print(f"可用記憶體: {info['available_memory_gb']} GB") 
        print(f"記憶體使用率: {info['memory_usage_percent']}%")
        print(f"最佳工作進程數: {self.max_workers}")
        
        # 性能等級評估
        if self.cpu_count >= 12:
            level = "🚀 超高性能系統"
            estimate = "~5-8分鐘"
        elif self.cpu_count >= 8:
            level = "⚡ 高性能系統" 
            estimate = "~8-12分鐘"
        elif self.cpu_count >= 4:
            level = "💼 標準性能系統"
            estimate = "~15-25分鐘"
        else:
            level = "📱 基礎性能系統"
            estimate = "~30-45分鐘"
        
        print(f"系統等級: {level}")
        print(f"預估批次處理時間: {estimate} (49檔股票)")
    
    def chunk_stocks(self, stock_list, chunk_size=None):
        """將股票列表分塊以優化記憶體使用"""
        if chunk_size is None:
            # 根據系統資源動態決定分塊大小
            if self.cpu_count >= 12:
                chunk_size = 8
            elif self.cpu_count >= 8:
                chunk_size = 6
            elif self.cpu_count >= 4:
                chunk_size = 4
            else:
                chunk_size = 2
        
        for i in range(0, len(stock_list), chunk_size):
            yield stock_list[i:i + chunk_size]
    
    def process_stock_chunk(self, stock_chunk, speed_mode='fast'):
        """處理一個股票塊"""
        results = []
        
        # 為每個塊創建獨立的資料庫連接
        db = DBConnector()
        
        for table, stock_info in stock_chunk:
            try:
                # 驗證表格
                if not db.validate_stock_table(table):
                    results.append({
                        'table': table,
                        'status': 'skip',
                        'reason': '不是有效的股票資料表',
                        'stock_name': stock_info.get('name', '未知')
                    })
                    continue
                
                # 讀取數據
                data = db.read_stock_data(table)
                if data.empty or len(data) < 50:
                    results.append({
                        'table': table,
                        'status': 'skip',
                        'reason': f'資料不足 ({len(data)} 筆)',
                        'stock_name': stock_info.get('name', '未知')
                    })
                    continue
                
                # 快速優化
                start_time = time.time()
                result = fast_optimize(data, speed_mode)
                process_time = time.time() - start_time
                
                # 保存結果
                stock_code = db.extract_stock_code_from_table_name(table)
                info = db.get_stock_info(stock_code)
                industry = info['Industry'] if info else "未知"
                
                db.save_best_params(table, result, industry)
                
                results.append({
                    'table': table,
                    'status': 'success',
                    'stock_name': stock_info.get('name', info.get('StockName', '未知')),
                    'industry': industry,
                    'fitness': result.fitness,
                    'total_profit': result.total_profit,
                    'win_rate': result.win_rate,
                    'sharpe_ratio': result.sharpe_ratio,
                    'process_time': process_time
                })
                
            except Exception as e:
                results.append({
                    'table': table,  
                    'status': 'error',
                    'reason': str(e),
                    'stock_name': stock_info.get('name', '未知')
                })
        
        return results
    
    def ultra_fast_batch_optimize(self, speed_mode='fast', use_chunking=True):
        """超高性能批次優化"""
        self.print_system_analysis()
        
        print(f"\n🚀 啟動超高性能批次優化")
        print(f"速度模式: {speed_mode}")
        print(f"分塊處理: {'啟用' if use_chunking else '禁用'}")
        print("=" * 70)
        
        db = DBConnector()
        db.create_best_params_table()
        
        # 獲取目標股票表格
        all_tables = db.get_all_stock_tables()
        target_tables = []
        stock_mapping = {}
        
        for table in all_tables:
            for stock_name in self.target_stocks:
                if stock_name in table:
                    target_tables.append(table)
                    stock_mapping[table] = {'name': stock_name}
                    break
        
        if not target_tables:
            return "❌ 沒有找到匹配的股票表格"
        
        print(f"🎯 找到 {len(target_tables)} 個匹配的股票表格")
        
        start_time = time.time()
        all_results = []
        
        if use_chunking and len(target_tables) > self.max_workers:
            # 分塊處理模式 - 適合大量股票
            stock_data = [(table, stock_mapping[table]) for table in target_tables]
            chunks = list(self.chunk_stocks(stock_data))
            
            print(f"🔄 分成 {len(chunks)} 個處理塊，每塊最多 {len(chunks[0]) if chunks else 0} 檔股票")
            
            for i, chunk in enumerate(chunks, 1):
                chunk_start = time.time()
                print(f"\n處理第 {i}/{len(chunks)} 塊...")
                
                # 並行處理當前塊
                with ProcessPoolExecutor(max_workers=min(self.max_workers, len(chunk))) as executor:
                    chunk_tasks = [chunk[j:j+1] for j in range(len(chunk))]  # 每個任務處理一檔股票
                    
                    future_to_task = {
                        executor.submit(self.process_stock_chunk, task, speed_mode): task 
                        for task in chunk_tasks
                    }
                    
                    for future in as_completed(future_to_task):
                        results = future.result()
                        all_results.extend(results)
                        
                        # 顯示進度
                        completed = len(all_results)
                        total = len(target_tables)
                        percent = (completed / total) * 100
                        print(f"進度: {completed}/{total} ({percent:.1f}%)")
                
                chunk_time = (time.time() - chunk_start) / 60
                print(f"第 {i} 塊完成，耗時: {chunk_time:.1f} 分鐘")
        
        else:
            # 直接並行處理模式 - 適合中等數量股票
            print(f"🔄 直接並行處理，使用 {self.max_workers} 個工作進程")
            
            stock_tasks = [([table, stock_mapping[table]], speed_mode) for table in target_tables]
            
            with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_stock = {
                    executor.submit(self.process_stock_chunk, [task[0]], task[1]): task[0][0] 
                    for task in stock_tasks
                }
                
                for future in as_completed(future_to_stock):
                    results = future.result()
                    all_results.extend(results)
                    
                    # 顯示進度
                    completed = len(all_results)
                    total = len(target_tables)
                    percent = (completed / total) * 100
                    print(f"進度: {completed}/{total} ({percent:.1f}%)")
        
        # 統計結果
        total_time = (time.time() - start_time) / 60
        successful = [r for r in all_results if r['status'] == 'success']
        skipped = [r for r in all_results if r['status'] == 'skip']
        failed = [r for r in all_results if r['status'] == 'error']
        
        # 生成報告
        return self.generate_performance_report(
            all_results, successful, skipped, failed, total_time, speed_mode
        )
    
    def generate_performance_report(self, all_results, successful, skipped, failed, total_time, speed_mode):
        """生成性能報告"""
        report = []
        
        report.append("=" * 80)
        report.append("🎉 超高性能批次優化完成！")
        report.append("=" * 80)
        report.append(f"⚡ 速度模式: {speed_mode}")
        report.append(f"⏰ 總耗時: {total_time:.1f} 分鐘")
        report.append(f"🖥️  使用 {self.max_workers} 個並行進程")
        report.append(f"📊 處理結果:")
        report.append(f"   ✅ 成功: {len(successful)} 檔")
        report.append(f"   ⚠️  跳過: {len(skipped)} 檔")
        report.append(f"   ❌ 失敗: {len(failed)} 檔")
        
        if successful:
            avg_time = total_time / len(all_results)
            avg_fitness = sum(r['fitness'] for r in successful) / len(successful)
            avg_profit = sum(r['total_profit'] for r in successful) / len(successful)
            avg_win_rate = sum(r['win_rate'] for r in successful) / len(successful)
            
            report.append(f"\n📈 性能統計:")
            report.append(f"   ⚡ 平均每檔耗時: {avg_time:.2f} 分鐘")
            report.append(f"   🎯 平均適應度: {avg_fitness:.4f}")
            report.append(f"   💰 平均收益: {avg_profit:.2f}%")
            report.append(f"   🏆 平均勝率: {avg_win_rate:.1%}")
            
            # 顯示最佳表現股票
            best_stocks = sorted(successful, key=lambda x: x['fitness'], reverse=True)[:5]
            report.append(f"\n🏆 表現最佳的5檔股票:")
            for i, stock in enumerate(best_stocks, 1):
                report.append(f"   {i}. {stock['stock_name']}: 適應度={stock['fitness']:.4f}, "
                             f"收益={stock['total_profit']:.2f}%")
        
        if failed:
            report.append(f"\n❌ 失敗的股票:")
            for stock in failed[:10]:  # 只顯示前10個
                report.append(f"   • {stock['stock_name']}: {stock['reason']}")
            if len(failed) > 10:
                report.append(f"   ... 以及其他 {len(failed)-10} 檔")
        
        # 系統性能評估
        stocks_per_minute = len(all_results) / total_time if total_time > 0 else 0
        report.append(f"\n🚀 系統性能評估:")
        report.append(f"   處理速度: {stocks_per_minute:.1f} 檔股票/分鐘")
        
        if stocks_per_minute > 5:
            report.append("   🎉 超高性能！您的系統表現優異")
        elif stocks_per_minute > 3:
            report.append("   ⚡ 高性能！系統運行良好")
        elif stocks_per_minute > 1:
            report.append("   💼 標準性能，運行正常")
        else:
            report.append("   📝 建議檢查系統資源使用情況")
        
        return "\n".join(report)

def run_ultra_performance_batch():
    """運行超高性能批次處理"""
    print("🚀 超高性能批次處理器")
    print("自動優化系統配置以獲得最佳性能")
    print("=" * 70)
    
    batch_processor = UltraHighPerformanceBatch()
    
    print("\n選擇速度模式:")
    print("1. ⚡ 超高速模式 (ultra_fast) - 最快速度")
    print("2. 🚀 快速模式 (fast) - 平衡推薦")
    print("3. ⚖️  平衡模式 (balanced) - 品質平衡")
    print("4. 🎯 品質模式 (quality) - 最高品質")
    
    modes = ['ultra_fast', 'fast', 'balanced', 'quality']
    
    try:
        choice = input("\n請選擇模式 (1-4): ").strip()
        if choice in ['1', '2', '3', '4']:
            selected_mode = modes[int(choice) - 1]
            
            print(f"\n🎯 已選擇: {selected_mode} 模式")
            print("🚀 開始超高性能批次處理...")
            
            result = batch_processor.ultra_fast_batch_optimize(
                speed_mode=selected_mode,
                use_chunking=True
            )
            
            print(result)
            
        else:
            print("❌ 無效選擇")
            
    except KeyboardInterrupt:
        print("\n\n⚠️ 用戶中斷處理")
    except Exception as e:
        print(f"\n❌ 處理過程發生錯誤: {str(e)}")

if __name__ == "__main__":
    run_ultra_performance_batch()
