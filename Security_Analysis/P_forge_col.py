import numpy as np
import matplotlib.pyplot as plt
from scipy.special import comb
import math
import matplotlib.colors as mcolors

# ----------------- 全局参数 -----------------
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['pdf.fonttype'] = 42
plt.rcParams['ps.fonttype'] = 42

L_MAC = 24  # 截断哈希长度 (bits)

# ----------------- 核心计算 -----------------
def calculate_p_forge_log(K, M, C):
    """
    计算 C 个恶意节点串谋下的 P_forge(C) 的对数值。
    """
    # 1. 几何参数
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
            p_log = -300.0 
        else:
            p_log = math.log10(numerator / denominator)
            
    return p_log

# ----------------- 绘图执行 -----------------
parameter_pairs = [(13, 4), (31, 6), (57, 8), (133, 12)]

color_map = {
    1: '#74add1',  
    2: '#fdae61', 
    3: '#d6604d',  
    4: '#fee090'  
}

# 定义不同 (K, M) 参数组对应的 Z 轴范围 (z_min, z_max)
custom_zlim_map = {
    (13, 4): (0, 6),    
    (31, 6): (0, 25),  
    (57, 8): (0, 40),   
    (133, 12): (0, 60) 
}

for K, M in parameter_pairs:
    # 为每组参数实例化独立的画布
    fig = plt.figure(figsize=(8, 7))
    ax = fig.add_subplot(111, projection='3d')
    
    x_vals = []  # 跟随车辆数量 N_PF
    y_vals = []  # 恶意车辆数量 N_m
    z_vals = []  # 转换后的正数 Z 轴值
    
    # 跟随车辆 N_PF 属于 [5, 10]
    for N_PF in range(5, 11):
        # 恶意车辆数量 C 属于 [1, floor(0.4 * N_PF)]
        max_malicious = math.floor(0.4 * N_PF)
        if max_malicious < 1:
            continue
            
        for C in range(1, max_malicious + 1):
            x_vals.append(N_PF)
            y_vals.append(C)
            # 对原负向概率对数取绝对值 (加负号)，使数值转为正数
            z_vals.append(-calculate_p_forge_log(K, M, C))
            
    # --- 转换为三维柱状图的数据结构 ---
    dx = np.ones(len(x_vals)) * 0.6
    dy = np.ones(len(y_vals)) * 0.6
    
    x_pos = np.array(x_vals) - dx/2
    y_pos = np.array(y_vals) - dy/2
    
    z_pos = np.zeros(len(z_vals))
    dz = np.array(z_vals)
    
    colors = [color_map[y] for y in y_vals]
    
    # 绘制三维柱状图
    ax.bar3d(x_pos, y_pos, z_pos, dx, dy, dz, 
             color=colors, alpha=0.85, edgecolor='k', linewidth=0.4)
    
    # ----------------- 坐标轴与标签渲染 -----------------
    ax.set_xlabel('$N_{PF}$', fontsize=15, labelpad=10)
    ax.set_ylabel('$N_m$', fontsize=15, labelpad=10)
    
    ax.tick_params(axis='x', labelsize=15) 
    ax.tick_params(axis='y', labelsize=15) 
    ax.tick_params(axis='z', labelsize=15) 

    ax.zaxis.set_rotate_label(False)
    ax.set_zlabel('$-\log_{10}(P_{forge})$', fontsize=15, labelpad=2, rotation=90)
    
    ax.set_xticks(range(5, 11))
    ax.set_yticks(range(1, max(y_vals) + 1))
    
    if (K, M) in custom_zlim_map:
        z_min, z_max = custom_zlim_map[(K, M)]
        ax.set_zlim(z_min, z_max)
    else:
        # Fallback: 若未在字典中定义，则使用动态计算
        ax.set_zlim(0, max(z_vals) * 1.1)
    
    ax.invert_yaxis()
    
    ax.view_init(elev=25, azim=-55)

    # plt.tight_layout()
    
    fig.subplots_adjust(left=0.01, right=0.85, bottom=0.05, top=0.92)
    
    filename = f'p_forge_3d_bar_K{K}_M{M}.pdf'
    plt.savefig(filename, format='pdf', dpi=600, bbox_inches='tight', pad_inches=0.3)
    plt.show()
