#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 一鍵最大效能啟動器
自動偵測系統配置，設定最佳環境變數，並啟動超高性能批次處理
"""

import os
import sys
import time
import psutil
import multiprocessing as mp
from pathlib import Path

class MaxPerformanceLauncher:
    def __init__(self):
        self.cpu_count = mp.cpu_count()
        self.memory_gb = psutil.virtual_memory().total / (1024**3)
        self.available_memory = psutil.virtual_memory().available / (1024**3)
        
    def setup_environment(self):
        """設定最佳環境變數"""
        print("🔧 正在設定最佳環境變數...")
        
        # CPU 優化
        os.environ['OMP_NUM_THREADS'] = str(self.cpu_count)
        os.environ['NUMBA_NUM_THREADS'] = str(self.cpu_count)
        os.environ['MKL_NUM_THREADS'] = str(self.cpu_count)
        os.environ['OPENBLAS_NUM_THREADS'] = str(self.cpu_count)
        os.environ['VECLIB_MAXIMUM_THREADS'] = str(self.cpu_count)
        
        # 記憶體優化
        os.environ['PYTHONHASHSEED'] = '0'
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        
        # Numba 優化
        os.environ['NUMBA_THREADING_LAYER'] = 'workqueue'
        os.environ['NUMBA_NUM_THREADS'] = str(self.cpu_count)
        
        # MKL 優化（如果使用 Intel MKL）
        os.environ['MKL_DYNAMIC'] = 'FALSE'
        os.environ['MKL_NUM_THREADS'] = str(self.cpu_count)
        
        print(f"✅ 環境變數設定完成:")
        print(f"   - CPU 核心數: {self.cpu_count}")
        print(f"   - 總記憶體: {self.memory_gb:.1f} GB")
        print(f"   - 可用記憶體: {self.available_memory:.1f} GB")
        
    def check_system_resources(self):
        """檢查系統資源並給出建議"""
        print("\n🔍 系統資源檢查...")
        
        # CPU 檢查
        if self.cpu_count >= 12:
            cpu_status = "🔥 優秀"
        elif self.cpu_count >= 8:
            cpu_status = "✅ 良好"
        elif self.cpu_count >= 4:
            cpu_status = "⚠️ 可用"
        else:
            cpu_status = "❌ 不足"
            
        # 記憶體檢查
        if self.memory_gb >= 32:
            memory_status = "🔥 優秀"
        elif self.memory_gb >= 16:
            memory_status = "✅ 良好"
        elif self.memory_gb >= 8:
            memory_status = "⚠️ 可用"
        else:
            memory_status = "❌ 不足"
            
        print(f"   CPU: {self.cpu_count} 核心 - {cpu_status}")
        print(f"   記憶體: {self.memory_gb:.1f} GB - {memory_status}")
        
        # 磁碟檢查
        disk_usage = psutil.disk_usage('.')
        free_gb = disk_usage.free / (1024**3)
        print(f"   可用磁碟空間: {free_gb:.1f} GB")
        
        # 效能預估
        estimated_time = self.estimate_processing_time()
        print(f"\n⏱️ 預估處理時間 (49檔股票): {estimated_time}")
        
    def estimate_processing_time(self):
        """估算處理時間"""
        # 基於系統配置估算
        if self.cpu_count >= 16 and self.memory_gb >= 32:
            return "3-5 分鐘 🚀"
        elif self.cpu_count >= 12 and self.memory_gb >= 24:
            return "5-8 分鐘 ⚡"
        elif self.cpu_count >= 8 and self.memory_gb >= 16:
            return "8-12 分鐘 ✅"
        elif self.cpu_count >= 6 and self.memory_gb >= 12:
            return "12-20 分鐘 ⚠️"
        else:
            return "20-40 分鐘 ⏳"
    
    def optimize_python_process(self):
        """優化 Python 進程"""
        print("\n🐍 正在優化 Python 執行環境...")
        
        try:
            # 設定進程優先級（Windows）
            if sys.platform == "win32":
                import subprocess
                pid = os.getpid()
                subprocess.run(['wmic', 'process', 'where', f'processid={pid}', 
                              'CALL', 'setpriority', '128'], 
                              capture_output=True, text=True)
                print("   ✅ 設定為高優先級進程")
        except Exception as e:
            print(f"   ⚠️ 無法設定進程優先級: {e}")
            
        # 預熱 numba
        try:
            import numba
            print("   ✅ Numba JIT 編譯器已載入")
        except ImportError:
            print("   ⚠️ 建議安裝 numba 提升性能: pip install numba")
            
        # 檢查 Intel MKL
        try:
            import numpy as np
            if 'mkl' in np.__config__.show().lower():
                print("   ✅ 使用 Intel MKL 優化")
            else:
                print("   ⚠️ 建議使用 Intel MKL 版本的 numpy")
        except:
            pass
    
    def launch_ultra_performance_batch(self):
        """啟動超高性能批次處理"""
        print("\n🚀 正在啟動超高性能批次處理...")
        print("=" * 60)
        
        try:
            # 導入並運行超高性能批次處理器
            from ultra_performance_batch import UltraPerformanceBatch
            
            # 創建處理器實例
            batch_processor = UltraPerformanceBatch(
                max_workers=self.cpu_count,
                memory_limit_gb=int(self.available_memory * 0.8)  # 使用 80% 可用記憶體
            )
            
            # 開始處理
            start_time = time.time()
            results = batch_processor.run_batch_optimization()
            end_time = time.time()
            
            # 顯示結果
            print("\n" + "=" * 60)
            print("🎉 批次處理完成！")
            print(f"⏱️ 總耗時: {(end_time - start_time)/60:.1f} 分鐘")
            print(f"📊 處理結果: {len(results)} 檔股票")
            print(f"⚡ 平均速度: {len(results)/((end_time - start_time)/60):.1f} 檔/分鐘")
            
            return results
            
        except ImportError as e:
            print(f"❌ 無法導入超高性能批次處理器: {e}")
            print("請確保 ultra_performance_batch.py 存在且可導入")
            return None
        except Exception as e:
            print(f"❌ 執行過程中發生錯誤: {e}")
            return None
    
    def show_performance_tips(self):
        """顯示性能優化提示"""
        print("\n💡 性能優化提示:")
        
        tips = []
        
        if self.cpu_count < 8:
            tips.append("• 考慮升級至更多核心的處理器")
            
        if self.memory_gb < 16:
            tips.append("• 建議增加記憶體至 16GB 以上")
            
        if self.available_memory < 8:
            tips.append("• 關閉不必要的程式釋放記憶體")
            
        # 檢查是否有 SSD
        try:
            disk_io = psutil.disk_io_counters()
            if disk_io.read_time > disk_io.write_time * 2:
                tips.append("• 考慮使用 SSD 提升 I/O 性能")
        except:
            pass
            
        if not tips:
            tips.append("🔥 您的系統配置很棒，準備享受極速處理！")
            
        for tip in tips:
            print(f"   {tip}")

def main():
    """主函數"""
    print("🚀 最大效能啟動器")
    print("=" * 60)
    
    # 創建啟動器
    launcher = MaxPerformanceLauncher()
    
    # 設定環境
    launcher.setup_environment()
    
    # 檢查系統
    launcher.check_system_resources()
    
    # 優化 Python
    launcher.optimize_python_process()
    
    # 顯示提示
    launcher.show_performance_tips()
    
    # 詢問是否開始
    print("\n" + "=" * 60)
    response = input("🤔 是否開始超高性能批次處理？(y/n): ").strip().lower()
    
    if response in ['y', 'yes', '是', '']:
        # 啟動批次處理
        results = launcher.launch_ultra_performance_batch()
        
        if results:
            print("\n🎊 所有處理完成！檢查輸出文件查看詳細結果。")
        else:
            print("\n😅 處理過程中遇到問題，請檢查錯誤訊息。")
    else:
        print("\n👋 下次見！您可以隨時運行此腳本開始處理。")

if __name__ == "__main__":
    main()
