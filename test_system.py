import psutil
import multiprocessing

print(f"🖥️ 系統資源檢測:")
print(f"   CPU 核心數: {multiprocessing.cpu_count()}")
print(f"   總記憶體: {psutil.virtual_memory().total/(1024**3):.1f} GB")
print(f"   可用記憶體: {psutil.virtual_memory().available/(1024**3):.1f} GB")
print("✅ 系統資源檢測正常！")
