import numpy as np
import matplotlib.pyplot as plt
from scipy.special import comb
import math
import matplotlib.colors as mcolors

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

# 定义基于恶意车辆数量 Nm 的离散柔和配色字典
color_map = {
    1: '#74add1',  # 柔和灰蓝
    2: '#fdae61',  # 柔和橙色
    3: '#d6604d',  # 浅红色 (显著区分于灰蓝)
    4: '#fee090'   # 浅黄色
}

# 定义不同 (K, M) 参数组对应的 Z 轴范围 (z_min, z_max)
custom_zlim_map = {
    (13, 4): (0, 6),    # 修改 4 为该图所需的 Z 轴上限
    (31, 6): (0, 25),   # 修改 15 为该图所需的 Z 轴上限
    (57, 8): (0, 40),   # 修改 35 为该图所需的 Z 轴上限
    (133, 12): (0, 60)  # 修改 65 为该图所需的 Z 轴上限
}

for K, M in parameter_pairs:
    # 为每组参数实例化独立的画布
    fig = plt.figure(figsize=(8, 7))
    ax = fig.add_subplot(111, projection='3d')
    
    x_vals = []  # 跟随车辆数量 N_PF
    y_vals = []  # 恶意车辆数量 N_m (即 C)
    z_vals = []  # 转换后的正数 Z 轴值
    
    # 定义域遍历：跟随车辆 N_PF 属于 [5, 10]
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
    
    # 柱体统一从 Z=0 底部开始向上生长
    z_pos = np.zeros(len(z_vals))
    dz = np.array(z_vals)
    
    # 将离散配色映射至对应的 y_vals (即 Nm)
    colors = [color_map[y] for y in y_vals]
    
    # 绘制三维柱状图
    ax.bar3d(x_pos, y_pos, z_pos, dx, dy, dz, 
             color=colors, alpha=0.85, edgecolor='k', linewidth=0.4)
    
    # ----------------- 坐标轴与标签渲染 -----------------
    ax.set_xlabel('$N_{PF}$', fontsize=15, labelpad=10)
    ax.set_ylabel('$N_m$', fontsize=15, labelpad=10)
    
    # 单独设置 X, Y, Z 轴刻度数字的字体大小
    ax.tick_params(axis='x', labelsize=15) # 修改 10 为所需大小
    ax.tick_params(axis='y', labelsize=15) # 修改 10 为所需大小
    ax.tick_params(axis='z', labelsize=15) # 修改 10 为所需大小

    # 修正 1: 将 labelpad 减小为 2（或更小），迫使标签贴近 Z 轴刻度
    ax.zaxis.set_rotate_label(False)
    ax.set_zlabel('$-\log_{10}(P_{forge})$', fontsize=15, labelpad=2, rotation=90)
    
    # 刻度粒度锁定
    ax.set_xticks(range(5, 11))
    ax.set_yticks(range(1, max(y_vals) + 1))
    
    # 根据当前 (K, M) 动态或手动约束 Z 轴范围
    if (K, M) in custom_zlim_map:
        z_min, z_max = custom_zlim_map[(K, M)]
        ax.set_zlim(z_min, z_max)
    else:
        # Fallback: 若未在字典中定义，则使用动态计算
        ax.set_zlim(0, max(z_vals) * 1.1)
    
    # 反转 Y 轴
    ax.invert_yaxis()
    
    # 空间视角锁定
    ax.view_init(elev=25, azim=-55)

    # 修正 2: 移除自动布局，防止其错误裁剪 Z 轴标签
    # plt.tight_layout()
    
    # 修正 3: 手动控制画布绝对边距，强制在右侧 (right=0.85) 预留 15% 的空白宽度给 Z 轴标签
    fig.subplots_adjust(left=0.01, right=0.85, bottom=0.05, top=0.92)
    
    # 动态生成文件名并单独导出
    filename = f'p_forge_3d_bar_K{K}_M{M}.pdf'
    plt.savefig(filename, format='pdf', dpi=600, bbox_inches='tight', pad_inches=0.3)
    plt.show()