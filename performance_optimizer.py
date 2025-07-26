"""
高性能系統配置優化器
自動檢測和優化系統配置以獲得最佳數據處理性能
"""

import multiprocessing as mp
import psutil
import platform
import os
import sys
import time
from pathlib import Path

class PerformanceOptimizer:
    def __init__(self):
        self.cpu_count = mp.cpu_count()
        self.memory_gb = psutil.virtual_memory().total / (1024**3)
        self.system_info = self.get_system_info()
    
    def get_system_info(self):
        """獲取系統信息"""
        return {
            'platform': platform.system(),
            'processor': platform.processor(),
            'architecture': platform.architecture()[0],
            'python_version': sys.version,
            'cpu_count': self.cpu_count,
            'memory_gb': round(self.memory_gb, 2),
            'cpu_freq': psutil.cpu_freq().max if psutil.cpu_freq() else 'Unknown'
        }
    
    def print_system_analysis(self):
        """分析並顯示系統配置"""
        print("🖥️  系統性能分析")
        print("=" * 60)
        
        info = self.system_info
        print(f"操作系統: {info['platform']} ({info['architecture']})")
        print(f"處理器: {info['processor']}")
        print(f"CPU 核心數: {info['cpu_count']}")
        print(f"記憶體: {info['memory_gb']:.1f} GB")
        if info['cpu_freq'] != 'Unknown':
            print(f"CPU 最高頻率: {info['cpu_freq']:.0f} MHz")
        
        # CPU 使用率
        cpu_percent = psutil.cpu_percent(interval=1)
        memory_percent = psutil.virtual_memory().percent
        
        print(f"\n📊 當前系統狀態:")
        print(f"CPU 使用率: {cpu_percent:.1f}%")
        print(f"記憶體使用率: {memory_percent:.1f}%")
        
        # 性能評估
        print(f"\n⚡ 性能評估:")
        if info['cpu_count'] >= 8:
            print("✅ CPU 核心數充足 (≥8核)")
        elif info['cpu_count'] >= 4:
            print("🟡 CPU 核心數適中 (4-7核)")
        else:
            print("🔴 CPU 核心數較少 (<4核)")
        
        if info['memory_gb'] >= 16:
            print("✅ 記憶體充足 (≥16GB)")
        elif info['memory_gb'] >= 8:
            print("🟡 記憶體適中 (8-15GB)")
        else:
            print("🔴 記憶體較少 (<8GB)")
    
    def get_optimal_workers(self, task_type='cpu_intensive'):
        """計算最佳工作進程數"""
        if task_type == 'cpu_intensive':
            # CPU密集型任務：使用所有核心，但留一個給系統
            optimal = max(1, self.cpu_count - 1)
        elif task_type == 'mixed':
            # 混合任務：使用核心數的75%
            optimal = max(1, int(self.cpu_count * 0.75))
        elif task_type == 'memory_intensive':
            # 記憶體密集型：根據記憶體限制工作數
            optimal = max(1, min(self.cpu_count, int(self.memory_gb // 2)))
        else:
            optimal = self.cpu_count
        
        # 根據記憶體進一步限制
        if self.memory_gb < 8:
            optimal = min(optimal, 2)
        elif self.memory_gb < 16:
            optimal = min(optimal, 4)
        
        return optimal
    
    def get_performance_config(self):
        """獲取性能優化配置"""
        config = {
            'max_workers_cpu_intensive': self.get_optimal_workers('cpu_intensive'),
            'max_workers_mixed': self.get_optimal_workers('mixed'),
            'max_workers_memory_intensive': self.get_optimal_workers('memory_intensive'),
            'chunk_size': max(1, self.cpu_count * 2),
            'memory_limit_mb': int(self.memory_gb * 1024 * 0.8),  # 使用80%記憶體
            'enable_parallel': self.cpu_count > 1,
            'recommended_batch_size': self.get_recommended_batch_size()
        }
        
        return config
    
    def get_recommended_batch_size(self):
        """根據系統配置推薦批次大小"""
        if self.cpu_count >= 8 and self.memory_gb >= 16:
            return 10  # 高端系統可以處理更大批次
        elif self.cpu_count >= 4 and self.memory_gb >= 8:
            return 5   # 中端系統
        else:
            return 2   # 低端系統

def create_optimized_batch_config():
    """創建優化的批次處理配置"""
    optimizer = PerformanceOptimizer()
    config = optimizer.get_performance_config()
    
    print("🚀 生成優化配置...")
    optimizer.print_system_analysis()
    
    print(f"\n⚙️  推薦配置:")
    print("=" * 60)
    print(f"CPU密集型最大工作進程: {config['max_workers_cpu_intensive']}")
    print(f"混合型最大工作進程: {config['max_workers_mixed']}")
    print(f"記憶體密集型最大工作進程: {config['max_workers_memory_intensive']}")
    print(f"推薦批次大小: {config['recommended_batch_size']} 檔股票同時處理")
    print(f"記憶體限制: {config['memory_limit_mb']} MB")
    print(f"並行處理: {'啟用' if config['enable_parallel'] else '禁用'}")
    
    return config

def benchmark_system():
    """系統性能基準測試"""
    print("\n🏃‍♂️ 執行系統基準測試...")
    
    # CPU 基準測試
    print("測試 CPU 性能...")
    start_time = time.time()
    
    # 簡單的 CPU 密集型計算
    def cpu_task(n):
        return sum(i * i for i in range(n))
    
    # 單線程測試
    single_thread_time = time.time()
    result = cpu_task(100000)
    single_thread_time = time.time() - single_thread_time
    
    # 多線程測試
    multi_thread_time = time.time()
    with mp.Pool(processes=mp.cpu_count()) as pool:
        tasks = [25000] * mp.cpu_count()
        results = pool.map(cpu_task, tasks)
    multi_thread_time = time.time() - multi_thread_time
    
    speedup = single_thread_time / multi_thread_time if multi_thread_time > 0 else 1
    
    print(f"單線程耗時: {single_thread_time:.3f} 秒")
    print(f"多線程耗時: {multi_thread_time:.3f} 秒")
    print(f"加速比: {speedup:.2f}x")
    
    # 記憶體測試
    print("測試記憶體性能...")
    memory_start = time.time()
    
    # 創建大數組測試記憶體速度
    import numpy as np
    size = min(10000000, int(psutil.virtual_memory().available / 8 / 10))  # 安全大小
    arr = np.random.randn(size)
    memory_operations = np.sum(arr ** 2)
    memory_time = time.time() - memory_start
    
    print(f"記憶體操作耗時: {memory_time:.3f} 秒")
    print(f"處理速度: {size/memory_time/1000000:.2f} M元素/秒")
    
    return {
        'cpu_single_thread_time': single_thread_time,
        'cpu_multi_thread_time': multi_thread_time,
        'cpu_speedup': speedup,
        'memory_time': memory_time,
        'memory_throughput': size/memory_time/1000000
    }

def optimize_python_environment():
    """優化 Python 環境設置"""
    print("\n🐍 Python 環境優化建議:")
    print("=" * 60)
    
    # 檢查 Python 版本
    python_version = sys.version_info
    if python_version >= (3, 8):
        print("✅ Python 版本良好 (≥3.8)")
    else:
        print("🔴 建議升級 Python 版本到 3.8+")
    
    # 檢查重要套件
    important_packages = {
        'numpy': '數值計算加速',
        'pandas': '數據處理優化', 
        'numba': 'JIT 編譯加速',
        'multiprocessing': '並行處理',
        'concurrent.futures': '併發執行'
    }
    
    print("\n📦 重要套件檢查:")
    for package, description in important_packages.items():
        try:
            __import__(package)
            print(f"✅ {package}: {description}")
        except ImportError:
            print(f"❌ {package}: {description} (未安裝)")
    
    # 環境變量建議
    print("\n🔧 環境變量優化建議:")
    env_vars = {
        'OMP_NUM_THREADS': str(mp.cpu_count()),
        'NUMBA_NUM_THREADS': str(mp.cpu_count()),
        'MKL_NUM_THREADS': str(mp.cpu_count()),
        'OPENBLAS_NUM_THREADS': str(mp.cpu_count())
    }
    
    for var, value in env_vars.items():
        current = os.environ.get(var, '未設定')
        print(f"{var}: 當前={current}, 建議={value}")

def create_performance_script():
    """創建性能優化啟動腳本"""
    optimizer = PerformanceOptimizer()
    config = optimizer.get_performance_config()
    
    script_content = f'''"""
高性能批次處理啟動腳本
自動使用最佳系統配置
"""

import os
import multiprocessing as mp

# 系統檢測結果
CPU_COUNT = {optimizer.cpu_count}
MEMORY_GB = {optimizer.memory_gb:.1f}
OPTIMAL_WORKERS = {config['max_workers_cpu_intensive']}

# 設置環境變量優化
os.environ['OMP_NUM_THREADS'] = str(CPU_COUNT)
os.environ['NUMBA_NUM_THREADS'] = str(CPU_COUNT)
os.environ['MKL_NUM_THREADS'] = str(CPU_COUNT)

def run_optimized_batch():
    """運行優化的批次處理"""
    print(f"🚀 啟動高性能批次處理")
    print(f"系統配置: {{CPU_COUNT}} 核心, {{MEMORY_GB}} GB 記憶體")
    print(f"使用工作進程: {{OPTIMAL_WORKERS}}")
    
    try:
        from fast_batch_optimizer import optimize_specific_stocks_fast
        
        # 使用最佳配置
        result = optimize_specific_stocks_fast(
            speed_mode='fast',  # 平衡速度與品質
            max_workers=OPTIMAL_WORKERS,
            use_multiprocessing=True
        )
        
        print(result)
        
    except ImportError as e:
        print(f"❌ 導入錯誤: {{e}}")
        print("請確保 fast_batch_optimizer.py 文件存在")
    except Exception as e:
        print(f"❌ 執行錯誤: {{e}}")

if __name__ == "__main__":
    run_optimized_batch()
'''
    
    with open('optimized_batch_runner.py', 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print(f"\n✅ 已創建優化啟動腳本: optimized_batch_runner.py")
    print("使用方法: python optimized_batch_runner.py")

if __name__ == "__main__":
    print("💻 系統性能優化工具")
    print("=" * 60)
    
    # 創建性能配置
    config = create_optimized_batch_config()
    
    # 執行基準測試
    benchmark_results = benchmark_system()
    
    # Python 環境優化
    optimize_python_environment()
    
    # 創建優化腳本
    create_performance_script()
    
    print(f"\n🎯 性能優化完成！")
    print("建議執行順序:")
    print("1. python optimized_batch_runner.py  # 使用最佳配置")
    print("2. python fast_batch_optimizer.py    # 手動選擇配置")
    print("3. python main.py                    # GUI界面")
