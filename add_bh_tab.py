#!/usr/bin/env python3
"""
為 full_gui.py 添加買進持有分析頁籤的修補腳本
"""

def add_buy_hold_tab():
    """在 full_gui.py 中添加買進持有分析頁籤"""
    
    # 讀取原始文件
    with open('full_gui.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 定義要插入的買進持有分析頁籤代碼
    buy_hold_tab_code = '''
        with gr.Tab("💰 買進持有分析"):
            if modules_ok:
                gr.Markdown("### 📊 買進持有策略深度分析")
                gr.Markdown("**說明：** 分析各股票在不同時間區間的買進持有策略報酬表現")
                
                with gr.Row():
                    with gr.Column():
                        # 股票選擇
                        bh_industry_dropdown = gr.Dropdown(
                            choices=["請選擇產業"] + industries,
                            value="請選擇產業",
                            label="🏭 選擇產業"
                        )
                        bh_stock_dropdown = gr.Dropdown(
                            choices=[],
                            value=None,
                            label="📊 選擇股票"
                        )
                        
                        # 分析按鈕
                        analyze_bh_btn = gr.Button("📊 開始深度分析", size="lg", variant="primary")
                
                # 分析結果顯示
                with gr.Row():
                    bh_result_textbox = gr.Textbox(
                        label="📋 買進持有策略分析報告", 
                        lines=25,
                        max_lines=30
                    )
                
                # 事件處理
                def update_bh_stocks(industry):
                    return get_stocks_for_industry(industry, db_obj)
                
                def run_buy_hold_analysis(stock):
                    return run_detailed_buy_hold_analysis(stock, db_obj)
                
                bh_industry_dropdown.change(
                    update_bh_stocks,
                    inputs=[bh_industry_dropdown],
                    outputs=[bh_stock_dropdown]
                )
                
                analyze_bh_btn.click(
                    run_buy_hold_analysis,
                    inputs=[bh_stock_dropdown],
                    outputs=[bh_result_textbox]
                )
            else:
                gr.Markdown("### ❌ 買進持有分析不可用")
'''
    
    # 找到插入位置 (在 "結果查詢不可用" 之後，"系統狀態" 之前)
    insert_marker = '                gr.Markdown("### ❌ 結果查詢不可用")'
    
    if insert_marker in content:
        # 找到插入位置
        insert_pos = content.find(insert_marker) + len(insert_marker)
        
        # 插入買進持有分析頁籤
        new_content = content[:insert_pos] + buy_hold_tab_code + content[insert_pos:]
        
        # 寫回文件
        with open('full_gui.py', 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ 成功添加買進持有分析頁籤")
        return True
    else:
        print(f"❌ 找不到插入位置標記: {insert_marker}")
        return False

if __name__ == "__main__":
    add_buy_hold_tab()
