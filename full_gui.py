import gradio as gr
import pandas as pd
import numpy as np
import os
import sys

def test_and_import_modules():
    """測試並導入所有必要的模組"""
    try:
        # 測試基礎模組
        import pyodbc
        import matplotlib.pyplot as plt
        
        # 測試自定義模組
        from db_connector import DBConnector
        from ga_optimizer import GeneticAlgorithm, TradingParameters, TradingResult
        from report_generator import save_evolution_plot
        
        # 嘗試導入買進持有分析模組
        try:
            from buy_hold_analysis import analyze_multiple_periods
        except ImportError:
            print("⚠️ 買進持有分析模組未找到，部分功能將不可用")
        
        # 嘗試連接資料庫
        db = DBConnector()
        industries = db.get_industry_list()
        
        return True, f"✅ 所有模組載入成功！資料庫連接正常，找到 {len(industries)} 個產業", industries, db
        
    except ImportError as e:
        return False, f"❌ 模組導入失敗: {e}", [], None
    except Exception as e:
        return False, f"❌ 資料庫連接失敗: {e}", [], None

def get_stocks_for_industry(industry, db_obj):
    """獲取產業的股票列表"""
    if not db_obj or industry == "請選擇產業":
        return gr.Dropdown(choices=[], value=None)
    
    try:
        stocks = db_obj.get_stocks_by_industry(industry)
        if stocks:
            return gr.Dropdown(choices=stocks, value=stocks[0], label="選擇股票 (格式: 代碼+名稱)")
        else:
            return gr.Dropdown(choices=[], value=None, label="該產業無股票資料")
    except Exception as e:
        return gr.Dropdown(choices=[f"錯誤: {str(e)}"], value=None)

def run_full_ga_analysis(stock_name, db_obj, progress=gr.Progress()):
    """執行完整的基因演算法分析"""
    if not db_obj:
        return "❌ 資料庫未連接", None
    
    if not stock_name or "請" in stock_name or "錯誤" in stock_name:
        return "⚠️ 請選擇有效的股票", None
    
    try:
        progress(0, desc="載入股票數據...")
        
        # 載入股票數據
        print(f"🔍 開始載入股票資料: {stock_name}")
        data = db_obj.read_stock_data(stock_name)
        if data.empty:
            print(f"❌ 股票 {stock_name} 無數據")
            return f"❌ 股票 {stock_name} 無數據", None
        
        print(f"✅ 成功載入資料: {len(data)} 筆")
        print(f"📊 資料概覽:\n{data.head()}")
        
        progress(0.1, desc="準備分析參數...")
        
        # 獲取股票資訊
        stock_code = db_obj.extract_stock_code_from_table_name(stock_name)
        info = db_obj.get_stock_info(stock_code)
        industry = info['Industry'] if info else "未知"
        stock_display_name = info['StockName'] if info else "未知"
        
        progress(0.2, desc="初始化基因演算法...")
        
        # 導入基因演算法模組
        from ga_optimizer import GeneticAlgorithm
        from report_generator import save_evolution_plot
        
        # 固定參數設定
        generations = 50
        population_size = 50
        
        # 智能停止條件設定
        max_time_minutes = 5.0  # 最大執行時間（分鐘）
        convergence_threshold = 0.001  # 收斂閾值
        convergence_generations = 8  # 判斷收斂的世代數
        
        # 初始化基因演算法（帶智能停止條件）
        print(f"🔍 開始分析股票: {stock_name}")
        print(f"📊 原始資料形狀: {data.shape}")
        print(f"📊 資料欄位: {list(data.columns)}")
        
        ga = GeneticAlgorithm(
            data=data, 
            population_size=population_size, 
            generations=generations,
            mutation_rate=0.1,
            crossover_rate=0.8,
            max_time_minutes=max_time_minutes,
            convergence_threshold=convergence_threshold,
            convergence_generations=convergence_generations
        )
        
        progress(0.3, desc="開始基因演算法演化...")
        
        # 執行演化過程
        print("🧬 開始基因演算法演化...")
        best_result = ga.evolve()
        print(f"✅ 演化完成，最佳適應度: {best_result.fitness}")
        
        progress(0.8, desc="生成分析圖表...")
        
        # 生成演化過程圖表
        os.makedirs("outputs", exist_ok=True)
        save_evolution_plot(ga.best_fitness_history, ga.avg_fitness_history)
        
        progress(0.9, desc="保存最佳參數...")
        
        # 保存最佳參數到資料庫
        db_obj.save_best_params(stock_name, best_result, industry)
        
        progress(1.0, desc="分析完成！")
        
        # 計算買進持有策略報酬
        buy_hold_return = calculate_buy_and_hold_return(db_obj, stock_name)
        
        # 格式化結果
        train_data_info = f"訓練數據: {len(ga.train_data)} 筆 (2019-2023)"
        test_data_info = f"測試數據: {len(ga.test_data)} 筆 (2024)" if not ga.test_data.empty else "測試數據: 無"
        
        result_text = f"""🎉 基因演算法分析完成！

📊 **股票資訊**
股票名稱: {stock_display_name}
所屬產業: {industry}
買進持有策略報酬: {buy_hold_return}
總資料筆數: {len(data)} 筆
{train_data_info}
{test_data_info}

⚙️ **演算法參數與智能停止條件**
最大世代數: {generations}
族群大小: {population_size}
突變率: 0.1
交配率: 0.8
時間限制: {max_time_minutes} 分鐘
收斂閾值: {convergence_threshold}
收斂判斷世代: {convergence_generations}

🛑 **停止條件結果**
停止原因: {ga.stop_reason}
實際執行世代: {len(ga.best_fitness_history)}

📈 **訓練數據結果 (2019-2023)**
適應度: {best_result.fitness:.4f}
總利潤: ${best_result.total_profit:,.2f}
勝率: {best_result.win_rate:.1%}
最大回撤: {best_result.max_drawdown:.1%}
夏普比率: {best_result.sharpe_ratio:.4f}"""

        # 添加測試結果（如果有的話）
        if hasattr(best_result, 'test_result') and best_result.test_result:
            test_result = best_result.test_result
            result_text += f"""

🧪 **測試數據結果 (2024)**
適應度: {test_result.fitness:.4f}
總利潤: ${test_result.total_profit:,.2f}
勝率: {test_result.win_rate:.1%}
最大回撤: {test_result.max_drawdown:.1%}
夏普比率: {test_result.sharpe_ratio:.4f}

📊 **模型泛化性分析**
適應度差異: {best_result.fitness - test_result.fitness:.4f}
利潤差異: ${best_result.total_profit - test_result.total_profit:,.2f}
勝率差異: {(best_result.win_rate - test_result.win_rate)*100:.1f}%
泛化評估: {'✅ 良好' if abs(best_result.fitness - test_result.fitness) < 2.0 else '⚠️ 需注意'}"""

        result_text += f"""

🔧 **最佳交易參數**
區間數: {best_result.parameters.m_intervals}
持有天數: {best_result.parameters.hold_days}
目標利潤比例: {best_result.parameters.target_profit_ratio*100:.2f}%
門檻α: {best_result.parameters.alpha:.1f}%

✅ 結果已保存至資料庫！
"""
        
        return result_text, "outputs/evolution.png"
        
    except Exception as e:
        return f"❌ 分析過程發生錯誤: {str(e)}", None

def run_batch_analysis(industry, db_obj):
    """批次分析整個產業"""
    if not db_obj:
        return "❌ 資料庫未連接，無法執行批次分析"
    
    try:
        from multi_stock_optimizer import optimize_by_industry, optimize_all_stocks
        
        if industry == "全部":
            return optimize_all_stocks()
        else:
            return optimize_by_industry(industry)
    except ImportError:
        return "❌ 批次分析模組未找到"
    except Exception as e:
        return f"❌ 批次分析錯誤: {str(e)}"

def run_specific_stocks_batch(action_type, db_obj):
    """批次分析指定的49檔股票"""
    if not db_obj:
        return "❌ 資料庫未連接，無法執行批次分析"
    
    try:
        from batch_specific_stocks import optimize_specific_stocks, check_available_stocks
        
        if action_type == "檢查可用股票":
            return check_available_stocks()
        elif action_type == "開始批次優化":
            return optimize_specific_stocks()
        else:
            return "❌ 無效的操作類型"
    except ImportError:
        return "❌ 指定股票批次分析模組未找到"
    except Exception as e:
        return f"❌ 指定股票批次分析錯誤: {str(e)}"

def run_fast_batch_optimization(speed_mode, use_parallel, db_obj):
    """執行快速批次優化"""
    if not db_obj:
        return "❌ 資料庫未連接，無法執行快速批次優化"
    
    try:
        from fast_batch_optimizer import optimize_specific_stocks_fast
        
        max_workers = 4 if use_parallel else 1
        return optimize_specific_stocks_fast(
            speed_mode=speed_mode, 
            max_workers=max_workers, 
            use_multiprocessing=use_parallel
        )
    except ImportError:
        return "❌ 快速批次優化模組未找到"
    except Exception as e:
        return f"❌ 快速批次優化錯誤: {str(e)}"

def run_fast_single_analysis(stock_name, speed_mode, db_obj):
    """執行快速單一股票分析"""
    if not db_obj:
        return "❌ 資料庫未連接", None
    
    if not stock_name or "請" in stock_name or "錯誤" in stock_name:
        return "⚠️ 請選擇有效的股票", None
    
    try:
        from fast_ga_optimizer import fast_optimize
        from report_generator import save_evolution_plot
        import os
        
        # 載入股票數據
        data = db_obj.read_stock_data(stock_name)
        if data.empty:
            return f"❌ 股票 {stock_name} 無數據", None
        
        # 獲取股票資訊
        stock_code = db_obj.extract_stock_code_from_table_name(stock_name)
        info = db_obj.get_stock_info(stock_code)
        industry = info['Industry'] if info else "未知"
        stock_display_name = info['StockName'] if info else "未知"
        
        # 快速優化
        print(f"🚀 啟動快速優化: {stock_name} (模式: {speed_mode})")
        import time
        start_time = time.time()
        
        best_result = fast_optimize(data, speed_mode)
        
        elapsed_time = time.time() - start_time
        
        # 保存結果
        db_obj.save_best_params(stock_name, best_result, industry)
        
        # 生成結果報告
        # 計算買進持有策略報酬
        buy_hold_return = calculate_buy_and_hold_return(db_obj, stock_name)
        
        speed_info = {
            'ultra_fast': '⚡ 超高速模式',
            'fast': '🚀 快速模式',
            'balanced': '⚖️ 平衡模式',
            'quality': '🎯 品質模式'
        }
        
        result_text = f"""🚀 快速分析完成！

📊 **股票資訊**
股票名稱: {stock_display_name}
所屬產業: {industry}
買進持有策略報酬: {buy_hold_return}
總資料筆數: {len(data)} 筆

⚡ **快速優化設定**
優化模式: {speed_info.get(speed_mode, speed_mode)}
執行時間: {elapsed_time:.1f} 秒

📈 **最佳結果**
適應度: {best_result.fitness:.4f}
總利潤: {best_result.total_profit:.2f}%
勝率: {best_result.win_rate:.1%} 
最大回撤: {best_result.max_drawdown:.1%}
夏普比率: {best_result.sharpe_ratio:.4f}

🔧 **最佳交易參數**
區間數: {best_result.parameters.m_intervals}
持有天數: {best_result.parameters.hold_days}
目標利潤比例: {best_result.parameters.target_profit_ratio*100:.2f}%
門檻α: {best_result.parameters.alpha:.1f}%

✅ 結果已保存至資料庫！
"""
        
        return result_text, None
        
    except Exception as e:
        return f"❌ 快速分析錯誤: {str(e)}", None

def get_analysis_results(db_obj, industry_filter="全部"):
    """獲取所有分析結果並格式化為表格"""
    if not db_obj:
        return []
    
    try:
        # 確保 BestParameters 表存在
        db_obj.create_best_params_table()
        
        # 基本查詢
        if industry_filter == "全部":
            query = """
            SELECT 
                StockName,
                Industry,
                TotalProfit,
                TotalProfit as annual_return,
                MaxDrawdown,
                SharpeRatio,
                WinRate,
                CreateTime
            FROM BestParameters 
            ORDER BY CreateTime DESC
            """
        else:
            query = """
            SELECT 
                StockName,
                Industry,
                TotalProfit,
                TotalProfit as annual_return,
                MaxDrawdown,
                SharpeRatio,
                WinRate,
                CreateTime
            FROM BestParameters 
            WHERE Industry = ?
            ORDER BY CreateTime DESC
            """
        
        # 執行查詢
        if industry_filter == "全部":
            results = db_obj.execute_query(query)
        else:
            results = db_obj.execute_query(query, (industry_filter,))
        
        if not results:
            print("沒有找到分析結果，可能尚未進行任何分析")
            return []
        
        # 格式化結果
        formatted_results = []
        for row in results:
            stock_name = row[0]
            industry = row[1]
            total_profit = row[2] if row[2] is not None else 0
            annual_return = row[3] if row[3] is not None else 0
            max_drawdown = row[4] if row[4] is not None else 0
            sharpe_ratio = row[5] if row[5] is not None else 0
            win_rate = row[6] if row[6] is not None else 0
            
            # 計算買進持有策略報酬
            buy_hold_return = calculate_buy_and_hold_return(db_obj, stock_name)
            
            formatted_results.append([
                stock_name,  # 股票名稱
                buy_hold_return,  # 買進持有策略報酬
                f"{total_profit:.2f}%",  # 總報酬率
                f"{annual_return:.2f}%",  # 年化報酬率
                f"{max_drawdown:.2f}%",  # 最大回撤
                f"{sharpe_ratio:.4f}",  # 夏普比率
                f"{win_rate:.1f}%",  # 勝率
                industry  # 所屬產業
            ])
        
        return formatted_results
        
    except Exception as e:
        print(f"查詢分析結果錯誤: {e}")
        import traceback
        traceback.print_exc()
        return []

def calculate_buy_and_hold_return(db_obj, stock_name):
    """計算買進持有策略報酬"""
    try:
        # 從表名提取股票代號  
        stock_code = db_obj.extract_stock_code_from_table_name(stock_name)
        
        # 先嘗試使用英文欄位名
        try:
            # 獲取測試期間的數據 (2024年) - 使用英文欄位名，注意 Close 是保留字需要用方括號
            query = f"""
            SELECT TOP 1 [Close] as first_close
            FROM [{stock_name}]
            WHERE [Date] >= '2024-01-01'
            ORDER BY [Date] ASC
            """
            
            first_result = db_obj.execute_query(query)
            if not first_result or len(first_result) == 0:
                return "N/A"
            
            first_close = first_result[0][0]
            
            # 獲取最後一天的收盤價
            query = f"""
            SELECT TOP 1 [Close] as last_close
            FROM [{stock_name}]
            WHERE [Date] >= '2024-01-01'
            ORDER BY [Date] DESC
            """
            
            last_result = db_obj.execute_query(query)
            if not last_result or len(last_result) == 0:
                return "N/A"
            
            last_close = last_result[0][0]
            
        except:
            # 如果英文欄位名失敗，嘗試中文欄位名
            try:
                query = f"""
                SELECT TOP 1 [收盤價] as first_close
                FROM [{stock_name}]
                WHERE [日期] >= '2024-01-01'
                ORDER BY [日期] ASC
                """
                
                first_result = db_obj.execute_query(query)
                if not first_result or len(first_result) == 0:
                    return "N/A"
                
                first_close = first_result[0][0]
                
                # 獲取最後一天的收盤價
                query = f"""
                SELECT TOP 1 [收盤價] as last_close
                FROM [{stock_name}]
                WHERE [日期] >= '2024-01-01'
                ORDER BY [日期] DESC
                """
                
                last_result = db_obj.execute_query(query)
                if not last_result or len(last_result) == 0:
                    return "N/A"
                
                last_close = last_result[0][0]
                
            except:
                # 如果都失敗，嘗試檢查表格結構並使用實際的欄位名
                try:
                    # 查詢表格結構
                    schema_query = f"""
                    SELECT COLUMN_NAME 
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_NAME = '{stock_name}'
                    AND (COLUMN_NAME LIKE '%close%' OR COLUMN_NAME LIKE '%收盤%' OR COLUMN_NAME LIKE '%Close%')
                    """
                    
                    close_columns = db_obj.execute_query(schema_query)
                    
                    date_query = f"""
                    SELECT COLUMN_NAME 
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_NAME = '{stock_name}'
                    AND (COLUMN_NAME LIKE '%date%' OR COLUMN_NAME LIKE '%日期%' OR COLUMN_NAME LIKE '%Date%')
                    """
                    
                    date_columns = db_obj.execute_query(date_query)
                    
                    if close_columns and date_columns:
                        close_col = close_columns[0][0]
                        date_col = date_columns[0][0]
                        
                        # 使用檢測到的欄位名
                        query = f"""
                        SELECT TOP 1 [{close_col}] as first_close
                        FROM [{stock_name}]
                        WHERE [{date_col}] >= '2024-01-01'
                        ORDER BY [{date_col}] ASC
                        """
                        
                        first_result = db_obj.execute_query(query)
                        if not first_result or len(first_result) == 0:
                            return "N/A"
                        
                        first_close = first_result[0][0]
                        
                        query = f"""
                        SELECT TOP 1 [{close_col}] as last_close
                        FROM [{stock_name}]
                        WHERE [{date_col}] >= '2024-01-01'
                        ORDER BY [{date_col}] DESC
                        """
                        
                        last_result = db_obj.execute_query(query)
                        if not last_result or len(last_result) == 0:
                            return "N/A"
                        
                        last_close = last_result[0][0]
                    else:
                        return "N/A"
                except:
                    return "N/A"
        
        # 計算報酬率
        if first_close and last_close and first_close > 0:
            return_rate = (last_close - first_close) / first_close
            return f"{return_rate * 100:.2f}%"
        else:
            return "N/A"
            
    except Exception as e:
        print(f"計算買進持有報酬錯誤 ({stock_name}): {e}")
        return "N/A"

def get_database_status(db_obj):
    """獲取詳細的資料庫狀態"""
    if not db_obj:
        return """❌ 資料庫未連接

🔧 **故障排除步驟:**

1. **檢查 SQL Server 服務**
   - 開啟 Windows 服務管理員
   - 尋找 'SQL Server' 服務並確認運行中

2. **檢查資料庫連接設定**
   - 伺服器名稱: DESKTOP-TOB09L9
   - 資料庫名稱: StockDB
   - 認證: Windows 整合驗證

3. **檢查 ODBC 驅動程式**
   - 需要安裝 "ODBC Driver 17 for SQL Server"

4. **測試連接**
   - 使用 SQL Server Management Studio 測試連接

💡 如需修改連接設定，請編輯 db_connector.py 檔案"""
    
    try:
        industries = db_obj.get_industry_list()
        total_stocks = 0
        status_text = "✅ **資料庫連接成功**\n\n"
        status_text += f"📊 **總產業數:** {len(industries)}\n\n"
        
        for industry in industries:
            stocks = db_obj.get_stocks_by_industry(industry)
            total_stocks += len(stocks)
            status_text += f"• **{industry}:** {len(stocks)} 檔股票\n"
        
        status_text += f"\n📈 **總股票數:** {total_stocks}"
        status_text += f"\n🔄 **系統狀態:** 完整功能可用"
        return status_text
    except Exception as e:
        return f"❌ 讀取資料庫資訊失敗: {str(e)}"

def get_enhanced_system_status(db_obj):
    """獲取增強的系統狀態 (包含硬體資訊)"""
    try:
        import psutil
        import platform
        import sys
        import datetime
        import subprocess
        
        # 獲取資料庫狀態
        db_status = get_database_status(db_obj)
        
        # 獲取硬體狀態
        hardware_status = "\n" + "="*50 + "\n"
        hardware_status += "🖥️ **硬體系統資訊**\n\n"
        
        # 平台資訊
        hardware_status += "💻 **系統平台**\n"
        hardware_status += f"   • 作業系統: {platform.system()} {platform.release()}\n"
        hardware_status += f"   • 架構: {platform.architecture()[0]}\n"
        hardware_status += f"   • 處理器: {platform.processor()}\n"
        hardware_status += f"   • 電腦名稱: {platform.node()}\n"
        
        # 開機時間
        try:
            boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.datetime.now() - boot_time
            hardware_status += f"   • 開機時間: {boot_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            hardware_status += f"   • 運行時間: {str(uptime).split('.')[0]}\n"
        except:
            pass
        
        hardware_status += "\n"
        
        # CPU 資訊
        hardware_status += "🔥 **CPU 資訊**\n"
        try:
            cpu_count_physical = psutil.cpu_count(logical=False)
            cpu_count_logical = psutil.cpu_count(logical=True)
            cpu_percent = psutil.cpu_percent(interval=1)
            
            hardware_status += f"   • 物理核心: {cpu_count_physical}\n"
            hardware_status += f"   • 邏輯核心: {cpu_count_logical}\n"
            hardware_status += f"   • CPU 使用率: {cpu_percent}%\n"
            
            # CPU 頻率
            try:
                cpu_freq = psutil.cpu_freq()
                if cpu_freq:
                    hardware_status += f"   • 目前頻率: {cpu_freq.current:.0f} MHz\n"
                    hardware_status += f"   • 最大頻率: {cpu_freq.max:.0f} MHz\n"
            except:
                pass
        except Exception as e:
            hardware_status += f"   • CPU 資訊錯誤: {str(e)}\n"
        
        hardware_status += "\n"
        
        # 記憶體資訊
        hardware_status += "💾 **記憶體資訊**\n"
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            hardware_status += f"   • 總容量: {round(memory.total / (1024**3), 2)} GB\n"
            hardware_status += f"   • 已使用: {round(memory.used / (1024**3), 2)} GB ({memory.percent}%)\n"
            hardware_status += f"   • 可用: {round(memory.available / (1024**3), 2)} GB\n"
            hardware_status += f"   • 虛擬記憶體: {round(swap.used / (1024**3), 2)} / {round(swap.total / (1024**3), 2)} GB\n"
        except Exception as e:
            hardware_status += f"   • 記憶體資訊錯誤: {str(e)}\n"
        
        hardware_status += "\n"
        
        # GPU 資訊 (Windows)
        hardware_status += "🎮 **GPU 資訊**\n"
        try:
            if platform.system() == 'Windows':
                result = subprocess.run([
                    'wmic', 'path', 'win32_VideoController', 'get', 
                    'name,AdapterRAM', '/format:csv'
                ], capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')[1:]
                    gpu_found = False
                    
                    for i, line in enumerate(lines):
                        if line.strip():
                            parts = line.split(',')
                            if len(parts) >= 3:
                                name = parts[2] if len(parts) > 2 else 'Unknown'
                                memory = parts[1] if len(parts) > 1 else 'Unknown'
                                
                                if name != 'Unknown' and name.strip():
                                    hardware_status += f"   • GPU {i}: {name.strip()}\n"
                                    
                                    if memory != 'Unknown' and memory.strip():
                                        try:
                                            memory_gb = int(memory) / (1024**3)
                                            hardware_status += f"     - 記憶體: {memory_gb:.1f} GB\n"
                                        except:
                                            pass
                                    
                                    gpu_found = True
                    
                    if not gpu_found:
                        hardware_status += "   • 無法檢測到 GPU 資訊\n"
                else:
                    hardware_status += "   • GPU 檢測失敗\n"
            else:
                hardware_status += "   • 此平台不支援 GPU 檢測\n"
        except Exception as e:
            hardware_status += f"   • GPU 資訊錯誤: {str(e)}\n"
        
        hardware_status += "\n"
        
        # 磁碟資訊
        hardware_status += "💽 **磁碟資訊**\n"
        try:
            partitions = psutil.disk_partitions()
            for partition in partitions[:3]:  # 只顯示前3個分區
                try:
                    partition_usage = psutil.disk_usage(partition.mountpoint)
                    total_gb = round(partition_usage.total / (1024**3), 2)
                    used_gb = round(partition_usage.used / (1024**3), 2)
                    free_gb = round(partition_usage.free / (1024**3), 2)
                    usage_percent = round((partition_usage.used / partition_usage.total) * 100, 2)
                    
                    hardware_status += f"   • {partition.device} ({partition.fstype})\n"
                    hardware_status += f"     - 容量: {used_gb} / {total_gb} GB ({usage_percent}%)\n"
                    hardware_status += f"     - 可用: {free_gb} GB\n"
                except PermissionError:
                    continue
        except Exception as e:
            hardware_status += f"   • 磁碟資訊錯誤: {str(e)}\n"
        
        hardware_status += "\n"
        
        # Python 環境資訊
        hardware_status += "🐍 **Python 環境**\n"
        try:
            version_line = sys.version.split('\n')[0]
            hardware_status += f"   • 版本: {version_line}\n"
            hardware_status += f"   • 執行路徑: {sys.executable}\n"
            hardware_status += f"   • 已載入模組: {len(sys.modules)} 個\n"
        except Exception as e:
            hardware_status += f"   • Python 環境資訊錯誤: {str(e)}\n"
        
        # 結合資料
        combined_status = f"{db_status}\n{hardware_status}"
        
        return combined_status
        
    except ImportError as e:
        # 如果 psutil 不可用，只返回資料庫狀態
        return get_database_status(db_obj) + f"\n\n⚠️ 硬體監控模組未安裝: {str(e)}"
    except Exception as e:
        return f"{get_database_status(db_obj)}\n\n❌ 硬體監控錯誤: {str(e)}"

def create_full_interface():
    """創建完整功能的界面"""
    
    # 測試所有模組和資料庫連接
    modules_ok, status_message, industries, db_obj = test_and_import_modules()
    
    with gr.Blocks(title="基因演算法股票策略最佳化系統", theme=gr.themes.Soft()) as demo:
        if modules_ok:
            gr.Markdown("# 🚀 基因演算法股票策略最佳化系統")
            gr.Markdown(f"**✅ 系統狀態:** {status_message}")
            gr.Markdown("**📋 說明:** 選擇產業和股票，系統將執行完整的基因演算法分析 (世代數=50, 族群大小=50)")
        else:
            gr.Markdown("# ⚠️ 基因演算法股票策略最佳化系統 (系統錯誤)")
            gr.Markdown(f"**❌ 系統狀態:** {status_message}")
        
        with gr.Tab("🧬 基因演算法分析"):
            if modules_ok:
                with gr.Row():
                    with gr.Column(scale=1):
                        # 產業選擇
                        industry_choices = ["請選擇產業"] + industries
                        industry_dropdown = gr.Dropdown(
                            choices=industry_choices,
                            value="請選擇產業",
                            label="🏭 選擇產業"
                        )
                        
                        # 股票選擇
                        stock_dropdown = gr.Dropdown(
                            choices=[],
                            value=None,
                            label="📊 選擇股票"
                        )
                        
                        # 分析按鈕
                        analyze_btn = gr.Button(
                            "🧬 開始基因演算法分析", 
                            size="lg", 
                            variant="primary"
                        )
                    
                    with gr.Column(scale=1):
                        gr.Markdown("### ⚙️ 分析參數")
                        gr.Markdown("""
**🔒 固定參數設定:**
- 最大世代數: 50
- 族群大小: 50  
- 突變率: 0.1
- 交配率: 0.8

**🛑 智能停止條件:**
- ⏱️ 時間限制: 5 分鐘
- 📈 收斂閾值: 0.001
- 🔢 收斂判斷: 8 世代
- 🎯 自動停止: 達到任一條件即停止

**📊 訓練/測試分割:**
- 🏋️ 訓練期間: 2019-2023年
- 🧪 測試期間: 2024年
- 🎯 目標: 驗證模型泛化能力  
- 突變率: 0.1
- 交配率: 0.8

**🎯 優化目標:**
- 最大化總利潤
- 最大化勝率
- 最小化最大回撤
- 最大化夏普比率
""")
                
                # 結果顯示區域
                with gr.Row():
                    with gr.Column(scale=2):
                        result_textbox = gr.Textbox(
                            label="📋 分析結果", 
                            lines=20,
                            max_lines=25
                        )
                    with gr.Column(scale=1):
                        result_image = gr.Image(
                            label="📈 演化過程圖", 
                            type="filepath"
                        )
                
                # 事件處理
                def update_stocks(industry):
                    return get_stocks_for_industry(industry, db_obj)
                
                def run_analysis_with_progress(stock):
                    return run_full_ga_analysis(stock, db_obj)
                
                industry_dropdown.change(
                    update_stocks,
                    inputs=[industry_dropdown],
                    outputs=[stock_dropdown]
                )
                
                analyze_btn.click(
                    run_analysis_with_progress,
                    inputs=[stock_dropdown],
                    outputs=[result_textbox, result_image]
                )
                
            else:
                gr.Markdown("### ❌ 系統無法啟動")
                gr.Markdown("請檢查資料庫連接和模組安裝")

        with gr.Tab("⚡ 快速分析"):
            if modules_ok:
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("### 🚀 單一股票快速分析")
                        
                        # 產業和股票選擇
                        fast_industry_dropdown = gr.Dropdown(
                            choices=["請選擇產業"] + industries,
                            value="請選擇產業",
                            label="🏭 選擇產業"
                        )
                        fast_stock_dropdown = gr.Dropdown(
                            choices=[],
                            value=None,
                            label="📊 選擇股票"
                        )
                        
                        # 速度模式選擇
                        speed_mode_dropdown = gr.Dropdown(
                            choices=[
                                ("⚡ 超高速模式 (約30秒)", "ultra_fast"),
                                ("🚀 快速模式 (約1分鐘)", "fast"),
                                ("⚖️ 平衡模式 (約2分鐘)", "balanced"),
                                ("🎯 品質模式 (約3分鐘)", "quality")
                            ],
                            value="fast",
                            label="⚡ 選擇速度模式"
                        )
                        
                        fast_analyze_btn = gr.Button("⚡ 開始快速分析", size="lg", variant="primary")
                        fast_result_textbox = gr.Textbox(label="📊 快速分析結果", lines=15)
                        
                        def update_fast_stocks(industry):
                            return get_stocks_for_industry(industry, db_obj)
                        
                        def run_fast_analysis(stock, speed_mode):
                            return run_fast_single_analysis(stock, speed_mode, db_obj)
                        
                        fast_industry_dropdown.change(
                            update_fast_stocks,
                            inputs=[fast_industry_dropdown],
                            outputs=[fast_stock_dropdown]
                        )
                        
                        fast_analyze_btn.click(
                            run_fast_analysis,
                            inputs=[fast_stock_dropdown, speed_mode_dropdown],
                            outputs=[fast_result_textbox]
                        )
                    
                    with gr.Column():
                        gr.Markdown("### ⚡ 速度模式說明")
                        gr.Markdown("""
**⚡ 超高速模式 (ultra_fast)**
- ⏱️ 執行時間: ~30秒
- 🧬 族群大小: 20
- 🔄 世代數: 30
- 🎯 適用: 快速測試、初步評估

**🚀 快速模式 (fast)**
- ⏱️ 執行時間: ~1分鐘
- 🧬 族群大小: 30
- 🔄 世代數: 50
- 🎯 適用: 日常使用、快速決策

**⚖️ 平衡模式 (balanced)**
- ⏱️ 執行時間: ~2分鐘
- 🧬 族群大小: 40
- 🔄 世代數: 75
- 🎯 適用: 平衡速度與品質

**🎯 品質模式 (quality)**
- ⏱️ 執行時間: ~3分鐘
- 🧬 族群大小: 50
- 🔄 世代數: 100
- 🎯 適用: 高品質分析

**🚀 加速技術:**
- 並行適應度評估
- 自適應突變率
- 精英選擇策略
- 早期停止條件
- 智能收斂檢測
                        """)
            else:
                gr.Markdown("### ❌ 快速分析不可用")

        with gr.Tab("🔄 批次分析"):
            if modules_ok:
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("### 🏭 產業別批次分析")
                        batch_industry_choices = ["全部"] + industries
                        batch_industry_dropdown = gr.Dropdown(
                            choices=batch_industry_choices,
                            value="全部",
                            label="選擇批次分析的產業"
                        )
                        batch_result = gr.Textbox(label="📋 產業批次分析結果", lines=15)
                        batch_btn = gr.Button("🔄 開始產業批次分析", size="lg")
                        
                        def run_batch(industry):
                            return run_batch_analysis(industry, db_obj)
                        
                        batch_btn.click(
                            run_batch,
                            inputs=[batch_industry_dropdown],
                            outputs=[batch_result]
                        )
                    
                    with gr.Column():
                        gr.Markdown("### 🎯 指定股票批次分析")
                        gr.Markdown("分析以下49檔重點股票：")
                        gr.Markdown("""
                        **金融業：** 富邦金、國泰金、中信金、兆豐金、玉山金、元大金、開發金、華南金、台新金、新光金、合庫金、國票金、上海商銀、第一金
                        
                        **科技業：** 台積電、鴻海、聯發科、台達電、廣達、日月光投控、華碩、聯詠、和碩、研華、緯創
                        
                        **傳統產業：** 台塑、南亞、統一、台泥、亞泥、華新、中鋼、大成、中租-KY、遠東新、台塑化、台灣大、豐泰、寶成、和泰車、大聯大、陽明、萬海、永豐餘、統一超、卜蜂、美利達、南電、中保科
                        """)
                        
                        specific_action_dropdown = gr.Dropdown(
                            choices=["檢查可用股票", "開始批次優化"],
                            value="檢查可用股票",
                            label="選擇操作"
                        )
                        specific_result = gr.Textbox(label="📋 指定股票批次結果", lines=15)
                        specific_btn = gr.Button("🎯 執行指定股票批次", size="lg")
                        
                        def run_specific_batch(action):
                            return run_specific_stocks_batch(action, db_obj)
                        
                        specific_btn.click(
                            run_specific_batch,
                            inputs=[specific_action_dropdown],
                            outputs=[specific_result]
                        )
                
                # 添加快速批次處理區域
                gr.Markdown("---")
                gr.Markdown("### ⚡ 快速批次處理")
                
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("**🚀 指定股票快速批次優化**")
                        
                        batch_speed_dropdown = gr.Dropdown(
                            choices=[
                                ("⚡ 超高速批次 (總計約25分鐘)", "ultra_fast"),
                                ("🚀 快速批次 (總計約50分鐘)", "fast"),
                                ("⚖️ 平衡批次 (總計約1.5小時)", "balanced"),
                                ("🎯 品質批次 (總計約2.5小時)", "quality")
                            ],
                            value="fast",
                            label="選擇批次速度模式"
                        )
                        
                        use_parallel_checkbox = gr.Checkbox(
                            value=True,
                            label="🔄 啟用並行處理 (建議開啟)"
                        )
                        
                        fast_batch_result = gr.Textbox(label="📋 快速批次處理結果", lines=15)
                        fast_batch_btn = gr.Button("⚡ 開始快速批次優化", size="lg", variant="secondary")
                        
                        def run_fast_batch(speed_mode, use_parallel):
                            return run_fast_batch_optimization(speed_mode, use_parallel, db_obj)
                        
                        fast_batch_btn.click(
                            run_fast_batch,
                            inputs=[batch_speed_dropdown, use_parallel_checkbox],
                            outputs=[fast_batch_result]
                        )
                    
                    with gr.Column():
                        gr.Markdown("**⚡ 快速批次處理說明**")
                        gr.Markdown("""
**時間預估 (49檔股票):**
- ⚡ 超高速: ~25分鐘 (平均30秒/檔)
- 🚀 快速: ~50分鐘 (平均1分鐘/檔)  
- ⚖️ 平衡: ~1.5小時 (平均2分鐘/檔)
- 🎯 品質: ~2.5小時 (平均3分鐘/檔)

**🚀 加速技術:**
- 多進程並行處理
- 自適應參數優化
- 早期停止條件
- 精英選擇策略

**💡 建議:**
- 首次使用建議選擇「快速模式」
- 開啟並行處理可大幅縮短時間
- 超高速模式適合快速測試
- 品質模式適合正式分析
                        """)
            else:
                gr.Markdown("### ❌ 批次分析不可用")

        with gr.Tab("� 結果查詢"):
            if modules_ok:
                gr.Markdown("### 📋 所有分析結果")
                
                with gr.Row():
                    with gr.Column():
                        # 產業篩選
                        result_industry_dropdown = gr.Dropdown(
                            choices=["全部"] + industries,
                            value="全部",
                            label="🏭 篩選產業"
                        )
                        
                        # 查詢按鈕
                        query_btn = gr.Button("🔍 查詢結果", size="lg", variant="primary")
                
                # 結果表格
                with gr.Row():
                    results_dataframe = gr.Dataframe(
                        headers=["股票名稱", "買進持有策略報酬", "總報酬率", "年化報酬率", "最大回撤", "夏普比率", "勝率", "所屬產業"],
                        datatype=["str", "str", "str", "str", "str", "str", "str", "str"],
                        label="📈 分析結果總覽",
                        interactive=False,
                        wrap=True
                    )
                
                def query_results(industry_filter):
                    return get_analysis_results(db_obj, industry_filter)
                
                query_btn.click(
                    query_results,
                    inputs=[result_industry_dropdown],
                    outputs=[results_dataframe]
                )
            else:
                gr.Markdown("### ❌ 結果查詢不可用")

        with gr.Tab("�🔍 系統狀態"):
            gr.Markdown("### 📊 系統詳細資訊")
            
            # 添加系統摘要顯示
            with gr.Row():
                with gr.Column():
                    try:
                        import psutil
                        cpu_percent = psutil.cpu_percent(interval=0.1)
                        memory = psutil.virtual_memory()
                        system_summary = f"💻 CPU: {cpu_percent}% | 💾 記憶體: {memory.percent}% ({round(memory.used / (1024**3), 1)}/{round(memory.total / (1024**3), 1)} GB)"
                    except:
                        system_summary = "💻 硬體監控模組未安裝"
                    
                    gr.Markdown(f"**🖥️ 系統摘要:** {system_summary}")
            
            # 詳細系統狀態
            status_textbox = gr.Textbox(
                label="🔗 完整系統狀態", 
                lines=25, 
                value=get_enhanced_system_status(db_obj),
                max_lines=30
            )
            
            with gr.Row():
                refresh_btn = gr.Button("🔄 重新整理狀態", variant="primary")
                refresh_hardware_btn = gr.Button("🖥️ 刷新硬體資訊", variant="secondary")
            
            def refresh_status():
                return get_enhanced_system_status(db_obj)
            
            def refresh_hardware():
                # 直接返回增強的系統狀態
                return get_enhanced_system_status(db_obj)
            
            refresh_btn.click(
                refresh_status,
                outputs=[status_textbox]
            )
            
            refresh_hardware_btn.click(
                refresh_hardware,
                outputs=[status_textbox]
            )
    
    return demo

def run_detailed_buy_hold_analysis(stock, db_obj):
    """執行詳細的買進持有策略分析"""
    if not db_obj:
        return "❌ 資料庫未連接，無法執行分析"
    
    if not stock or stock == "請選擇股票":
        return "⚠️ 請先選擇股票"
    
    try:
        # 導入買進持有分析模組
        from buy_hold_analysis import analyze_multiple_periods
        
        # 提取股票代碼 (格式: "1101 台泥" -> "1101")
        stock_code = stock.split()[0] if stock else ""
        
        # 執行多區間分析
        analysis_result = analyze_multiple_periods(stock_code, db_obj)
        
        return analysis_result
        
    except ImportError:
        return "❌ 買進持有分析模組未找到，請確認 buy_hold_analysis.py 檔案存在"
    except Exception as e:
        return f"❌ 分析執行錯誤: {str(e)}"

# 創建完整界面
demo = create_full_interface()

if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7860)
