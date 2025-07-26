import gradio as gr
import pandas as pd
import numpy as np

# 首先嘗試導入資料庫相關模組
DB_AVAILABLE = False
db = None

def try_import_database():
    global DB_AVAILABLE, db
    try:
        import pyodbc
        from db_connector import DBConnector
        from multi_stock_optimizer import optimize_all_stocks, optimize_by_industry
        from ga_optimizer import GeneticAlgorithm
        from report_generator import save_evolution_plot
        
        # 嘗試連接資料庫
        db = DBConnector()
        test_industries = db.get_industry_list()
        DB_AVAILABLE = True
        print("✅ 資料庫連接成功")
        return True
    except ImportError as e:
        print(f"❌ 模組導入失敗: {e}")
        return False
    except Exception as e:
        print(f"❌ 資料庫連接失敗: {e}")
        print("請檢查:")
        print("1. SQL Server 是否啟動")
        print("2. 資料庫 'StockDB' 是否存在")
        print("3. 伺服器名稱是否正確")
        print("4. ODBC Driver 是否已安裝")
        return False

# 嘗試初始化資料庫
try_import_database()

def get_stocks_for_industry(industry):
    """根據選擇的產業返回對應的股票列表"""
    if not DB_AVAILABLE:
        return gr.Dropdown(choices=["請先修復資料庫連接"], value=None, label="資料庫未連接")
    
    if industry == "請選擇產業" or industry is None or industry.startswith("請"):
        return gr.Dropdown(choices=[], value=None, label="請先選擇產業")
        
    try:
        stocks = db.get_stocks_by_industry(industry)
        if stocks:
            return gr.Dropdown(choices=stocks, value=stocks[0], label="選擇股票 (格式: 代碼+名稱)")
        else:
            return gr.Dropdown(choices=[], value=None, label="該產業無股票資料")
    except Exception as e:
        return gr.Dropdown(choices=[], value=None, label=f"錯誤: {str(e)}")

def run_ga_analysis(table_name, generations=50, population_size=50):
    """運行基因演算法分析"""
    if not DB_AVAILABLE:
        return "❌ 資料庫未連接，無法執行分析", None
    
    try:
        from ga_optimizer import GeneticAlgorithm
        from report_generator import save_evolution_plot
        
        # 讀取股票數據
        data = db.read_stock_data(table_name)
        if data.empty:
            return f"❌ 股票資料表 '{table_name}' 無數據", None
        
        # 獲取股票資訊
        stock_code = db.extract_stock_code_from_table_name(table_name)
        info = db.get_stock_info(stock_code)
        industry = info['Industry'] if info else "未知"
        stock_name = info['StockName'] if info else "未知"

        # 執行基因演算法
        print(f"開始分析 {stock_code} ({stock_name})...")
        ga = GeneticAlgorithm(data, population_size=int(population_size), generations=int(generations))
        best_result = ga.evolve()

        # 生成圖表
        save_evolution_plot(ga.best_fitness_history, ga.avg_fitness_history)

        # 保存最佳參數
        db.save_best_params(table_name, best_result, industry)

        result_text = (
            f"✅ 分析完成!\n\n"
            f"股票: {stock_code} ({stock_name})\n"
            f"資料表: {table_name}\n"
            f"產業: {industry}\n\n"
            f"績效指標:\n"
            f"📈 最佳適應度: {best_result.fitness:.4f}\n"
            f"💰 總利潤: {best_result.total_profit:.2f}\n"
            f"🎯 勝率: {best_result.win_rate:.1%}\n"
            f"📉 最大回撤: {best_result.max_drawdown:.1%}\n\n"
            f"最佳參數:\n"
            f"🔢 區間數: {best_result.parameters.m_intervals}\n"
            f"📅 持有天數: {best_result.parameters.hold_days}\n"
            f"🎯 目標利潤比例: {best_result.parameters.target_profit_ratio:.2f}\n"
            f"⚖️ 門檻α: {best_result.parameters.alpha:.2f}"
        )

        return result_text, "outputs/evolution.png"
        
    except Exception as e:
        return f"❌ 分析過程發生錯誤: {str(e)}", None

def run_batch_optimization(industry):
    """批次最佳化"""
    if not DB_AVAILABLE:
        return "❌ 資料庫未連接，無法執行批次處理"
    
    try:
        from multi_stock_optimizer import optimize_all_stocks, optimize_by_industry
        if industry == "全部":
            return optimize_all_stocks()
        else:
            return optimize_by_industry(industry)
    except Exception as e:
        return f"❌ 批次處理錯誤: {str(e)}"

def get_database_status():
    """獲取資料庫狀態"""
    if not DB_AVAILABLE:
        return """❌ 資料庫未連接

🔧 故障排除步驟:

1. 檢查 SQL Server 服務
   - 開啟 Windows 服務管理員
   - 尋找 'SQL Server' 服務並確認運行中

2. 檢查資料庫連接設定
   - 伺服器名稱: DESKTOP-TOB09L9
   - 資料庫名稱: StockDB
   - 認證: Windows 整合驗證

3. 檢查 ODBC 驅動程式
   - 需要安裝 "ODBC Driver 17 for SQL Server"

4. 測試連接
   - 使用 SQL Server Management Studio 測試連接

💡 如需修改連接設定，請編輯 db_connector.py 檔案"""
    
    try:
        industries = db.get_industry_list()
        total_stocks = 0
        status_text = "✅ 資料庫連接成功\n\n"
        status_text += f"📊 總產業數: {len(industries)}\n\n"
        
        for industry in industries:
            stocks = db.get_stocks_by_industry(industry)
            total_stocks += len(stocks)
            status_text += f"• {industry}: {len(stocks)} 檔股票\n"
        
        status_text += f"\n📈 總股票數: {total_stocks}"
        return status_text
    except Exception as e:
        return f"❌ 讀取資料庫資訊失敗: {str(e)}"

def create_main_interface():
    """創建主要界面"""
    
    with gr.Blocks(title="股票策略最佳化系統") as demo:
        if DB_AVAILABLE:
            gr.Markdown("# 🚀 基因演算法股票策略最佳化")
            gr.Markdown("**✨ 系統狀態:** 資料庫已連接，可進行真實數據分析")
        else:
            gr.Markdown("# ⚠️ 基因演算法股票策略最佳化 (離線模式)")
            gr.Markdown("**❌ 系統狀態:** 資料庫未連接，請檢查設定")
        
        gr.Markdown("**📋 操作說明:** 選擇產業和股票，系統將使用固定參數 (世代數=50, 族群大小=50) 進行分析")
        
        with gr.Tab("📈 單檔分析"):        
            with gr.Row():
                with gr.Column():
                    # 產業選擇
                    if DB_AVAILABLE:
                        try:
                            industry_list = ["請選擇產業"] + db.get_industry_list()
                        except Exception as e:
                            industry_list = [f"載入產業失敗: {str(e)}"]
                    else:
                        industry_list = ["請先修復資料庫連接"]
                        
                    industry_dropdown = gr.Dropdown(
                        choices=industry_list, 
                        value=industry_list[0], 
                        label="🏭 選擇產業"
                    )
                    
                    stock_dropdown = gr.Dropdown(
                        choices=[], 
                        value=None, 
                        label="📊 選擇股票"
                    )
                    
                with gr.Column():
                    gr.Markdown("### ⚙️ 分析參數")
                    gr.Markdown("🔒 **固定參數設定:**")
                    gr.Markdown("• 世代數: 50")
                    gr.Markdown("• 族群大小: 50")
                    gr.Markdown("• 突變率: 0.1")
                    gr.Markdown("• 交配率: 0.8")
            
            # 分析按鈕和結果
            analyze_btn = gr.Button("🚀 開始分析", size="lg", variant="primary")
            
            with gr.Row():
                with gr.Column():
                    output_text = gr.Textbox(label="📋 分析結果", lines=15)
                with gr.Column():
                    output_img = gr.Image(label="📈 演化過程圖", type="filepath")
            
            # 事件處理
            industry_dropdown.change(
                get_stocks_for_industry,
                inputs=[industry_dropdown],
                outputs=[stock_dropdown]
            )
            
            def run_analysis(stock_dropdown_val):
                if not DB_AVAILABLE:
                    return "❌ 資料庫未連接，無法執行分析", None
                if not stock_dropdown_val or "請" in stock_dropdown_val:
                    return "⚠️ 請選擇有效的股票", None
                return run_ga_analysis(stock_dropdown_val)
            
            analyze_btn.click(
                run_analysis,
                inputs=[stock_dropdown],
                outputs=[output_text, output_img]
            )

        with gr.Tab("🔄 批次處理"):
            if DB_AVAILABLE:
                try:
                    batch_industry_list = ["全部"] + db.get_industry_list()
                except:
                    batch_industry_list = ["載入失敗"]
            else:
                batch_industry_list = ["資料庫未連接"]
                
            batch_industry_dropdown = gr.Dropdown(
                choices=batch_industry_list, 
                value=batch_industry_list[0], 
                label="🏭 選擇批次處理的產業"
            )
            batch_output = gr.Textbox(label="📋 批次處理狀態", lines=15)
            batch_btn = gr.Button("🔄 開始批次分析", size="lg")
            batch_btn.click(run_batch_optimization, [batch_industry_dropdown], batch_output)
        
        with gr.Tab("🔍 系統狀態"):
            gr.Markdown("### 📊 資料庫連接資訊")
            
            db_status = gr.Textbox(label="🔗 資料庫狀態", lines=15, value=get_database_status())
            refresh_btn = gr.Button("🔄 重新整理")
            refresh_btn.click(lambda: get_database_status(), outputs=[db_status])
    
    return demo

# 創建並運行界面
demo = create_main_interface()

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
