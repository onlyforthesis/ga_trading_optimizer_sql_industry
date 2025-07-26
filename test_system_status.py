#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 系統狀態功能測試腳本
"""

import sys
import os

# 添加當前目錄到路徑
sys.path.append(os.getcwd())

def test_system_status():
    """測試系統狀態功能"""
    print("🔍 測試系統狀態功能")
    print("=" * 50)
    
    try:
        # 測試資料庫連接
        from db_connector import DatabaseConnector
        db_obj = DatabaseConnector()
        
        print("✅ 資料庫連接測試:")
        if db_obj.connection:
            print("   • 資料庫連接成功")
        else:
            print("   • 資料庫連接失敗")
        
        # 測試基本系統狀態
        print("\n🖥️ 測試基本系統狀態:")
        from full_gui import get_database_status
        db_status = get_database_status(db_obj)
        print("   • 資料庫狀態獲取:", "成功" if db_status else "失敗")
        
        # 測試增強系統狀態
        print("\n🔧 測試增強系統狀態:")
        from full_gui import get_enhanced_system_status
        enhanced_status = get_enhanced_system_status(db_obj)
        print("   • 增強狀態獲取:", "成功" if enhanced_status else "失敗")
        
        # 測試 psutil
        print("\n💻 測試硬體監控模組:")
        try:
            import psutil
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            print(f"   • CPU 使用率: {cpu_percent}%")
            print(f"   • 記憶體使用率: {memory.percent}%")
            print(f"   • 記憶體總量: {round(memory.total / (1024**3), 2)} GB")
            print("   • psutil 模組: ✅ 正常")
        except ImportError:
            print("   • psutil 模組: ❌ 未安裝")
        except Exception as e:
            print(f"   • psutil 模組: ❌ 錯誤: {e}")
        
        # 測試平台資訊
        print("\n🏛️ 測試平台資訊:")
        try:
            import platform
            print(f"   • 作業系統: {platform.system()}")
            print(f"   • 版本: {platform.release()}")
            print(f"   • 架構: {platform.architecture()[0]}")
            print("   • platform 模組: ✅ 正常")
        except Exception as e:
            print(f"   • platform 模組: ❌ 錯誤: {e}")
        
        # 顯示部分增強狀態內容
        print("\n📋 系統狀態預覽:")
        print("-" * 30)
        preview = enhanced_status[:500] + "..." if len(enhanced_status) > 500 else enhanced_status
        print(preview)
        
        print("\n🎉 系統狀態功能測試完成!")
        
    except ImportError as e:
        print(f"❌ 匯入錯誤: {e}")
    except Exception as e:
        print(f"❌ 測試錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_system_status()
