import matplotlib.pyplot as plt
import numpy as np
import scipy.special as sp

# ==========================================
# 1. 参数配置
# ==========================================
K = 31  
M = 6   
n = 2   
I_max = n + 2  # 交集上限
MAC_bits = 24  # 单个 MAC 的位宽
P_single_mac_guess = 2.0 ** (-MAC_bits)

C_vals = np.arange(1, 5)

# ==========================================
# 2. 秘密份额并集 U 的计算
# ==========================================
linear_U = np.minimum(C_vals * M, K)

U_rnc = np.zeros_like(C_vals, dtype=float)
U_rnc[0] = M
for i in range(1, len(C_vals)):
    new_points = max(1, M - i * (I_max - 1)) 
    U_rnc[i] = min(K, U_rnc[i-1] + new_points)

# ==========================================
# 3. 伪造概率 P_forge 计算
# ==========================================
P_forge_linear = np.zeros_like(C_vals, dtype=float)
P_forge_rnc = np.zeros_like(C_vals, dtype=float)

for i, C in enumerate(C_vals):
    # --- 无 RNC 时的概率 ---
    P_forge_linear[i] = sp.comb(linear_U[i], M) / sp.comb(K, M)

    # --- 有 RNC 时的概率 ---
    Cov_max = min(M, C * I_max)
    
    if Cov_max < M:
        blind_spot = M - Cov_max
        P_forge_rnc[i] = P_single_mac_guess ** blind_spot
    else:
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

plt.xticks(np.arange(1, 5, 1))
plt.xlim(0.8, 4.2)

plt.ylim(1e-16, 2)

plt.grid(True, which="both", linestyle='--', alpha=0.7)
plt.legend(loc='lower right', fontsize=11)
plt.tight_layout()
plt.savefig('Fig_Pforge_vs_C.pdf', format='pdf', dpi=600)
plt.close()
