import gradio as gr
import pandas as pd
import numpy as np

def simple_demo():
    """簡化版的演示界面"""
    
    # 模擬產業和股票數據
    industries = ["科技業", "金融業", "傳統產業", "生技醫療", "電子零組件"]
    
    stocks_by_industry = {
        "科技業": ["2330台積電", "2454聯發科", "2308台達電"],
        "金融業": ["2891中信金", "2882國泰金", "2892第一金"],
        "傳統產業": ["1101台泥", "1102亞泥", "2002中鋼"],
        "生技醫療": ["4119旭富", "6505台塑化", "1234生技"],
        "電子零組件": ["2317鴻海", "3008大立光", "2327國巨"]
    }
    
    def get_stocks_for_industry(industry):
        """根據選擇的產業返回對應的股票列表"""
        if industry in stocks_by_industry:
            stocks = stocks_by_industry[industry]
            return gr.Dropdown(choices=stocks, value=stocks[0], label="選擇股票")
        else:
            return gr.Dropdown(choices=[], value=None, label="請先選擇產業")
    
    def run_optimization(industry, stock):
        """模擬優化過程"""
        if not industry or not stock:
            return "請選擇產業和股票"
        
        # 模擬優化結果
        result_text = f"""
優化完成！

選擇的產業: {industry}
選擇的股票: {stock}

使用固定參數:
- 世代數: 50
- 族群大小: 50

模擬結果:
- 最佳適應度: 0.8524
- 總利潤: 125,430 元
- 勝率: 68.5%
- 最大回撤: -12.3%

最佳參數:
- 區間數: 15
- 持有天數: 5
- 目標利潤比例: 0.08
- 門檻α: 1.25

注意: 這是模擬結果，請連接資料庫以獲得真實分析。
        """
        
        return result_text
    
    with gr.Blocks(title="股票策略最佳化 - 簡化版") as demo:
        gr.Markdown("# 基因演算法股票策略最佳化 (簡化版)")
        gr.Markdown("**操作說明：** 只需選擇產業和股票即可開始優化，系統使用固定的演算法參數")
        
        with gr.Row():
            with gr.Column():
                industry_dropdown = gr.Dropdown(
                    choices=["請選擇產業"] + industries,
                    value="請選擇產業",
                    label="選擇產業"
                )
                
                stock_dropdown = gr.Dropdown(
                    choices=[],
                    value=None,
                    label="選擇股票"
                )
                
            with gr.Column():
                gr.Markdown("### 參數設定")
                gr.Markdown("使用固定參數：世代數=50, 族群大小=50")
        
        output_text = gr.Textbox(label="最佳化結果", lines=15)
        btn = gr.Button("開始最佳化", size="lg")
        
        # 產業選擇改變時更新股票列表
        industry_dropdown.change(
            get_stocks_for_industry,
            inputs=[industry_dropdown],
            outputs=[stock_dropdown]
        )
        
        # 點擊最佳化按鈕
        btn.click(
            run_optimization,
            inputs=[industry_dropdown, stock_dropdown],
            outputs=[output_text]
        )
        
        gr.Markdown("---")
        gr.Markdown("### 說明")
        gr.Markdown("""
        - 此為簡化版演示界面
        - 顯示的是模擬數據，非真實交易結果
        - 若要使用真實數據，請確保資料庫連接正常
        - 系統已簡化為只需選擇產業和股票兩個參數
        """)
    
    return demo

if __name__ == "__main__":
    demo = simple_demo()
    demo.launch(server_name="0.0.0.0", server_port=7860)
