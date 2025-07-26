# 🚀 基因演算法股票策略最佳化系統

[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![SQL Server](https://img.shields.io/badge/database-SQL%20Server-red.svg)](https://www.microsoft.com/sql-server)
[![Gradio](https://img.shields.io/badge/gui-Gradio-orange.svg)](https://gradio.app)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

一個使用基因演算法優化股票交易策略的系統，具有Web界面和完整的數據分析功能。

## 📋 目錄

- [功能特色](#功能特色)
- [系統架構](#系統架構)
- [安裝指南](#安裝指南)
- [使用方法](#使用方法)
- [核心模組](#核心模組)
- [參數說明](#參數說明)
- [故障排除](#故障排除)
- [最新改進](#最新改進)
- [貢獻指南](#貢獻指南)

## ✨ 功能特色

### 🧬 核心功能
- **基因演算法優化**: 自動尋找最佳交易參數
- **多股票批次分析**: 支援產業別批次優化
- **智能停止條件**: 時間限制 + 收斂檢測
- **數據質量檢查**: 價格變化合理性驗證
- **Web圖形界面**: 直觀的Gradio介面

### 📊 分析功能
- **回測分析**: 2019-2023訓練，2024測試
- **績效指標**: 夏普比率、勝率、最大回撤
- **視覺化圖表**: 演化過程即時顯示
- **參數保存**: 結果自動存儲至數據庫

### 🔧 技術特色
- **參數驗證**: 防止不合理參數設定
- **錯誤處理**: 完整的異常處理機制
- **BOM處理**: 自動處理Unicode BOM字符
- **診斷工具**: 多種問題診斷腳本

## 🏗️ 系統架構

```
📦 ga_trading_optimizer_sql_industry/
├── 🖥️ GUI介面
│   ├── main.py                    # 原始GUI啟動
│   ├── full_gui.py               # 完整功能GUI
│   ├── improved_gui.py           # 改進版GUI (推薦)
│   └── simple_gui.py             # 簡化版GUI
│
├── 🧬 核心演算法
│   ├── ga_optimizer.py           # 基因演算法主程式
│   ├── multi_stock_optimizer.py  # 多股票優化器
│   └── report_generator.py       # 報告生成器
│
├── 💾 數據處理
│   ├── db_connector.py           # 數據庫連接器
│   └── data_loader.py            # 數據載入器
│
├── 🔍 診斷工具
│   ├── comprehensive_diagnostic.py    # 綜合診斷
│   ├── real_data_diagnostic.py       # 真實數據診斷
│   ├── zero_results_diagnostic.py    # 零結果問題診斷
│   ├── fix_zero_results.py          # 零結果修復工具
│   └── price_quality_checker.py     # 價格質量檢查
│
├── 🧪 測試工具
│   ├── test_*.py                 # 各種測試腳本
│   └── check_bestparams_table.py # 數據庫檢查
│
└── 📁 輸出
    └── outputs/
        └── evolution.png         # 演化過程圖表
```

## 💻 安裝指南

### 🔧 環境需求
- **Python**: 3.10 或更高版本
- **SQL Server**: 支援Windows整合驗證
- **ODBC Driver**: ODBC Driver 17 for SQL Server

### 📦 安裝步驟

1. **克隆專案**
```bash
git clone https://github.com/onlyforthesis/ga_trading_optimizer_sql_industry.git
cd ga_trading_optimizer_sql_industry
```

2. **安裝相依套件**
```bash
pip install -r requirements.txt
```

3. **設定數據庫**
```bash
# 確保SQL Server服務運行
# 設定資料庫連接字串 (在 db_connector.py 中)
Server: DESKTOP-TOB09L9\\StockDB
Database: StockDB
```

4. **驗證安裝**
```bash
python check_bestparams_table.py
```

## 🚀 使用方法

### 🖥️ 啟動系統

#### 方法1: 改進版GUI (推薦)
```bash
python improved_gui.py
```
- 訪問: http://127.0.0.1:7861
- ✅ 支援自訂參數
- ✅ 快速預設策略
- ✅ 零結果問題已修復

#### 方法2: 原始完整GUI
```bash
python main.py
```
- 訪問: http://127.0.0.1:7860
- 固定參數設定

### 📊 使用流程

1. **選擇分析模式**
   - 🧬 基因演算法分析
   - 🔄 批次分析
   - 🔍 系統狀態檢查

2. **設定參數**
   - 選擇預設策略 (保守/平衡/積極)
   - 或自訂所有參數

3. **執行分析**
   - 選擇產業和股票
   - 點擊「開始分析」
   - 等待結果生成

## ⚙️ 核心模組

### 🧬 ga_optimizer.py
基因演算法核心引擎
```python
from ga_optimizer import GeneticAlgorithm, TradingParameters

# 創建參數
params = TradingParameters(
    m_intervals=12,           # 移動平均間隔
    hold_days=2,             # 持有天數
    target_profit_ratio=0.015, # 目標利潤比 (1.5%)
    alpha=0.6                # α門檻 (0.6%)
)

# 執行優化
ga = GeneticAlgorithm(data)
result = ga.evolve()
```

### 💾 db_connector.py
數據庫連接和操作
```python
from db_connector import DBConnector

db = DBConnector()
industries = db.get_industry_list()      # 獲取產業列表
stocks = db.get_stocks_by_industry("電子")  # 獲取股票列表
data = db.read_stock_data("2330TSE")     # 讀取股票數據
```

### 🔍 診斷工具
```bash
# 綜合系統診斷
python comprehensive_diagnostic.py

# 真實數據診斷
python real_data_diagnostic.py

# 零結果問題診斷
python zero_results_diagnostic.py

# 價格質量檢查
python price_quality_checker.py
```

## 📐 參數說明

### 🔧 交易參數

| 參數 | 說明 | 建議範圍 | 預設值 |
|------|------|----------|--------|
| `m_intervals` | 移動平均計算期間 | 8-20 | 12 |
| `hold_days` | 股票持有天數 | 1-5 | 2 |
| `target_profit_ratio` | 目標利潤比例 | 1.5%-3% | 1.5% |
| `alpha` | 買賣信號門檻 | 0.5%-1.5% | 0.6% |

### 🧬 演算法參數

| 參數 | 說明 | 建議值 |
|------|------|--------|
| `population_size` | 族群大小 | 50 |
| `generations` | 最大世代數 | 50 |
| `mutation_rate` | 突變率 | 0.1 |
| `crossover_rate` | 交配率 | 0.8 |

### 🛑 停止條件

| 條件 | 說明 | 預設值 |
|------|------|--------|
| `max_time_minutes` | 最大執行時間 | 5分鐘 |
| `convergence_threshold` | 收斂閾值 | 0.001 |
| `convergence_generations` | 收斂判斷世代數 | 8 |

## 🎯 快速預設策略

### 🛡️ 保守策略
```python
TradingParameters(
    m_intervals=15,    # 較長移動平均
    hold_days=3,       # 中期持有
    target_profit_ratio=0.02,  # 2%目標
    alpha=0.8         # 0.8%門檻
)
```

### ⚖️ 平衡策略 (推薦)
```python
TradingParameters(
    m_intervals=12,    # 中等移動平均
    hold_days=2,       # 短期持有
    target_profit_ratio=0.015, # 1.5%目標
    alpha=0.6         # 0.6%門檻
)
```

### ⚡ 積極策略
```python
TradingParameters(
    m_intervals=8,     # 短移動平均
    hold_days=2,       # 短期持有
    target_profit_ratio=0.025, # 2.5%目標
    alpha=1.0         # 1.0%門檻
)
```

## 🔧 故障排除

### ❌ 常見問題

#### 1. 零結果問題 (總利潤$0.00, 勝率0%)
**症狀**: 所有績效指標都是零
**原因**: 參數設定導致無法產生交易信號
**解決方案**:
```bash
# 運行診斷工具
python zero_results_diagnostic.py

# 使用修復工具
python fix_zero_results.py

# 使用改進版GUI
python improved_gui.py
```

#### 2. 數據庫連接失敗
**症狀**: `資料庫未連接`
**解決方案**:
```bash
# 檢查SQL Server服務
# 驗證連接設定
python check_bestparams_table.py
```

#### 3. α參數超出範圍 (α > 1)
**症狀**: `門檻α: 1.764 不可能大於1`
**解決方案**: 已修復，α現在正確表示為百分比 (0.5%-99%)

#### 4. BOM字符錯誤
**症狀**: Unicode BOM字符導致欄位識別失敗
**解決方案**: 系統已自動處理BOM字符

### 🩺 診斷命令

```bash
# 完整系統診斷
python comprehensive_diagnostic.py

# 檢查真實數據質量
python real_data_diagnostic.py

# 檢查價格變化合理性
python price_quality_checker.py

# 測試極端參數
python test_extreme_target.py
```

## 🆕 最新改進

### ✅ v2.0 主要更新 (2025年7月)

#### 🐛 問題修復
- ✅ **零結果問題**: 完全解決總利潤$0.00的問題
- ✅ **α參數範圍**: 修正α>1的顯示錯誤
- ✅ **目標利潤比**: 移除不合理的上限限制
- ✅ **BOM字符處理**: 自動清理Unicode BOM
- ✅ **錯誤分級**: 區分系統錯誤與策略表現

#### 🚀 功能增強
- 🆕 **改進版GUI**: 支援自訂參數和快速預設
- 🆕 **價格質量檢查**: 驗證價格變化合理性(-100%~+100%)
- 🆕 **智能預設值**: 基於實際測試的最佳參數
- 🆕 **診斷工具集**: 完整的問題診斷和修復工具
- 🆕 **參數驗證**: 實時參數合理性檢查

#### 📊 性能優化
- ⚡ **更快收斂**: 優化的停止條件
- ⚡ **更好的預設值**: 實測最佳參數組合
- ⚡ **錯誤處理**: 完善的異常處理機制

### 🎯 測試驗證
基於真實股票數據(2891BTW)的測試結果：
- **平衡策略**: 適應度2.96, 勝率35.3% ✅
- **數據質量**: 100%合理變化，優秀數據質量 ✅
- **零結果修復**: 所有測試案例正常運作 ✅

## 📊 績效指標說明

### 📈 適應度函數
```
適應度 = 利潤分數 + 勝率分數 - 回撤懲罰

利潤分數 = 總利潤 * 25000  # 放大利潤影響
勝率分數 = 勝率 * 20        # 勝率權重
回撤懲罰 = 最大回撤 * 10    # 風險控制
```

### 📊 評估標準
- **優秀**: 適應度 > 5.0
- **良好**: 適應度 2.0-5.0
- **尚可**: 適應度 0-2.0
- **需改進**: 適應度 < 0

### ⚠️ 錯誤代碼
- **-10.0000**: 系統錯誤 (數據問題)
- **-5.0000**: 參數錯誤 (設定問題)
- **負值**: 策略表現差但正常

## 🔬 數據質量標準

### 📊 價格變化合理性
- **優秀**: 99%以上變化在±100%範圍內
- **良好**: 95-99%合理變化
- **有問題**: <95%合理變化

### 📈 數據要求
- **最少筆數**: 100筆以上
- **欄位完整**: 必需Date, Close欄位
- **數值有效**: 無NaN或無效數值
- **時間連續**: 合理的時間序列

## 📱 界面功能

### 🖥️ 改進版GUI功能
1. **📋 快速預設**: 一鍵選擇最佳策略
2. **🎛️ 自訂參數**: 完全自由調整所有參數
3. **🔍 實時驗證**: 參數合理性即時檢查
4. **📊 詳細結果**: 完整的分析報告
5. **🩺 診斷頁面**: 問題診斷和修復建議

### 📊 分析報告內容
- 📈 **績效指標**: 利潤、勝率、回撤、夏普比率
- 🔧 **最佳參數**: 優化後的交易參數
- 📊 **數據分析**: 訓練/測試數據統計
- 🛑 **停止原因**: 演化終止條件
- 📈 **視覺圖表**: 演化過程曲線

## 🤝 貢獻指南

### 🛠️ 開發環境設定
```bash
# 克隆專案
git clone https://github.com/onlyforthesis/ga_trading_optimizer_sql_industry.git

# 安裝開發依賴
pip install -r requirements.txt

# 運行測試
python -m pytest tests/
```

### 📝 代碼風格
- 使用中文註解和變數名
- 遵循PEP 8代碼風格
- 添加類型提示 (Type Hints)
- 編寫單元測試

### 🐛 問題回報
1. 檢查是否為已知問題
2. 提供詳細的錯誤訊息
3. 包含重現步驟
4. 標注作業系統和Python版本

## 📄 授權條款

本專案採用 MIT 授權條款 - 詳見 [LICENSE](LICENSE) 檔案

## 👥 作者

- **主要開發者**: onlyforthesis
- **專案類型**: 論文研究專案
- **聯絡方式**: [GitHub Issues](https://github.com/onlyforthesis/ga_trading_optimizer_sql_industry/issues)

## 🙏 致謝

- 感謝所有貢獻者的參與
- 感謝開源社群的支持
- 特別感謝Gradio、pandas、numpy等優秀開源專案

---

## 📚 快速開始

### 🚀 5分鐘快速體驗

1. **下載並安裝**
```bash
git clone https://github.com/onlyforthesis/ga_trading_optimizer_sql_industry.git
cd ga_trading_optimizer_sql_industry
pip install -r requirements.txt
```

2. **啟動改進版GUI**
```bash
python improved_gui.py
```

3. **開始分析**
- 訪問: http://127.0.0.1:7861
- 選擇「平衡策略」預設
- 選擇產業和股票
- 點擊「開始分析」

**🎉 恭喜！您已經成功運行了基因演算法股票策略最佳化系統！**

---

*最後更新: 2025年7月26日*
*版本: v2.0*
*狀態: 穩定版本，零結果問題已修復* ✅
