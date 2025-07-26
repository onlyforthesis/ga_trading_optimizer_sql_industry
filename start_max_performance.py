#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 電腦最大效能啟動器
讓您的電腦發揮最大效能跑數據分析！
"""

import os
import sys
import time
import multiprocessing as mp

def setup_max_performance():
    """設定最大效能環境"""
    print("🚀 正在設定最大效能環境...")
    
    # 獲取系統資源
    cpu_count = mp.cpu_count()
    
    # 設定最佳環境變數
    performance_vars = {
        'OMP_NUM_THREADS': str(cpu_count),
        'NUMBA_NUM_THREADS': str(cpu_count),
        'MKL_NUM_THREADS': str(cpu_count),
        'OPENBLAS_NUM_THREADS': str(cpu_count),
        'PYTHONHASHSEED': '0',
        'NUMBA_THREADING_LAYER': 'workqueue'
    }
    
    for key, value in performance_vars.items():
        os.environ[key] = value
        print(f"   {key} = {value}")
    
    print(f"✅ 環境設定完成，將使用 {cpu_count} 個 CPU 核心")
    
    return cpu_count

def show_system_info():
    """顯示系統資訊"""
    print("\n📊 系統資訊:")
    print(f"   Python 版本: {sys.version.split()[0]}")
    print(f"   作業系統: {sys.platform}")
    
    try:
        import psutil
        memory_gb = psutil.virtual_memory().total / (1024**3)
        available_gb = psutil.virtual_memory().available / (1024**3)
        print(f"   總記憶體: {memory_gb:.1f} GB")
        print(f"   可用記憶體: {available_gb:.1f} GB")
        
        # 估算處理時間
        cpu_count = mp.cpu_count()
        if cpu_count >= 16 and memory_gb >= 32:
            time_estimate = "3-5 分鐘"
        elif cpu_count >= 8 and memory_gb >= 16:
            time_estimate = "8-15 分鐘"
        else:
            time_estimate = "15-30 分鐘"
        
        print(f"   預估處理時間: {time_estimate}")
        
    except ImportError:
        print("   (無法取得詳細記憶體資訊)")

def run_ultra_performance_batch():
    """執行超高效能批次處理"""
    print("\n🔥 啟動超高效能批次處理...")
    print("=" * 50)
    
    try:
        # 檢查必要檔案
        required_files = [
            'ultra_performance_batch.py',
            'fast_ga_optimizer.py',
            'db_connector.py'
        ]
        
        missing_files = []
        for file in required_files:
            if not os.path.exists(file):
                missing_files.append(file)
        
        if missing_files:
            print(f"❌ 缺少必要檔案: {', '.join(missing_files)}")
            return False
        
        # 導入並執行批次處理
        print("📁 正在載入批次處理模組...")
        from ultra_performance_batch import main as ultra_main
        
        start_time = time.time()
        print(f"⏰ 開始時間: {time.strftime('%H:%M:%S')}")
        
        # 執行批次處理
        result = ultra_main()
        
        end_time = time.time()
        elapsed_minutes = (end_time - start_time) / 60
        
        print("\n" + "=" * 50)
        print("🎉 批次處理完成！")
        print(f"⏰ 結束時間: {time.strftime('%H:%M:%S')}")
        print(f"⚡ 總耗時: {elapsed_minutes:.1f} 分鐘")
        
        if elapsed_minutes > 0:
            speed = 49 / elapsed_minutes  # 假設處理 49 檔股票
            print(f"🚀 處理速度: {speed:.1f} 檔/分鐘")
        
        return True
        
    except ImportError as e:
        print(f"❌ 無法導入批次處理模組: {e}")
        print("\n💡 解決方案:")
        print("   1. 確保 ultra_performance_batch.py 檔案存在")
        print("   2. 檢查相關模組是否正確安裝")
        return False
        
    except Exception as e:
        print(f"❌ 執行過程發生錯誤: {e}")
        print("\n🔧 請檢查:")
        print("   1. 資料庫連接是否正常")
        print("   2. 股票代碼清單是否正確")
        print("   3. 系統資源是否充足")
        return False

def show_performance_tips():
    """顯示效能優化建議"""
    print("\n💡 最大效能使用建議:")
    print("   🔸 關閉不必要的應用程式")
    print("   🔸 確保電源設定為「高效能」模式")
    print("   🔸 建議使用 SSD 硬碟")
    print("   🔸 確保散熱良好，避免降頻")
    print("   🔸 如果可能，增加更多記憶體")

def main():
    """主程式"""
    print("🚀 電腦最大效能股票分析啟動器")
    print("讓您的電腦發揮最大效能跑數據！")
    print("=" * 50)
    
    # 設定最大效能環境
    cpu_count = setup_max_performance()
    
    # 顯示系統資訊
    show_system_info()
    
    # 顯示效能建議
    show_performance_tips()
    
    print("\n" + "=" * 50)
    print("🎯 準備開始 49 檔重點股票的超高速批次分析")
    print("   這將使用您電腦的所有 CPU 核心進行並行處理")
    print("   請確保電腦處於良好狀態並有足夠電力")
    
    # 等待用戶確認
    print("\n🤔 是否開始超高效能批次處理？")
    response = input("   請輸入 'y' 開始，或按 Enter 取消: ").strip().lower()
    
    if response in ['y', 'yes', '是']:
        print("\n🚀 開始處理，請稍候...")
        
        success = run_ultra_performance_batch()
        
        if success:
            print("\n🎊 所有分析完成！")
            print("📁 請檢查輸出檔案獲取詳細結果")
            print("📈 建議檢查 best_params 資料表查看最佳參數")
        else:
            print("\n😓 處理過程遇到問題")
            print("🔧 請檢查錯誤訊息並重試")
    else:
        print("\n👋 已取消，隨時可以重新執行此腳本")

if __name__ == "__main__":
    main()
