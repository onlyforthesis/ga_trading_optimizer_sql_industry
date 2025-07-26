"""
加速優化演示腳本
比較標準版本與加速版本的性能差異
"""

import time
import sys
from db_connector import DBConnector

def demo_speed_comparison():
    """演示加速優化的效果"""
    
    print("🚀 加速優化演示")
    print("=" * 60)
    
    # 連接資料庫並找一檔測試股票
    db = DBConnector()
    tables = db.get_all_stock_tables()
    
    # 尋找台積電作為測試對象
    test_table = None
    for table in tables:
        if '台積電' in table:
            test_table = table
            break
    
    if not test_table:
        print("❌ 找不到台積電資料，使用第一檔可用股票")
        if tables:
            test_table = tables[0]
        else:
            print("❌ 沒有可用的股票資料")
            return
    
    print(f"📊 測試股票: {test_table}")
    
    # 載入股票資料
    data = db.read_stock_data(test_table)
    if data.empty:
        print("❌ 無法載入股票資料")
        return
    
    print(f"📈 資料筆數: {len(data)}")
    print("-" * 60)
    
    # 測試不同速度模式
    from fast_ga_optimizer import fast_optimize
    
    modes = [
        ('⚡ 超高速模式', 'ultra_fast'),
        ('🚀 快速模式', 'fast'),
        ('⚖️ 平衡模式', 'balanced'),
        ('🎯 品質模式', 'quality')
    ]
    
    results = {}
    
    for mode_name, mode_code in modes:
        print(f"\n🔄 測試 {mode_name}...")
        
        try:
            start_time = time.time()
            result = fast_optimize(data, mode_code)
            elapsed_time = time.time() - start_time
            
            results[mode_code] = {
                'name': mode_name,
                'time': elapsed_time,
                'fitness': result.fitness,
                'profit': result.total_profit,
                'win_rate': result.win_rate,
                'sharpe': result.sharpe_ratio
            }
            
            print(f"✅ 完成！耗時: {elapsed_time:.1f} 秒")
            print(f"   適應度: {result.fitness:.4f}")
            print(f"   總收益: {result.total_profit:.2f}%")
            print(f"   勝率: {result.win_rate:.1%}")
            
        except Exception as e:
            print(f"❌ 失敗: {str(e)}")
            results[mode_code] = {'name': mode_name, 'error': str(e)}
    
    # 輸出比較表格
    print("\n" + "=" * 80)
    print("📊 性能比較報告")
    print("=" * 80)
    print(f"{'模式':<15} {'時間(秒)':<10} {'適應度':<10} {'收益(%)':<10} {'勝率(%)':<10} {'夏普比率':<10}")
    print("-" * 80)
    
    for mode_code in ['ultra_fast', 'fast', 'balanced', 'quality']:
        if mode_code in results:
            r = results[mode_code]
            if 'error' not in r:
                print(f"{r['name']:<15} {r['time']:<10.1f} {r['fitness']:<10.4f} "
                      f"{r['profit']:<10.2f} {r['win_rate']*100:<10.1f} {r['sharpe']:<10.4f}")
            else:
                print(f"{r['name']:<15} {'錯誤':<10} {r['error']}")
    
    print("\n💡 建議:")
    if 'fast' in results and 'error' not in results['fast']:
        fast_time = results['fast']['time']
        print(f"🚀 快速模式 ({fast_time:.1f}秒) 適合日常使用")
        
        if 'ultra_fast' in results and 'error' not in results['ultra_fast']:
            ultra_time = results['ultra_fast']['time']
            speedup = fast_time / ultra_time
            print(f"⚡ 超高速模式比快速模式快 {speedup:.1f} 倍")
    
    # 計算批次處理時間預估
    print(f"\n📊 49檔股票批次處理時間預估:")
    for mode_code in ['ultra_fast', 'fast', 'balanced', 'quality']:
        if mode_code in results and 'error' not in results[mode_code]:
            single_time = results[mode_code]['time']
            batch_time = single_time * 49 / 60  # 轉換為分鐘
            parallel_time = batch_time / 4  # 假設4核並行
            
            print(f"  {results[mode_code]['name']:<15}: "
                  f"串行 {batch_time:.0f}分鐘, 並行 {parallel_time:.0f}分鐘")

def demo_batch_processing():
    """演示批次處理的樣本"""
    print("\n🎯 批次處理演示 (處理3檔股票)")
    print("=" * 50)
    
    # 從49檔指定股票中選3檔做演示
    demo_stocks = ['台積電', '鴻海', '聯發科']
    
    from fast_batch_optimizer import optimize_specific_stocks_fast
    
    # 先模擬檢查可用股票
    print("🔍 檢查演示股票可用性...")
    db = DBConnector()
    all_tables = db.get_all_stock_tables()
    
    available_demo = []
    for table in all_tables:
        for stock in demo_stocks:
            if stock in table:
                available_demo.append((stock, table))
                break
    
    print(f"✅ 找到 {len(available_demo)} 檔可用於演示:")
    for stock, table in available_demo:
        print(f"   • {stock} -> {table}")
    
    if len(available_demo) >= 1:
        print(f"\n🚀 使用快速模式處理 {len(available_demo)} 檔股票...")
        
        # 這裡可以添加實際的批次處理演示
        # 但為了不影響真實資料，僅顯示預期效果
        
        estimated_time = len(available_demo) * 60  # 每檔1分鐘
        parallel_time = estimated_time / min(4, len(available_demo))
        
        print(f"📊 預估處理時間:")
        print(f"   串行處理: {estimated_time/60:.1f} 分鐘")
        print(f"   並行處理: {parallel_time/60:.1f} 分鐘")
        print(f"   加速比: {estimated_time/parallel_time:.1f}x")
    
    print("\n💡 要執行完整的49檔批次處理，請運行:")
    print("   python fast_batch_optimizer.py")

if __name__ == "__main__":
    print("🧪 加速優化分析演示程式")
    print("\n選擇演示:")
    print("1. 單一股票速度比較")
    print("2. 批次處理演示")
    print("3. 全部演示")
    print("4. 退出")
    
    while True:
        try:
            choice = input("\n請選擇 (1-4): ").strip()
            
            if choice == "1":
                demo_speed_comparison()
                break
            elif choice == "2":
                demo_batch_processing()
                break  
            elif choice == "3":
                demo_speed_comparison()
                demo_batch_processing()
                break
            elif choice == "4":
                print("👋 再見！")
                break
            else:
                print("❌ 無效選擇，請輸入 1-4")
                
        except KeyboardInterrupt:
            print("\n\n👋 用戶中斷")
            break
        except Exception as e:
            print(f"\n❌ 錯誤: {str(e)}")
