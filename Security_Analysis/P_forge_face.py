import numpy as np
import matplotlib.pyplot as plt
from scipy.special import comb
import math

# ----------------- 全局参数与渲染配置 -----------------
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['pdf.fonttype'] = 42
plt.rcParams['ps.fonttype'] = 42

L_MAC = 24  # 截断哈希长度 (bits)

# ----------------- 核心数学模型计算 -----------------
def calculate_p_forge_log(K, M, C):
    """
    根据给定的 (K, M) 动态推导射影空间维度 n，
    并计算 C 个恶意节点串谋下的 P_forge(C) 的对数值。
    """
    # 1. 几何参数反解
    q = M - 1
    n = round(math.log(K * (q - 1) + 1, q)) - 1
    I_max = n + 2
    
    # 2. 覆盖能力计算
    cov_max = min(M, C * I_max)
    
    # 3. 分段函数 P_forge(C)
    if cov_max < M:
        exponent = M - cov_max
        p_log = exponent * (-L_MAC) * math.log10(2)
    else:
        expected_u = round(K * (1 - (1 - M/K)**C))
        U = max(M, min(expected_u, K)) 
        
        numerator = comb(U, M, exact=False)
        denominator = comb(K, M, exact=False)
        
        if numerator <= 0 or denominator <= 0:
            p_log = -300.0  # 浮点运算极小值截断
        else:
            p_log = math.log10(numerator / denominator)
            
    return p_log

# ----------------- 绘图执行逻辑 -----------------
parameter_pairs = [(13, 4), (31, 6), (57, 8), (133, 12)]

for K, M in parameter_pairs:
    # 为每组参数实例化独立的画布
    fig = plt.figure(figsize=(7, 6))
    ax = fig.add_subplot(111, projection='3d')
    
    x_vals = []  # 跟随车辆数量 N_PF
    y_vals = []  # 恶意车辆数量 N_m (即 C)
    z_vals = []  # log10(P_forge)
    
    # 定义域遍历：跟随车辆 N_PF 属于 [5, 10]
    for N_PF in range(5, 11):
        # 恶意车辆数量 C 属于 [1, floor(0.4 * N_PF)]
        max_malicious = math.floor(0.4 * N_PF)
        if max_malicious < 1:
            continue
            
        for C in range(1, max_malicious + 1):
            x_vals.append(N_PF)
            y_vals.append(C)
            z_vals.append(calculate_p_forge_log(K, M, C))
            
    # Delaunay 三角剖分绘制不规则定义域曲面
    surf = ax.plot_trisurf(x_vals, y_vals, z_vals, cmap='plasma', 
                           edgecolor='k', linewidth=0.5, alpha=0.9)
    
    # 坐标轴与标签渲染
    ax.set_title(f'Global Pool $K={K}$, Local Subset $M={M}$', fontsize=13, fontweight='bold', pad=15)
    ax.set_xlabel('Follower Vehicles ($N_{PF}$)', fontsize=10, labelpad=10)
    ax.set_ylabel('Malicious Colluders ($N_m$)', fontsize=10, labelpad=10)
    ax.set_zlabel('$\log_{10}(P_{forge})$', fontsize=10, labelpad=10)
    
    # 刻度粒度锁定
    ax.set_xticks(range(5, 11))
    ax.set_yticks(range(1, max(y_vals) + 1))
    
    # 空间视角锁定以凸显断崖式衰减特征
    ax.view_init(elev=25, azim=-55)

    plt.tight_layout()
    
    # 动态生成文件名并单独导出
    filename = f'p_forge_3d_K{K}_M{M}.pdf'
    plt.savefig(filename, format='pdf', dpi=600, bbox_inches='tight')
    plt.show()