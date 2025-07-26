import gradio as gr
import sys
import os

def test_database_connection():
    """測試資料庫連接"""
    try:
        # 嘗試導入pyodbc
        import pyodbc
        drivers = pyodbc.drivers()
        
        # 嘗試導入我們的資料庫連接器
        from db_connector import DBConnector
        
        # 嘗試連接資料庫
        db = DBConnector()
        industries = db.get_industry_list()
        
        return True, f"✅ 資料庫連接成功！找到 {len(industries)} 個產業", industries, db
        
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
        return gr.Dropdown(choices=stocks, value=stocks[0] if stocks else None)
    except Exception as e:
        return gr.Dropdown(choices=[f"錯誤: {str(e)}"], value=None)

def run_analysis(stock_name, db_obj):
    """執行股票分析"""
    if not db_obj:
        return "❌ 資料庫未連接"
    
    if not stock_name or "請" in stock_name:
        return "⚠️ 請選擇股票"
    
    try:
        # 嘗試讀取股票數據
        data = db_obj.read_stock_data(stock_name)
        row_count = len(data)
        
        if row_count == 0:
            return f"❌ 股票 {stock_name} 無數據"
        
        # 獲取股票資訊
        stock_code = db_obj.extract_stock_code_from_table_name(stock_name)
        info = db_obj.get_stock_info(stock_code)
        
        result = f"""✅ 資料讀取成功！

股票代碼: {stock_code}
股票名稱: {info['StockName'] if info else '未知'}
所屬產業: {info['Industry'] if info else '未知'}
資料筆數: {row_count} 筆

⚠️ 注意: 這只是資料讀取測試
真正的基因演算法分析需要完整的模組支援"""
        
        return result
        
    except Exception as e:
        return f"❌ 分析失敗: {str(e)}"

def create_interface():
    """創建簡化的測試界面"""
    
    # 測試資料庫連接
    db_ok, db_message, industries, db_obj = test_database_connection()
    
    with gr.Blocks(title="股票分析系統測試") as demo:
        gr.Markdown("# 🧪 股票分析系統 - 資料庫連接測試")
        gr.Markdown(f"**連接狀態:** {db_message}")
        
        if db_ok:
            gr.Markdown("### 📊 系統可用，可以進行真實資料分析")
            
            # 產業選擇
            industry_choices = ["請選擇產業"] + industries
            industry_dropdown = gr.Dropdown(
                choices=industry_choices,
                value="請選擇產業",
                label="選擇產業"
            )
            
            # 股票選擇
            stock_dropdown = gr.Dropdown(
                choices=[],
                value=None,
                label="選擇股票"
            )
            
            # 分析按鈕
            analyze_btn = gr.Button("🔍 測試資料讀取", size="lg")
            
            # 結果顯示
            result_text = gr.Textbox(label="測試結果", lines=10)
            
            # 事件綁定
            def update_stocks(industry):
                return get_stocks_for_industry(industry, db_obj)
            
            def run_test(stock):
                return run_analysis(stock, db_obj)
            
            industry_dropdown.change(
                update_stocks,
                inputs=[industry_dropdown],
                outputs=[stock_dropdown]
            )
            
            analyze_btn.click(
                run_test,
                inputs=[stock_dropdown],
                outputs=[result_text]
            )
            
        else:
            gr.Markdown("### ❌ 資料庫連接失敗")
            gr.Markdown("""
**故障排除建議:**

1. **檢查 SQL Server 服務**
   - 開啟「服務」管理員
   - 確認 SQL Server 服務正在運行

2. **檢查連接設定**
   - 伺服器: DESKTOP-TOB09L9
   - 資料庫: StockDB
   - 使用 Windows 驗證

3. **安裝必要元件**
   - Microsoft ODBC Driver 17 for SQL Server
   - 確認 pyodbc 套件已安裝

4. **測試連接**
   - 使用 SQL Server Management Studio 測試連接
   - 確認資料庫 StockDB 存在
            """)
    
    return demo

# 創建界面
demo = create_interface()

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
