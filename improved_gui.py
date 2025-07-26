import gradio as gr
import pandas as pd
import os

# 檢查必要的模組
def test_and_import_modules():
    """測試並導入所有必要的模組"""
    try:
        from db_connector import DBConnector
        
        # 連接資料庫
        db = DBConnector()
        industries = db.get_industry_list()
        
        return True, "系統完全正常", industries, db
    except ImportError as e:
        return False, f"模組載入失敗: {e}", [], None
    except Exception as e:
        return False, f"資料庫連接失敗: {e}", [], None

def get_stocks_by_industry(industry):
    """根據產業獲取股票列表"""
    if industry == "請選擇產業":
        return gr.Dropdown(choices=[], value=None)
    
    try:
        # 重新創建數據庫連接
        from db_connector import DBConnector
        db_obj = DBConnector()
        stocks = db_obj.get_stocks_by_industry(industry)
        if stocks:
            return gr.Dropdown(choices=stocks, value=stocks[0], label="選擇股票 (格式: 代碼+名稱)")
        else:
            return gr.Dropdown(choices=[], value=None, label="該產業無股票數據")
    except Exception as e:
        return gr.Dropdown(choices=[], value=None, label=f"載入股票失敗: {e}")

def analyze_stock_with_custom_params(stock_name, m_intervals, hold_days, target_profit_ratio, alpha, 
                                   population_size, generations, max_time_minutes, progress=gr.Progress()):
    """使用自訂參數分析股票"""
    try:
        # 重新創建數據庫連接
        from db_connector import DBConnector
        db_obj = DBConnector()
    except Exception as e:
        return f"❌ 資料庫連接失敗: {e}", None
    
    if not stock_name or stock_name == "請選擇股票":
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
        
        # 智能停止條件設定
        convergence_threshold = 0.001  # 收斂閾值
        convergence_generations = 8  # 判斷收斂的世代數
        
        # 初始化基因演算法（使用自訂參數）
        print(f"🔍 開始分析股票: {stock_name}")
        print(f"📊 自訂參數: intervals={m_intervals}, days={hold_days}, profit={target_profit_ratio:.1%}, alpha={alpha:.1f}%")
        
        ga = GeneticAlgorithm(
            data=data, 
            population_size=int(population_size), 
            generations=int(generations),
            mutation_rate=0.1,
            crossover_rate=0.8,
            max_time_minutes=float(max_time_minutes),
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

⚙️ **自訂演算法參數**
最大世代數: {generations}
族群大小: {population_size}
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

💡 **參數建議** (避免零結果問題):
- 如果總利潤為 $0.00，建議降低α值至 0.5-1.5%
- 如果勝率為 0.0%，建議降低目標利潤比至 1.5-3%
- 如果沒有交易信號，建議減少移動平均間隔至 8-15
- 建選擇波動較大的股票進行測試
"""
        
        return result_text, "outputs/evolution.png"
        
    except Exception as e:
        return f"❌ 分析過程發生錯誤: {str(e)}", None

def create_improved_interface():
    """創建改進版界面，支援自訂參數"""
    
    # 測試所有模組和資料庫連接
    modules_ok, status_message, industries, db_obj = test_and_import_modules()
    
    with gr.Blocks(title="改進版基因演算法股票策略最佳化系統", theme=gr.themes.Soft()) as demo:
        if modules_ok:
            gr.Markdown("# 🚀 改進版基因演算法股票策略最佳化系統")
            gr.Markdown(f"**✅ 系統狀態:** {status_message}")
            gr.Markdown("**📋 說明:** 支援自訂參數，避免零結果問題")
        else:
            gr.Markdown("# ⚠️ 基因演算法股票策略最佳化系統 (系統錯誤)")
            gr.Markdown(f"**❌ 系統狀態:** {status_message}")
        
        with gr.Tab("🧬 自訂參數分析"):
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
                        
                        # 更新股票列表
                        industry_dropdown.change(
                            get_stocks_by_industry,
                            inputs=[industry_dropdown],
                            outputs=[stock_dropdown]
                        )
                    
                    with gr.Column(scale=1):
                        gr.Markdown("### ⚙️ 交易策略參數")
                        gr.Markdown("**建議值基於實際測試，可避免零結果問題**")
                        
                        # 策略參數 - 使用優化後的預設值
                        m_intervals = gr.Slider(
                            minimum=5, maximum=50, step=1, value=12,  # 優化的預設值
                            label="📊 移動平均間隔 (建議: 8-20)"
                        )
                        
                        hold_days = gr.Slider(
                            minimum=1, maximum=30, step=1, value=2,  # 優化的預設值
                            label="📅 持有天數 (建議: 1-5)"
                        )
                        
                        target_profit_ratio = gr.Slider(
                            minimum=0.01, maximum=0.10, step=0.005, value=0.015,  # 1.5% 優化的預設值
                            label="🎯 目標利潤比 (建議: 1.5-3.0%)"
                        )
                        
                        alpha = gr.Slider(
                            minimum=0.3, maximum=5.0, step=0.1, value=0.6,  # 0.6% 優化的預設值
                            label="🚪 門檻α (%) (建議: 0.5-1.5%)"
                        )
                        
                        gr.Markdown("### 🧬 演算法參數")
                        
                        population_size = gr.Slider(
                            minimum=10, maximum=100, step=10, value=30,  # 減少族群大小以提高速度
                            label="👥 族群大小"
                        )
                        
                        generations = gr.Slider(
                            minimum=10, maximum=100, step=10, value=30,  # 減少世代數以提高速度
                            label="🔄 最大世代數"
                        )
                        
                        max_time_minutes = gr.Slider(
                            minimum=1.0, maximum=10.0, step=0.5, value=3.0,  # 減少時間限制
                            label="⏱️ 時間限制 (分鐘)"
                        )
                        
                        # 分析按鈕
                        analyze_btn = gr.Button(
                            "🧬 開始自訂參數分析", 
                            size="lg", 
                            variant="primary"
                        )
                
                with gr.Row():
                    with gr.Column():
                        result_textbox = gr.Textbox(
                            label="📋 分析結果", 
                            lines=20,
                            placeholder="分析結果將在這裡顯示..."
                        )
                    
                    with gr.Column():
                        result_image = gr.Image(
                            label="📈 演化過程圖表",
                            type="filepath"
                        )
                
                # 快速預設按鈕
                gr.Markdown("### ⚡ 快速預設參數")
                with gr.Row():
                    def set_conservative():
                        return 15, 3, 0.02, 0.8  # 保守參數
                    
                    def set_balanced():
                        return 12, 2, 0.015, 0.6  # 平衡參數（推薦）
                    
                    def set_aggressive():
                        return 8, 2, 0.025, 1.0  # 積極參數
                    
                    conservative_btn = gr.Button("🛡️ 保守策略", size="sm")
                    balanced_btn = gr.Button("⚖️ 平衡策略 (推薦)", size="sm", variant="secondary")
                    aggressive_btn = gr.Button("⚡ 積極策略", size="sm")
                    
                    conservative_btn.click(
                        set_conservative,
                        outputs=[m_intervals, hold_days, target_profit_ratio, alpha]
                    )
                    
                    balanced_btn.click(
                        set_balanced,
                        outputs=[m_intervals, hold_days, target_profit_ratio, alpha]
                    )
                    
                    aggressive_btn.click(
                        set_aggressive,
                        outputs=[m_intervals, hold_days, target_profit_ratio, alpha]
                    )
                
                # 分析功能
                analyze_btn.click(
                    analyze_stock_with_custom_params,
                    inputs=[
                        stock_dropdown, m_intervals, hold_days, target_profit_ratio, alpha,
                        population_size, generations, max_time_minutes
                    ],
                    outputs=[result_textbox, result_image]
                )
                
            else:
                gr.Markdown("### ❌ 系統無法啟動")
                gr.Markdown("請檢查資料庫連接和模組安裝")

        with gr.Tab("📋 零結果問題診斷"):
            gr.Markdown("### 🔍 零結果問題常見原因與解決方案")
            gr.Markdown("""
**❌ 常見問題症狀:**
- 總利潤: $0.00
- 勝率: 0.0%
- 最大回撤: 10.0%
- 夏普比率: 0.0000

**🔍 主要原因:**
1. **α門檻值過高** - 導致無法產生買入信號
2. **目標利潤比過高** - 導致所有交易都達不到目標
3. **移動平均間隔過長** - 減少交易機會
4. **持有天數過短** - 無法累積足夠利潤

**💡 解決方案:**
1. **降低α值**: 從預設的2%降至0.5-1.5%
2. **降低目標利潤比**: 從5%降至1.5-3%
3. **縮短移動平均**: 從20降至8-15
4. **調整持有天數**: 設為1-5天
5. **選擇高波動股票**: 避免選擇價格過於穩定的股票

**✅ 推薦參數組合:**
- **平衡策略**: 間隔12, 持有2天, 利潤1.5%, α0.6%
- **保守策略**: 間隔15, 持有3天, 利潤2.0%, α0.8%
- **積極策略**: 間隔8, 持有2天, 利潤2.5%, α1.0%
""")
    
    return demo

# 創建改進版界面
demo = create_improved_interface()

if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7861)  # 使用不同的端口避免衝突
