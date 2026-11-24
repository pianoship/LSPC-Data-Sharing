import matplotlib.pyplot as plt
import numpy as np
import scipy.special as sp

# ==========================================
# 1. 核心参数配置
# ==========================================
K = 31  # 射影空间点总数
M = 6   # 单个 RNC 包含的点数 (q+1)
n = 2   # 射影空间维度
I_max = n + 2  # 确定性交集上限
MAC_bits = 24  # 单个 MAC 的截断位宽
P_single_mac_guess = 2.0 ** (-MAC_bits) # 猜中单个未知 MAC 的概率

# 修改点 1：将范围修改为 1 到 4
C_vals = np.arange(1, 5)

# ==========================================
# 2. 秘密份额并集 U 的计算
# ==========================================
# 无 RNC：零约束下的线性累加
linear_U = np.minimum(C_vals * M, K)

# 有 RNC：高度重叠导致集合增长极度缓慢 (理论收敛模型)
U_rnc = np.zeros_like(C_vals, dtype=float)
U_rnc[0] = M
for i in range(1, len(C_vals)):
    # 模拟交集冗余：每增加一辆车，带来的非重复新份额锐减
    new_points = max(1, M - i * (I_max - 1)) 
    U_rnc[i] = min(K, U_rnc[i-1] + new_points)

# ==========================================
# 3. 严格遵循双重边界的伪造概率 P_forge 计算
# ==========================================
P_forge_linear = np.zeros_like(C_vals, dtype=float)
P_forge_rnc = np.zeros_like(C_vals, dtype=float)

for i, C in enumerate(C_vals):
    # --- 无 RNC 时的概率 (传统基线) ---
    P_forge_linear[i] = sp.comb(linear_U[i], M) / sp.comb(K, M)

    # --- 有 RNC 时的概率 (严格对齐密码学现实) ---
    Cov_max = min(M, C * I_max)
    
    if Cov_max < M:
        # 几何截断生效：无法全覆盖，必须穷举盲区 MAC
        blind_spot = M - Cov_max
        P_forge_rnc[i] = P_single_mac_guess ** blind_spot
    else:
        # 几何全覆盖可能发生：概率由目标完全落入 U_rnc 的超几何分布决定
        P_forge_rnc[i] = sp.comb(U_rnc[i], M) / sp.comb(K, M)

# ==========================================
# 图表绘制设置
# ==========================================
plt.rcParams.update({'font.size': 14, 'font.family': 'serif', 'axes.linewidth': 1.5})

# --- 绘制 Fig  U vs C ---
plt.figure(figsize=(7, 5))
plt.plot(C_vals, U_rnc, marker='o', markersize=8, linewidth=2.5, color='#005293', label='Proposed RNC (High Overlap)')
plt.plot(C_vals, linear_U, marker='s', markersize=8, linewidth=2.5, linestyle='--', color='#e3000f', label='Without RNC (Linear)')
plt.axhline(y=K, color='black', linestyle=':', linewidth=2, label=f'Total Pool Size $K={K}$')

plt.xlabel('Number of Malicious Followers $C$', fontweight='bold')
plt.ylabel('Size of Share Union $U$', fontweight='bold')

# 修改点 2：调整 X 轴刻度和边界
plt.xticks(np.arange(1, 5, 1))
plt.yticks(np.arange(0, 36, 5))
plt.xlim(0.8, 4.2)
plt.ylim(0, 35)

plt.grid(True, linestyle='--', alpha=0.7)
plt.legend(loc='upper left', fontsize=11)
plt.tight_layout()
plt.savefig('Fig_U_vs_C.pdf', format='pdf', dpi=600)
plt.close()

# --- 绘制 Fig  P_forge vs C ---
plt.figure(figsize=(7, 5))
plt.plot(C_vals, P_forge_rnc, marker='^', markersize=8, linewidth=2.5, color='#005293', label='Proposed RNC')
plt.plot(C_vals, P_forge_linear, marker='x', markersize=8, linewidth=2.5, linestyle='--', color='#e3000f', label='Without RNC')

plt.yscale('log')
plt.xlabel('Number of Malicious Followers $C$', fontweight='bold')
plt.ylabel('Forgery Probability $P_{forge}$', fontweight='bold')

# 修改点 3：调整 X 轴刻度和边界
plt.xticks(np.arange(1, 5, 1))
plt.xlim(0.8, 4.2)

# 自适应 Y 轴下限，容纳极小的 2^-48 概率
plt.ylim(1e-16, 2)

plt.grid(True, which="both", linestyle='--', alpha=0.7)
plt.legend(loc='lower right', fontsize=11)
plt.tight_layout()
plt.savefig('Fig_Pforge_vs_C.pdf', format='pdf', dpi=600)
plt.close()