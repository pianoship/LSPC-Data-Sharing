import matplotlib.pyplot as plt
import numpy as np

# 设置全局字体和论文绘图风格
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
plt.rcParams['axes.edgecolor'] = '#333333'
plt.rcParams['axes.linewidth'] = 1.0
plt.rcParams['hatch.linewidth'] = 1.0  # 控制填充纹理的线宽

# 数据准备
schemes = ['LSPC (Ours)', 'HDMA', 'ALI', 'CLSS']
gen_times = [0.0099, 0.4320, 0.1620, 0.1730]    # 消息生成耗时 (ms)
ver_times = [0.0024, 0.6477, 0.0400, 1.5333]    # 消息验证耗时 (ms)

# 定义颜色与填充纹理 (Hatch)
colors = ['#d95f02', '#2b83ba', '#4575b4', '#74add1']
hatches = ['', '////', '....', 'xxxx']

def plot_bar_chart(x_labels, y_data, title, y_label, filename, max_y_scale=1.2):
    fig, ax = plt.subplots(figsize=(7, 4.5), dpi=300)
    
    x = np.arange(len(x_labels))
    width = 0.55
    
    # 绘制柱状图
    bars = ax.bar(x, y_data, width=width, color=colors, edgecolor='black', linewidth=1.0, zorder=3)
    
    # 为每个柱体单独设置对应的填充纹理
    for bar, hatch in zip(bars, hatches):
        bar.set_hatch(hatch)
    
    # 添加网格线
    ax.grid(axis='y', linestyle='--', alpha=0.5, zorder=0)
    
    # 设置横纵坐标与标签
    ax.set_ylabel(y_label, fontsize=12, fontweight='bold')
    ax.set_title(title, fontsize=13, fontweight='bold', pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(x_labels, fontsize=11)
    
    ax.set_ylim(0, max(y_data) * max_y_scale)
    
    # 为每个条形图在上方添加具体的数值标签
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height:.4f}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 5),  # 向上偏移 5 点
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=10.5, fontweight='bold')
        
    plt.tight_layout()
    # 输出为 PDF 矢量图
    plt.savefig(f"{filename}.pdf", format='pdf', bbox_inches='tight')
    plt.show()

# ================= 1. 消息生成开销对比图 =================
plot_bar_chart(
    x_labels=schemes,
    y_data=gen_times,
    title='Message Generation Overhead Comparison',
    y_label='Generation Time (ms)',
    filename='message_generation_overhead',
    max_y_scale=1.18
)

# ================= 2. 消息验证开销对比图 =================
plot_bar_chart(
    x_labels=schemes,
    y_data=ver_times,
    title='Message Verification Overhead Comparison',
    y_label='Verification Time (ms)',
    filename='message_verification_overhead',
    max_y_scale=1.15
)
