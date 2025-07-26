import pyodbc
import pandas as pd

class DBConnector:
    def __init__(self, server="DESKTOP-TOB09L9", database="StockDB"):
        self.server = server
        self.database = database
        self.conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;"
        
        try:
            self.conn = pyodbc.connect(self.conn_str)
            print(f"成功連接到資料庫: {server}\\{database}")
        except pyodbc.Error as e:
            print(f"資料庫連接失敗: {e}")
            print(f"連接字串: {self.conn_str}")
            raise e

    def get_all_stock_tables(self):
        """獲取所有股票資料表，排除系統表和非股票表"""
        query = "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE'"
        all_tables = [row[0] for row in self.conn.cursor().execute(query).fetchall()]
        
        # 系統表和非股票表的黑名單
        exclude_tables = {
            'bestparameters', 'stockindustry', 'sysdiagrams', 
            'dtproperties', 'MSreplication_options', 'sysmergesubscriptions',
            'sysmergearticles', 'sysmergeschemachange', 'sysmergehistory',
            'sysmergeconflicts', 'syscategories', 'sysdac_instances',
            'sysssislog', 'sysssispackagefolders', 'sysssispackages'
        }
        
        # 過濾表格：只保留股票代碼格式的表 (如：1101TW台泥)
        stock_tables = []
        for table in all_tables:
            if table.lower() not in exclude_tables:
                # 檢查是否是股票代碼格式 (數字開頭的表)
                if table and len(table) > 4 and table[:4].isdigit():
                    stock_tables.append(table)
        
        return stock_tables

    def read_stock_data(self, table_name):
        """讀取股票資料，包含錯誤處理"""
        try:
            # 先檢查表格是否存在必要的欄位
            if not self.validate_stock_table(table_name):
                raise ValueError(f"表格 {table_name} 不是有效的股票資料表")
                
            query = f"SELECT * FROM [{table_name}] ORDER BY Date"
            return pd.read_sql(query, self.conn)
        except Exception as e:
            print(f"讀取股票資料失敗 {table_name}: {e}")
            return pd.DataFrame()  # 返回空的 DataFrame
    
    def validate_stock_table(self, table_name):
        """驗證表格是否為有效的股票資料表"""
        try:
            # 檢查表格是否存在Date欄位
            query = f"""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = '{table_name}' AND COLUMN_NAME = 'Date'
            """
            cursor = self.conn.cursor()
            result = cursor.execute(query).fetchone()
            return result is not None
        except:
            return False

    def get_stock_info(self, stock_code):
        query = f"SELECT TOP 1 * FROM StockIndustry WHERE StockCode='{stock_code}'"
        cursor = self.conn.cursor()
        row = cursor.execute(query).fetchone()
        if row:
            return {"StockCode": row[0], "StockName": row[1], "Industry": row[2]}
        return None

    def get_industry_list(self):
        query = "SELECT DISTINCT Industry FROM StockIndustry"
        return [row[0] for row in self.conn.cursor().execute(query).fetchall()]

    def get_stocks_by_industry(self, industry):
        query = f"SELECT StockCode, StockName FROM StockIndustry WHERE Industry='{industry}'"
        results = self.conn.cursor().execute(query).fetchall()
        # 返回格式為 "股票代碼+股票名稱" 的表名稱列表
        return [f"{row[0]}{row[1]}" for row in results]
    
    def extract_stock_code_from_table_name(self, table_name):
        """從表名稱中提取股票代碼"""
        # 假設表名格式為 "1101TW台泥"，我們需要提取 "1101TW" 部分
        import re
        match = re.match(r'^(\d+TW)', table_name)
        return match.group(1) if match else table_name

    def create_best_params_table(self):
        query = '''
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='BestParameters' AND xtype='U')
        CREATE TABLE BestParameters (
            Id INT IDENTITY(1,1) PRIMARY KEY,
            StockCode NVARCHAR(50),
            StockName NVARCHAR(50),
            Industry NVARCHAR(50),
            BestIntervals INT,
            HoldDays INT,
            TargetProfitRatio FLOAT,
            Alpha FLOAT,
            TotalProfit FLOAT,
            WinRate FLOAT,
            MaxDrawdown FLOAT,
            SharpeRatio FLOAT,
            Fitness FLOAT,
            CreateTime DATETIME DEFAULT GETDATE()
        )'''
        self.conn.cursor().execute(query)
        self.conn.commit()

    def save_best_params(self, table_name, result, industry):
        # 從表名稱中提取股票代碼
        stock_code = self.extract_stock_code_from_table_name(table_name)
        info = self.get_stock_info(stock_code)
        stock_name = info['StockName'] if info else "未知"
        query = '''
        INSERT INTO BestParameters
        (StockCode, StockName, Industry, BestIntervals, HoldDays, TargetProfitRatio, Alpha, TotalProfit, WinRate, MaxDrawdown, SharpeRatio, Fitness)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        params = (stock_code, stock_name, industry,
                  result.parameters.m_intervals, result.parameters.hold_days, result.parameters.target_profit_ratio,
                  result.parameters.alpha, result.total_profit, result.win_rate, result.max_drawdown, result.sharpe_ratio, result.fitness)
        self.conn.cursor().execute(query, params)
        self.conn.commit()
