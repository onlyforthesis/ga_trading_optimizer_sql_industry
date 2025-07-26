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
        
        # 格式化結果
        train_data_info = f"訓練數據: {len(ga.train_data)} 筆 (2019-2023)"
        test_data_info = f"測試數據: {len(ga.test_data)} 筆 (2024)" if not ga.test_data.empty else "測試數據: 無"
        
        result_text = f"""🎉 基因演算法分析完成！

📊 **股票資訊**
股票代碼: {stock_code}
股票名稱: {stock_display_name}
所屬產業: {industry}
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

        with gr.Tab("🔄 批次分析"):
            if modules_ok:
                batch_industry_choices = ["全部"] + industries
                batch_industry_dropdown = gr.Dropdown(
                    choices=batch_industry_choices,
                    value="全部",
                    label="🏭 選擇批次分析的產業"
                )
                batch_result = gr.Textbox(label="📋 批次分析結果", lines=15)
                batch_btn = gr.Button("🔄 開始批次分析", size="lg")
                
                def run_batch(industry):
                    return run_batch_analysis(industry, db_obj)
                
                batch_btn.click(
                    run_batch,
                    inputs=[batch_industry_dropdown],
                    outputs=[batch_result]
                )
            else:
                gr.Markdown("### ❌ 批次分析不可用")

        with gr.Tab("🔍 系統狀態"):
            gr.Markdown("### 📊 系統詳細資訊")
            
            status_textbox = gr.Textbox(
                label="🔗 系統狀態", 
                lines=15, 
                value=get_database_status(db_obj)
            )
            refresh_btn = gr.Button("🔄 重新整理狀態")
            
            def refresh_status():
                return get_database_status(db_obj)
            
            refresh_btn.click(
                refresh_status,
                outputs=[status_textbox]
            )
    
    return demo

# 創建完整界面
demo = create_full_interface()

if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7860)
