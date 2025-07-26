import gradio as gr
from ga_optimizer import GeneticAlgorithm
from report_generator import save_evolution_plot

# 嘗試連接資料庫，如果失敗則提供錯誤信息
try:
    from db_connector import DBConnector
    from multi_stock_optimizer import optimize_all_stocks, optimize_by_industry
    db = DBConnector()
    # 測試資料庫連接
    test_query = db.get_industry_list()
    DB_AVAILABLE = True
    print("✅ 資料庫連接成功")
except Exception as e:
    print(f"❌ 資料庫連接失敗: {e}")
    print("請檢查:")
    print("1. SQL Server 是否啟動")
    print("2. 資料庫 'StockDB' 是否存在")
    print("3. 伺服器名稱是否正確 (目前設定: DESKTOP-TOB09L9)")
    print("4. ODBC Driver 17 for SQL Server 是否已安裝")
    db = None
    DB_AVAILABLE = False

def get_stocks_for_industry(industry):
    """根據選擇的產業返回對應的股票列表"""
    if not DB_AVAILABLE:
        # 返回模擬數據
        return gr.Dropdown(choices=["模擬資料 - 請連接資料庫"], value="模擬資料 - 請連接資料庫", label="資料庫未連接")
    
    if industry == "請選擇產業" or industry is None:
        return gr.Dropdown(choices=[], value=None, label="請先選擇產業")
    try:
        stocks = db.get_stocks_by_industry(industry)
        if stocks:
            return gr.Dropdown(choices=stocks, value=stocks[0], label="選擇股票 (格式: 代碼+名稱)")
        else:
            return gr.Dropdown(choices=[], value=None, label="該產業無股票資料")
    except Exception as e:
        return gr.Dropdown(choices=[], value=None, label=f"錯誤: {str(e)}")

def run_ga(table_name, generations, population_size):
    if not DB_AVAILABLE:
        return "資料庫未連接，無法執行分析。請檢查資料庫連接。"
    
    data = db.read_stock_data(table_name)
    # 從表名稱中提取股票代碼來查詢股票資訊
    stock_code = db.extract_stock_code_from_table_name(table_name)
    info = db.get_stock_info(stock_code)
    industry = info['Industry'] if info else "未知"
    stock_name = info['StockName'] if info else "未知"

    ga = GeneticAlgorithm(data, population_size=int(population_size), generations=int(generations))
    best_result = ga.evolve()

    save_evolution_plot(ga.best_fitness_history, ga.avg_fitness_history)

    db.save_best_params(table_name, best_result, industry)

    result_text = (
        f"股票: {stock_code} ({stock_name})\n"
        f"資料表: {table_name}\n"
        f"產業: {industry}\n"
        f"最佳適應度: {best_result.fitness:.4f}\n"
        f"總利潤: {best_result.total_profit:.2f}\n"
        f"勝率: {best_result.win_rate:.1%}\n"
        f"最大回撤: {best_result.max_drawdown:.1%}\n"
        f"最佳參數:\n"
        f"- 區間數={best_result.parameters.m_intervals}\n"
        f"- 持有天數={best_result.parameters.hold_days}\n"
        f"- 目標利潤比例={best_result.parameters.target_profit_ratio:.2f}\n"
        f"- 門檻α={best_result.parameters.alpha:.2f}"
    )

    return result_text, "outputs/evolution.png"

def run_batch(industry):
    if not DB_AVAILABLE:
        return "資料庫未連接，無法執行批次處理"
    
    try:
        from multi_stock_optimizer import optimize_all_stocks, optimize_by_industry
        if industry == "全部":
            return optimize_all_stocks()
        else:
            return optimize_by_industry(industry)
    except Exception as e:
        return f"批次處理錯誤: {str(e)}"

with gr.Blocks() as demo:
    if DB_AVAILABLE:
        gr.Markdown("## 基因演算法股票策略最佳化 (簡化版)")
        gr.Markdown("**操作說明：** 只需選擇產業和股票即可開始優化，系統使用固定的演算法參數")
    else:
        gr.Markdown("## 基因演算法股票策略最佳化 (離線模式)")
        gr.Markdown("**注意：** 資料庫未連接，請檢查資料庫設定後重新啟動應用")
    
    with gr.Tab("單檔最佳化"):        
        with gr.Row():
            with gr.Column():
                # SQL Server 輸入 - 產業和股票連動選擇
                if DB_AVAILABLE:
                    try:
                        industry_list = ["請選擇產業"] + db.get_industry_list()
                        print(f"載入了 {len(industry_list)-1} 個產業")
                    except Exception as e:
                        industry_list = [f"載入產業失敗: {str(e)}"]
                        print(f"載入產業列表失敗: {e}")
                else:
                    industry_list = ["資料庫未連接 - 請檢查設定"]
                    
                industry_dropdown = gr.Dropdown(
                    choices=industry_list, 
                    value="請選擇產業", 
                    label="選擇產業"
                )
                
                stock_dropdown = gr.Dropdown(
                    choices=[], 
                    value=None, 
                    label="選擇股票 (格式: 代碼+名稱)"
                )
                
            with gr.Column():
                gr.Markdown("### 參數設定")
                gr.Markdown("使用固定參數：世代數=50, 族群大小=50")
                generations = gr.State(value=50)  # 固定世代數
                population = gr.State(value=50)   # 固定族群大小
        
        # 結果顯示
        output_text = gr.Textbox(label="最佳化結果", lines=10)
        output_img = gr.Image(label="演化過程", type="filepath")
        btn = gr.Button("開始最佳化", size="lg")
        
        # 產業選擇改變時更新股票列表
        industry_dropdown.change(
            get_stocks_for_industry,
            inputs=[industry_dropdown],
            outputs=[stock_dropdown]
        )
        
        # 點擊最佳化按鈕
        def run_optimization(stock_dropdown_val):
            if not DB_AVAILABLE:
                return "資料庫未連接，無法執行優化", None
                
            if not stock_dropdown_val:
                return "請選擇股票", None
            
            # 使用固定參數
            generations_val = 50
            population_val = 50
            return run_ga(stock_dropdown_val, generations_val, population_val)
        
        btn.click(
            run_optimization,
            inputs=[stock_dropdown],
            outputs=[output_text, output_img]
        )

    with gr.Tab("批次最佳化"):
        if DB_AVAILABLE:
            try:
                batch_industry_list = ["全部"] + db.get_industry_list()
            except:
                batch_industry_list = ["資料庫連接失敗"]
        else:
            batch_industry_list = ["資料庫未連接"]
            
        batch_industry_dropdown = gr.Dropdown(
            choices=batch_industry_list, 
            value="全部", 
            label="選擇產業進行批次最佳化"
        )
        batch_output = gr.Textbox(label="批次處理狀態", lines=15)
        batch_btn = gr.Button("開始批次最佳化", size="lg")
        batch_btn.click(run_batch, [batch_industry_dropdown], batch_output)
    
    with gr.Tab("資料庫狀態"):
        gr.Markdown("### 資料庫連接資訊")
        
        def get_db_status():
            if not DB_AVAILABLE:
                return "❌ 資料庫未連接\n\n請檢查:\n1. SQL Server 是否啟動\n2. 資料庫名稱是否正確\n3. ODBC 驅動是否安裝\n4. 連接字串是否正確"
            
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
                return f"❌ 資料庫連接失敗: {str(e)}"
        
        db_status = gr.Textbox(label="資料庫狀態", lines=10, value=get_db_status())
        refresh_btn = gr.Button("重新整理")
        refresh_btn.click(lambda: get_db_status(), outputs=[db_status])

demo.launch()
