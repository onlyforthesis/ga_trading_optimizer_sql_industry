"""
加速版遺傳演算法優化器
包含多種加速策略：
1. 並行處理適應度評估
2. 早期停止條件
3. 自適應參數
4. 快速模式配置
"""

import numpy as np
import pandas as pd
import random
import time
from dataclasses import dataclass
from typing import List
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import multiprocessing as mp
from ga_optimizer import TradingParameters, TradingResult, GeneticAlgorithm

class FastGeneticAlgorithm(GeneticAlgorithm):
    """加速版遺傳演算法"""
    
    def __init__(self, data: pd.DataFrame, **kwargs):
        # 設定加速模式的預設參數
        fast_defaults = {
            'population_size': 30,      # 減少族群大小
            'generations': 50,          # 減少世代數
            'max_time_minutes': 2.0,    # 減少時間限制
            'convergence_threshold': 0.01,  # 放寬收斂條件
            'convergence_generations': 5,   # 減少收斂判斷世代數
            'use_parallel': True,       # 啟用並行處理
            'early_stop_patience': 10,  # 早期停止耐心值
            'elite_ratio': 0.2,        # 精英比例
            'adaptive_mutation': True   # 自適應突變
        }
        
        # 合併用戶參數
        for key, value in fast_defaults.items():
            if key not in kwargs:
                kwargs[key] = value
        
        # 提取加速相關參數
        self.use_parallel = kwargs.pop('use_parallel', True)
        self.early_stop_patience = kwargs.pop('early_stop_patience', 10)
        self.elite_ratio = kwargs.pop('elite_ratio', 0.2)
        self.adaptive_mutation = kwargs.pop('adaptive_mutation', True)
        
        super().__init__(data, **kwargs)
        
        # 加速相關狀態
        self.no_improvement_count = 0
        self.best_ever_fitness = -float('inf')
        self.stop_reason = ""  # 初始化停止原因
        
    def parallel_fitness_evaluation(self, population: List[TradingParameters]) -> List[float]:
        """並行評估適應度"""
        if not self.use_parallel or len(population) < 4:
            # 如果不使用並行或族群太小，使用原始方法
            return [self.evaluate_fitness(individual).fitness for individual in population]
        
        try:
            # 使用線程池而不是進程池，避免數據序列化開銷
            with ThreadPoolExecutor(max_workers=min(4, len(population))) as executor:
                fitness_results = list(executor.map(self.evaluate_fitness, population))
                fitness_values = [result.fitness for result in fitness_results]
            return fitness_values
        except Exception as e:
            print(f"⚠️ 並行處理失敗，回退到串行處理: {e}")
            return [self.evaluate_fitness(individual).fitness for individual in population]
    
    def adaptive_mutation_rate(self, generation: int) -> float:
        """自適應突變率"""
        if not self.adaptive_mutation:
            return self.mutation_rate
        
        # 隨著世代增加，逐漸降低突變率
        base_rate = self.mutation_rate
        decay_factor = 0.95
        return max(0.05, base_rate * (decay_factor ** generation))
    
    def elite_selection(self, population: List[TradingParameters], fitness_values: List[float]) -> List[TradingParameters]:
        """精英選擇 - 保留最好的個體"""
        if not fitness_values:
            return []
        
        # 計算精英數量
        elite_count = max(1, int(len(population) * self.elite_ratio))
        
        # 配對並排序
        paired = list(zip(population, fitness_values))
        paired.sort(key=lambda x: x[1], reverse=True)  # 降序排列
        
        # 返回精英個體
        return [individual for individual, _ in paired[:elite_count]]
    
    def check_early_stop(self, current_best_fitness: float) -> bool:
        """檢查早期停止條件"""
        if current_best_fitness > self.best_ever_fitness:
            self.best_ever_fitness = current_best_fitness
            self.no_improvement_count = 0
            return False
        else:
            self.no_improvement_count += 1
            return self.no_improvement_count >= self.early_stop_patience
    
    def tournament_selection_fast(self, population: List[TradingParameters], fitness_values: List[float], tournament_size: int = 3) -> TradingParameters:
        """快速錦標賽選擇 - 適合加速版本"""
        if not population or not fitness_values:
            return self.create_random_individual()
        
        # 隨機選擇錦標賽參與者
        tournament_indices = random.sample(range(len(population)), min(tournament_size, len(population)))
        
        # 找到適應度最高的個體
        best_index = max(tournament_indices, key=lambda i: fitness_values[i])
        return population[best_index]

    def crossover_fast(self, parent1: TradingParameters, parent2: TradingParameters) -> tuple:
        """快速交叉操作 - 返回兩個子代"""
        if random.random() > self.crossover_rate:
            return parent1, parent2
        
        # 混合交叉 - 對數值參數進行插值
        alpha_blend1 = random.uniform(0.3, 0.7)
        alpha_blend2 = 1 - alpha_blend1
        
        child1 = TradingParameters(
            m_intervals=random.choice([parent1.m_intervals, parent2.m_intervals]),
            hold_days=random.choice([parent1.hold_days, parent2.hold_days]),
            target_profit_ratio=parent1.target_profit_ratio * alpha_blend1 + parent2.target_profit_ratio * alpha_blend2,
            alpha=max(self.param_ranges['alpha'][0], 
                     min(self.param_ranges['alpha'][1],
                         parent1.alpha * alpha_blend1 + parent2.alpha * alpha_blend2))
        )
        
        child2 = TradingParameters(
            m_intervals=random.choice([parent1.m_intervals, parent2.m_intervals]),
            hold_days=random.choice([parent1.hold_days, parent2.hold_days]),
            target_profit_ratio=parent1.target_profit_ratio * alpha_blend2 + parent2.target_profit_ratio * alpha_blend1,
            alpha=max(self.param_ranges['alpha'][0], 
                     min(self.param_ranges['alpha'][1],
                         parent1.alpha * alpha_blend2 + parent2.alpha * alpha_blend1))
        )
        
        return child1, child2

    def evolve(self) -> TradingResult:
        """加速版演化過程"""
        print(f"🚀 啟動加速版遺傳演算法優化")
        print(f"📊 參數: 族群={self.population_size}, 世代={self.generations}, 並行={self.use_parallel}")
        
        start_time = time.time()
        
        # 初始化族群
        population = [self.create_random_individual() for _ in range(self.population_size)]
        
        best_individual = None
        best_fitness = -float('inf')
        
        for generation in range(self.generations):
            generation_start = time.time()
            
            # 並行評估適應度
            fitness_values = self.parallel_fitness_evaluation(population)
            
            # 記錄最佳適應度
            current_best_fitness = max(fitness_values) if fitness_values else -float('inf')
            current_avg_fitness = np.mean(fitness_values) if fitness_values else 0
            
            self.best_fitness_history.append(current_best_fitness)
            self.avg_fitness_history.append(current_avg_fitness)
            
            # 更新全局最佳
            if current_best_fitness > best_fitness:
                best_fitness = current_best_fitness
                best_individual = population[fitness_values.index(current_best_fitness)]
            
            generation_time = time.time() - generation_start
            print(f"世代 {generation+1}/{self.generations}: 最佳適應度={current_best_fitness:.4f}, "
                  f"平均適應度={current_avg_fitness:.4f}, 耗時={generation_time:.2f}秒")
            
            # 檢查停止條件
            if self.check_time_limit(start_time):
                self.stop_reason = f"超過時間限制 ({self.max_time_minutes} 分鐘)"
                print(f"⏰ {self.stop_reason}")
                break
            
            if self.check_convergence():
                self.stop_reason = f"達到收斂條件 (變異 < {self.convergence_threshold})"
                print(f"🎯 {self.stop_reason}")
                break
            
            if self.check_early_stop(current_best_fitness):
                self.stop_reason = f"早期停止 ({self.early_stop_patience} 世代無改善)"
                print(f"⏹️ {self.stop_reason}")
                break
            
            # 選擇、交叉、突變
            if generation < self.generations - 1:  # 不是最後一世代
                # 精英選擇
                elites = self.elite_selection(population, fitness_values)
                
                # 生成新世代
                new_population = elites.copy()  # 保留精英
                
                # 自適應突變率
                current_mutation_rate = self.adaptive_mutation_rate(generation)
                
                while len(new_population) < self.population_size:
                    # 選擇父母
                    parent1 = self.tournament_selection_fast(population, fitness_values)
                    parent2 = self.tournament_selection_fast(population, fitness_values)
                    
                    # 交叉
                    if random.random() < self.crossover_rate:
                        child1, child2 = self.crossover_fast(parent1, parent2)
                    else:
                        child1, child2 = parent1, parent2
                    
                    # 突變
                    if random.random() < current_mutation_rate:
                        child1 = self.mutate(child1)
                    if random.random() < current_mutation_rate:
                        child2 = self.mutate(child2)
                    
                    new_population.extend([child1, child2])
                
                population = new_population[:self.population_size]
        
        # 計算最終結果
        if best_individual:
            final_result = self.evaluate_fitness(best_individual)
            total_time = (time.time() - start_time) / 60
            print(f"✅ 優化完成！總耗時: {total_time:.2f} 分鐘")
            print(f"🎯 停止原因: {self.stop_reason}")
            return final_result
        else:
            print("❌ 優化失敗")
            return TradingResult(
                parameters=TradingParameters(5, 3, 0.03, 0.02),
                fitness=-1,
                total_profit=0,
                win_rate=0,
                max_drawdown=0.1,
                sharpe_ratio=0.0
            )

def create_speed_preset(speed_mode: str) -> dict:
    """創建速度預設配置"""
    presets = {
        'ultra_fast': {
            'population_size': 20,
            'generations': 30,
            'max_time_minutes': 1.0,
            'convergence_threshold': 0.02,
            'convergence_generations': 3,
            'early_stop_patience': 5,
            'use_parallel': True
        },
        'fast': {
            'population_size': 30,
            'generations': 50,
            'max_time_minutes': 2.0,
            'convergence_threshold': 0.01,
            'convergence_generations': 5,
            'early_stop_patience': 8,
            'use_parallel': True
        },
        'balanced': {
            'population_size': 40,
            'generations': 75,
            'max_time_minutes': 3.0,
            'convergence_threshold': 0.005,
            'convergence_generations': 8,
            'early_stop_patience': 10,
            'use_parallel': True
        },
        'quality': {
            'population_size': 50,
            'generations': 100,
            'max_time_minutes': 5.0,
            'convergence_threshold': 0.001,
            'convergence_generations': 10,
            'early_stop_patience': 15,
            'use_parallel': True
        }
    }
    
    return presets.get(speed_mode, presets['balanced'])

# 便利函數
def fast_optimize(data: pd.DataFrame, speed_mode: str = 'fast') -> TradingResult:
    """快速優化便利函數"""
    config = create_speed_preset(speed_mode)
    
    # 所有模式都使用 FastGeneticAlgorithm，不再使用 UltraFastGeneticAlgorithm
    optimizer = FastGeneticAlgorithm(data, **config)
    return optimizer.evolve()

if __name__ == "__main__":
    # 測試不同速度模式
    print("🧪 測試加速版遺傳演算法")
    
    # 這裡需要實際的股票數據來測試
    # data = load_test_data()  # 需要實現
    # 
    # print("\n⚡ 超高速模式測試:")
    # result = fast_optimize(data, 'ultra_fast')
    # print(f"結果: 適應度={result.fitness:.4f}")
    # 
    # print("\n🚀 快速模式測試:")
    # result = fast_optimize(data, 'fast')
    # print(f"結果: 適應度={result.fitness:.4f}")
