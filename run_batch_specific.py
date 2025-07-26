"""
簡單的指定股票批次處理執行器
可以直接運行這個腳本來處理49檔指定股票
"""

import sys
import time
from batch_specific_stocks import optimize_specific_stocks, check_available_stocks

def main():
    print("=" * 70)
    print("🎯 指定股票批次優化工具")
    print("=" * 70)
    print("將處理以下49檔重點股票:")
    print("台積電、鴻海、聯發科、台達電、廣達、富邦金、國泰金、中信金、兆豐金、玉山金")
    print("台塑、南亞、統一、台泥、亞泥、華新、日月光投控、華碩、聯詠、和碩")
    print("元大金、中鋼、開發金、大成、中租-KY、遠東新、台塑化、研華、華南金、台新金")
    print("新光金、台灣大、豐泰、合庫金、寶成、和泰車、大聯大、陽明、萬海、永豐餘")
    print("統一超、國票金、卜蜂、美利達、南電、中保科、上海商銀、緯創、第一金")
    print("=" * 70)
    print()
    
    print("請選擇操作:")
    print("1. 檢查哪些股票在資料庫中可用")
    print("2. 開始批次優化處理")
    print("3. 退出")
    print()
    
    while True:
        try:
            choice = input("請輸入選擇 (1/2/3): ").strip()
            
            if choice == "1":
                print("\n🔍 正在檢查股票可用性...")
                result = check_available_stocks()
                print(result)
                print("\n" + "=" * 50)
                
            elif choice == "2":
                print("\n⚠️  注意：批次優化可能需要較長時間（每檔股票約5分鐘）")
                confirm = input("確定要開始批次優化嗎？(y/N): ").strip().lower()
                
                if confirm in ['y', 'yes', '是']:
                    print("\n🚀 開始批次優化處理...")
                    start_time = time.time()
                    
                    try:
                        result = optimize_specific_stocks()
                        print(result)
                        
                        end_time = time.time()
                        elapsed = (end_time - start_time) / 60
                        print(f"\n⏱️  總執行時間: {elapsed:.1f} 分鐘")
                        
                    except KeyboardInterrupt:
                        print("\n\n⚠️  用戶中斷了批次處理")
                    except Exception as e:
                        print(f"\n❌ 批次處理發生錯誤: {str(e)}")
                else:
                    print("❌ 已取消批次優化")
                
                print("\n" + "=" * 50)
                
            elif choice == "3":
                print("👋 再見！")
                break
                
            else:
                print("❌ 無效選擇，請輸入 1、2 或 3")
                
        except KeyboardInterrupt:
            print("\n\n👋 用戶中斷，程式結束")
            break
        except Exception as e:
            print(f"\n❌ 發生錯誤: {str(e)}")

if __name__ == "__main__":
    main()
