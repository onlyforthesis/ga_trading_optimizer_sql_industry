import numpy as np
import pandas as pd
import random
from dataclasses import dataclass
from typing import List

@dataclass
class TradingParameters:
    m_intervals: int
    hold_days: int
    target_profit_ratio: float
    alpha: float

@dataclass
class TradingResult:
    parameters: TradingParameters
    fitness: float
    total_profit: float
    win_rate: float
    max_drawdown: float
    sharpe_ratio: float = 0.0
    test_result: 'TradingResult' = None  # 測試數據結果

class GeneticAlgorithm:
    def __init__(self, data: pd.DataFrame, population_size: int = 50, generations: int = 100, 
                 mutation_rate: float = 0.1, crossover_rate: float = 0.8,
                 max_time_minutes: float = 10.0, convergence_threshold: float = 1e-6,
                 convergence_generations: int = 10):
        self.original_data = data.copy()
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        
        # 數據分割：2019-2023訓練，2024測試
        self.train_data, self.test_data = self.split_train_test_data(data)
        self.data = self.train_data  # 預設使用訓練數據
        
        # 新增停止條件參數
        self.max_time_minutes = max_time_minutes
        self.convergence_threshold = convergence_threshold  # 適應度變異閾值
        self.convergence_generations = convergence_generations  # 判斷收斂的世代數
        
        # 記錄適應度歷史
        self.best_fitness_history = []
        self.avg_fitness_history = []
        
        # 停止條件狀態
        self.stop_reason = ""
        
        # 參數範圍
        self.param_ranges = {
            'm_intervals': (5, 50),
            'hold_days': (1, 30),
            'target_profit_ratio': (0.02, float('inf')),  # 調整為2%到無上限
            'alpha': (0.5, 99.0)  # α代表門檻百分比，0.5%到99%之間
        }
    
    def split_train_test_data(self, data):
        """分割訓練和測試數據：2019-2023訓練，2024測試"""
        try:
            # 處理欄位名稱中的BOM字符
            data.columns = data.columns.str.replace('\ufeff', '', regex=False)
            
            print(f"📊 原始數據: {len(data)} 筆, 欄位: {list(data.columns)}")
            
            # 找到日期欄位
            date_column = None
            for col in ['Date', 'date', '日期', 'DATE', 'DateTime', 'Time']:
                if col in data.columns:
                    date_column = col
                    break
            
            if date_column is None:
                print("⚠️ 警告: 沒有找到日期欄位，使用全部資料作為訓練資料")
                return data.copy(), pd.DataFrame()
            
            # 確保Date欄位為datetime類型
            data[date_column] = pd.to_datetime(data[date_column], errors='coerce')
            
            # 移除無效日期
            data = data.dropna(subset=[date_column])
            
            if len(data) == 0:
                print("❌ 日期轉換後資料為空")
                return pd.DataFrame(), pd.DataFrame()
            
            data_sorted = data.sort_values(date_column).reset_index(drop=True)
            
            # 檢查日期範圍
            min_date = data_sorted[date_column].min()
            max_date = data_sorted[date_column].max()
            print(f"📅 資料日期範圍: {min_date.strftime('%Y-%m-%d')} 到 {max_date.strftime('%Y-%m-%d')}")
            
            # 分割數據
            train_data = data_sorted[data_sorted[date_column].dt.year.between(2019, 2023)].copy()
            test_data = data_sorted[data_sorted[date_column].dt.year == 2024].copy()
            
            print(f"📊 數據分割完成:")
            print(f"   訓練數據 (2019-2023): {len(train_data)} 筆")
            print(f"   測試數據 (2024): {len(test_data)} 筆")
            
            if len(train_data) == 0:
                print("⚠️ 警告: 2019-2023年訓練數據為空，使用全部數據的前80%作為訓練")
                split_point = int(len(data_sorted) * 0.8)
                train_data = data_sorted[:split_point].copy()
                test_data = data_sorted[split_point:].copy()
                print(f"📊 重新分割: 訓練 {len(train_data)} 筆, 測試 {len(test_data)} 筆")
            
            if len(test_data) == 0:
                print("⚠️ 警告: 2024年測試數據為空")
            
            return train_data, test_data
            
        except Exception as e:
            print(f"❌ 數據分割失敗: {e}")
            print("使用全部數據作為訓練數據")
            return data.copy(), pd.DataFrame()
    
    def create_random_individual(self) -> TradingParameters:
        """創建隨機個體 - 增強多樣性"""
        # 對於target_profit_ratio，使用實際的合理上限進行隨機生成
        max_target_ratio = 1.0  # 100%作為實際生成的上限
        
        return TradingParameters(
            m_intervals=random.randint(*self.param_ranges['m_intervals']),
            hold_days=random.randint(*self.param_ranges['hold_days']),
            target_profit_ratio=round(random.uniform(self.param_ranges['target_profit_ratio'][0], max_target_ratio), 4),
            alpha=round(random.uniform(*self.param_ranges['alpha']), 3)
        )
    
    def check_convergence(self) -> bool:
        """檢查種群是否已收斂"""
        if len(self.best_fitness_history) < self.convergence_generations:
            return False
        
        # 取最近的幾個世代的最佳適應度
        recent_fitness = self.best_fitness_history[-self.convergence_generations:]
        
        # 計算適應度變異（標準差）
        fitness_variance = np.std(recent_fitness)
        
        # 如果變異小於閾值，認為已收斂
        return fitness_variance < self.convergence_threshold
    
    def check_time_limit(self, start_time) -> bool:
        """檢查是否超過時間限制"""
        import time
        elapsed_minutes = (time.time() - start_time) / 60
        return elapsed_minutes >= self.max_time_minutes
    
    def evaluate_fitness(self, params: TradingParameters) -> TradingResult:
        """評估個體適應度"""
        try:
            # 檢查資料是否為空
            if self.data.empty:
                print("⚠️ 評估資料為空")
                return TradingResult(
                    parameters=params,
                    fitness=-10,
                    total_profit=0,
                    win_rate=0,
                    max_drawdown=1.0
                )
            
            # 複製資料並檢查必要欄位
            data = self.data.copy()
            
            # 處理欄位名稱中的BOM字符
            data.columns = data.columns.str.replace('\ufeff', '', regex=False)
            
            print(f"📊 評估資料: {len(data)} 筆, 欄位: {list(data.columns)}")
            
            # 檢查參數合理性
            if params.m_intervals <= 0 or params.hold_days <= 0 or params.target_profit_ratio <= 0 or params.alpha <= 0:
                print(f"❌ 參數不合理: m_intervals={params.m_intervals}, hold_days={params.hold_days}, target_profit_ratio={params.target_profit_ratio}, alpha={params.alpha}")
                return TradingResult(
                    parameters=params,
                    fitness=-8,
                    total_profit=0,
                    win_rate=0,
                    max_drawdown=1.0
                )
            
            # 確定價格欄位（嘗試不同的可能名稱）
            price_column = None
            for col in ['Close', 'close', '收盤價', 'CLOSE', 'Close Price']:
                if col in data.columns:
                    price_column = col
                    break
            
            if price_column is None:
                # 如果沒有找到明確的價格欄位，嘗試使用數值型欄位
                numeric_cols = data.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) > 0:
                    price_column = numeric_cols[-1]  # 使用最後一個數值欄位
                    print(f"⚠️ 未找到Close欄位，使用 {price_column} 作為價格")
                else:
                    print("❌ 無法找到價格欄位")
                    return TradingResult(
                        parameters=params,
                        fitness=-10,
                        total_profit=0,
                        win_rate=0,
                        max_drawdown=1.0
                    )
            
            # 確保價格欄位為數值型
            try:
                data[price_column] = pd.to_numeric(data[price_column], errors='coerce')
                print(f"✅ 價格數據轉換為數值型")
            except Exception as e:
                print(f"❌ 價格數據轉換失敗: {e}")
                return TradingResult(
                    parameters=params,
                    fitness=-10,
                    total_profit=0,
                    win_rate=0,
                    max_drawdown=1.0
                )
            
            # 確保資料中沒有NaN值
            data = data.dropna(subset=[price_column])
            if len(data) < params.m_intervals + 10:  # 需要足夠的資料點
                print(f"⚠️ 資料不足: 只有 {len(data)} 筆資料")
                return TradingResult(
                    parameters=params,
                    fitness=-5,
                    total_profit=0,
                    win_rate=0,
                    max_drawdown=1.0
                )
            
            # 計算移動平均
            window = max(1, min(params.m_intervals, len(data) // 2))
            data['MA'] = data[price_column].rolling(window=window).mean()
            
            # 計算交易信號
            data['signal'] = 0
            # α直接代表門檻百分比，例如α=2.5表示2.5%的門檻
            alpha_threshold = params.alpha / 100.0  # 將α轉換為小數形式的百分比
            
            # 檢查α是否過大導致無法交易
            if alpha_threshold > 0.5:  # 如果α超過50%，可能很難產生信號
                print(f"⚠️ 警告: α值過高 ({params.alpha}%)，可能導致交易信號稀少")
            
            # 改進的交易信號計算
            buy_condition = data[price_column] > data['MA'] * (1 + alpha_threshold)
            sell_condition = data[price_column] < data['MA'] * (1 - alpha_threshold)
            
            data.loc[buy_condition, 'signal'] = 1
            data.loc[sell_condition, 'signal'] = -1
            
            buy_signals = (data['signal'] == 1).sum()
            sell_signals = (data['signal'] == -1).sum()
            print(f"🔍 交易信號統計: 買入信號 {buy_signals} 個, 賣出信號 {sell_signals} 個")
            
            # 如果完全沒有買入信號，給予適度懲罰而不是完全失敗
            if buy_signals == 0:
                print("⚠️ 沒有買入信號產生，可能α值設定不當")
                return TradingResult(
                    parameters=params,
                    fitness=-3,  # 較輕的懲罰，讓演算法有機會調整
                    total_profit=0,
                    win_rate=0,
                    max_drawdown=0.1
                )
            
            # 模擬交易
            positions = []
            current_position = None
            total_profit = 0
            wins = 0
            trades = 0
            max_drawdown = 0
            peak_value = 1000  # 初始資金
            current_value = 1000
            
            for i in range(window, len(data)):  # 從移動平均計算完成後開始
                current_price = data.iloc[i][price_column]
                current_signal = data.iloc[i]['signal']
                
                if pd.isna(current_price) or pd.isna(data.iloc[i]['MA']):
                    continue
                
                if current_position is None and current_signal == 1:
                    # 開多倉
                    current_position = {
                        'type': 'long',
                        'entry_price': current_price,
                        'entry_date': i,
                        'target_price': current_price * (1 + params.target_profit_ratio)
                    }
                    
                elif current_position is not None:
                    days_held = i - current_position['entry_date']
                    
                    # 檢查出場條件
                    should_exit = False
                    if current_position['type'] == 'long':
                        if (current_price >= current_position['target_price'] or 
                            days_held >= params.hold_days or 
                            current_signal == -1):
                            should_exit = True
                    
                    if should_exit:
                        # 計算利潤
                        if current_position['type'] == 'long':
                            profit_pct = (current_price - current_position['entry_price']) / current_position['entry_price']
                        
                        total_profit += profit_pct
                        current_value *= (1 + profit_pct)
                        
                        if profit_pct > 0:
                            wins += 1
                        trades += 1
                        
                        # 更新最大回撤
                        if current_value > peak_value:
                            peak_value = current_value
                        drawdown = (peak_value - current_value) / peak_value if peak_value > 0 else 0
                        max_drawdown = max(max_drawdown, drawdown)
                        
                        current_position = None
            
            print(f"💹 交易結果: {trades} 筆交易, 勝率 {wins/trades*100 if trades > 0 else 0:.1f}%, 總利潤 {total_profit:.4f}")
            
            # 計算績效指標
            win_rate = wins / trades if trades > 0 else 0
            avg_profit = total_profit / trades if trades > 0 else 0
            
            # 改進的適應度計算 - 更敏感的多目標優化
            if trades > 0:
                # 基礎收益分數 (放大權重)
                profit_score = avg_profit * 100
                
                # 勝率分數
                winrate_score = win_rate * 20
                
                # 回撤懲罰 (非線性懲罰)
                drawdown_penalty = max_drawdown * max_drawdown * 50
                
                # 交易頻率獎勵 (適度交易)
                trade_frequency = trades / len(data)
                frequency_bonus = min(trade_frequency * 10, 5) if trade_frequency > 0.01 else 0
                
                # 綜合適應度
                fitness = profit_score + winrate_score - drawdown_penalty + frequency_bonus
                
                # 加入隨機擾動避免收斂到局部最優
                fitness += random.uniform(-0.1, 0.1)
                
                print(f"✅ 適應度計算完成: {fitness:.4f} (利潤:{profit_score:.2f}, 勝率:{winrate_score:.2f}, 回撤懲罰:{drawdown_penalty:.2f})")
            else:
                # 無交易時的處理 - 根據α值給予不同程度的懲罰
                if params.alpha > 50:  # α值過高
                    fitness = -2 + random.uniform(-0.5, 0.5)
                    print("⚠️ α值過高導致無交易，輕度懲罰")
                elif params.target_profit_ratio > 0.5:  # 目標利潤過高
                    fitness = -2 + random.uniform(-0.5, 0.5)
                    print("⚠️ 目標利潤過高導致無交易，輕度懲罰")
                else:
                    fitness = -3 + random.uniform(-0.5, 0.5)  # 其他原因無交易
                    print("⚠️ 無交易產生，使用懲罰適應度")
            
            return TradingResult(
                parameters=params,
                fitness=fitness,
                total_profit=total_profit * 1000,  # 轉換為實際金額
                win_rate=win_rate,
                max_drawdown=max_drawdown
            )
            
        except Exception as e:
            # 如果評估失敗，返回負適應度
            print(f"❌ 適應度評估失敗: {e}")
            import traceback
            traceback.print_exc()
            return TradingResult(
                parameters=params,
                fitness=-10,
                total_profit=0,
                win_rate=0,
                max_drawdown=1.0
            )
    
    def evaluate_on_test_data(self, params: TradingParameters) -> TradingResult:
        """在測試數據上評估參數性能"""
        if self.test_data.empty:
            print("⚠️ 測試數據為空，無法進行測試評估")
            return TradingResult(
                parameters=params,
                fitness=0,
                total_profit=0,
                win_rate=0,
                max_drawdown=0
            )
        
        try:
            # 使用測試數據進行評估
            original_data = self.data
            self.data = self.test_data  # 暫時切換到測試數據
            
            # 調用原有的評估方法
            result = self.evaluate_fitness(params)
            
            # 恢復原有數據
            self.data = original_data
            
            return result
            
        except Exception as e:
            print(f"❌ 測試評估失敗: {e}")
            self.data = original_data  # 確保恢復原有數據
            return TradingResult(
                parameters=params,
                fitness=-10,
                total_profit=0,
                win_rate=0,
                max_drawdown=1.0
            )
    
    def crossover(self, parent1: TradingParameters, parent2: TradingParameters) -> TradingParameters:
        """交叉操作 - 改進版"""
        if random.random() > self.crossover_rate:
            return parent1 if random.random() < 0.5 else parent2
        
        # 混合交叉 - 對數值參數進行插值
        alpha_blend = random.uniform(0.3, 0.7)
        
        new_alpha = parent1.alpha * alpha_blend + parent2.alpha * (1 - alpha_blend)
        # 確保alpha值在合理範圍內
        new_alpha = max(self.param_ranges['alpha'][0], min(self.param_ranges['alpha'][1], new_alpha))
        
        return TradingParameters(
            m_intervals=random.choice([parent1.m_intervals, parent2.m_intervals]),
            hold_days=random.choice([parent1.hold_days, parent2.hold_days]),
            target_profit_ratio=parent1.target_profit_ratio * alpha_blend + parent2.target_profit_ratio * (1 - alpha_blend),
            alpha=new_alpha
        )
    
    def mutate(self, individual: TradingParameters) -> TradingParameters:
        """突變操作 - 增強版"""
        # 每個參數都有機會突變
        if random.random() < self.mutation_rate:
            # m_intervals 突變
            if random.random() < 0.25:
                individual.m_intervals = max(self.param_ranges['m_intervals'][0], 
                                           min(self.param_ranges['m_intervals'][1],
                                               individual.m_intervals + random.randint(-8, 8)))
        
        if random.random() < self.mutation_rate:
            # hold_days 突變
            if random.random() < 0.25:
                individual.hold_days = max(self.param_ranges['hold_days'][0],
                                         min(self.param_ranges['hold_days'][1],
                                             individual.hold_days + random.randint(-5, 5)))
        
        if random.random() < self.mutation_rate:
            # target_profit_ratio 突變
            if random.random() < 0.25:
                new_ratio = individual.target_profit_ratio + random.uniform(-0.03, 0.03)
                # 確保不低於下限，無上限
                individual.target_profit_ratio = max(self.param_ranges['target_profit_ratio'][0], new_ratio)
        
        if random.random() < self.mutation_rate:
            # alpha 突變
            if random.random() < 0.25:
                individual.alpha = max(self.param_ranges['alpha'][0],
                                     min(self.param_ranges['alpha'][1],
                                         individual.alpha + random.uniform(-5.0, 5.0)))
                # 確保alpha值在合理範圍內（0.5%到99%）
        
        return individual
    
    def tournament_selection(self, population: List[TradingResult], tournament_size: int = 3) -> TradingParameters:
        """錦標賽選擇"""
        tournament = random.sample(population, min(tournament_size, len(population)))
        winner = max(tournament, key=lambda x: x.fitness)
        return winner.parameters
    
    def evolve(self) -> TradingResult:
        """執行遺傳演算法 - 使用智能停止條件"""
        import time
        
        # 設定隨機種子以確保每次執行都有不同結果
        random.seed()
        np.random.seed()
        
        # 記錄開始時間
        start_time = time.time()
        
        # 初始化族群
        population = []
        for _ in range(self.population_size):
            individual = self.create_random_individual()
            result = self.evaluate_fitness(individual)
            population.append(result)
        
        # 演化過程 - 檢查三個停止條件
        generation = 0
        while generation < self.generations:
            # 記錄當前世代的適應度
            fitnesses = [ind.fitness for ind in population]
            best_fitness = max(fitnesses)
            avg_fitness = sum(fitnesses) / len(fitnesses)
            
            self.best_fitness_history.append(best_fitness)
            self.avg_fitness_history.append(avg_fitness)
            
            # 檢查停止條件
            stop_conditions = []
            
            # 條件1：檢查時間限制
            if self.check_time_limit(start_time):
                self.stop_reason = f"達到時間限制 ({self.max_time_minutes} 分鐘)"
                stop_conditions.append("時間限制")
            
            # 條件2：檢查收斂
            if self.check_convergence():
                self.stop_reason = f"種群已收斂 (適應度變異 < {self.convergence_threshold})"
                stop_conditions.append("種群收斂")
            
            # 條件3：檢查最大世代數
            if generation >= self.generations - 1:
                self.stop_reason = f"達到最大世代數 ({self.generations})"
                stop_conditions.append("最大世代")
            
            # 如果滿足任一停止條件，結束演化
            if stop_conditions:
                print(f"世代 {generation}: 停止演化 - {', '.join(stop_conditions)}")
                print(f"最佳適應度 = {best_fitness:.4f}, 平均適應度 = {avg_fitness:.4f}")
                break
            
            # 選擇、交叉、突變產生新族群
            new_population = []
            
            # 保留最佳個體 (菁英主義)
            best_individual = max(population, key=lambda x: x.fitness)
            new_population.append(best_individual)
            
            # 產生其他個體
            while len(new_population) < self.population_size:
                parent1 = self.tournament_selection(population)
                parent2 = self.tournament_selection(population)
                
                child = self.crossover(parent1, parent2)
                child = self.mutate(child)
                
                child_result = self.evaluate_fitness(child)
                new_population.append(child_result)
            
            population = new_population
            
            # 顯示進度 - 每5世代顯示一次
            if generation % 5 == 0:
                elapsed_minutes = (time.time() - start_time) / 60
                print(f"世代 {generation}: 最佳適應度 = {best_fitness:.4f}, 平均適應度 = {avg_fitness:.4f}, 已用時間 = {elapsed_minutes:.1f}分")
            
            generation += 1
        
        # 獲取最佳結果（基於訓練數據）
        best_result = max(population, key=lambda x: x.fitness)
        total_time = (time.time() - start_time) / 60
        
        # 在測試數據上評估最佳參數
        test_result = self.evaluate_on_test_data(best_result.parameters)
        
        print(f"\n🎉 演化完成!")
        print(f"📊 停止原因: {self.stop_reason}")
        print(f"⏱️  總用時間: {total_time:.2f} 分鐘")
        print(f"🔢 執行世代: {generation + 1} / {self.generations}")
        print(f"📈 訓練數據最佳適應度: {best_result.fitness:.4f}")
        
        if not self.test_data.empty:
            print(f"🧪 測試數據適應度: {test_result.fitness:.4f}")
            print(f"📊 訓練vs測試差異: {best_result.fitness - test_result.fitness:.4f}")
        
        if len(self.best_fitness_history) > 0:
            print(f"📊 適應度改進: {self.best_fitness_history[-1] - self.best_fitness_history[0]:.4f}")
        
        # 將測試結果添加到最佳結果中供後續使用
        best_result.test_result = test_result if not self.test_data.empty else None
        
        return best_result