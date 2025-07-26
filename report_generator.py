import matplotlib.pyplot as plt
import matplotlib
import os

# 設定中文字體
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False  # 解決負號顯示問題

def save_evolution_plot(fitness_history, avg_history, output_path="outputs/evolution.png"):
    plt.figure(figsize=(10, 6))
    plt.plot(fitness_history, label="最佳適應度", linewidth=2)
    plt.plot(avg_history, label="平均適應度", linestyle="--")
    plt.title("遺傳演算法適應度演化")
    plt.xlabel("世代")
    plt.ylabel("適應度")
    plt.legend()
    plt.grid(True, alpha=0.3)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300)
    plt.close()
