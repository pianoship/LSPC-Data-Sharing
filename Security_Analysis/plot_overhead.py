import matplotlib.pyplot as plt
import numpy as np

# ==========================================
# 全局参数与样式设置
# ==========================================
T_hash = 0.3317  # 单次哈希耗时 (us) [已根据 C++ 真实基准测试更新]
K_target = 31    # 最优全局池大小 (n=2, q=5)
M_target = 6     # 最优局部子集大小 (n=2, q=5)
base_payload = 156 # 基础载荷大小 (Bytes) [确保 156 + 3*31 = 249 Bytes]

plt.rcParams.update({
    'font.size': 14, 
    'font.family': 'serif', 
    'axes.linewidth': 1.5
})

# ==========================================
# 绘制 Fig 4(a): PL 计算开销 (Generation Delay vs K)
# ==========================================
# 调整 K 的展示范围，使其覆盖我们的 target = 31
K_vals = np.arange(10, 71, 10) 
PL_delay = (K_vals + 2) * T_hash

plt.figure(figsize=(7, 5))
plt.plot(K_vals, PL_delay, marker='o', markersize=8, linewidth=2.5, color='#005293', label='PL Generation Delay')
# 标出最优设定点 K=31
PL_target_delay = (K_target + 2) * T_hash
plt.plot(K_target, PL_target_delay, marker='*', markersize=15, color='#e3000f', label=f'Optimal K={K_target} ({PL_target_delay:.2f} $\mu$s)')
plt.axvline(x=K_target, color='gray', linestyle='--', alpha=0.7)

plt.xlabel('Global Secret Pool Size $K$', fontweight='bold')
plt.ylabel('Generation Time ($\mu$s)', fontweight='bold')
plt.xticks(np.arange(10, 71, 10))
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend(loc='lower right', fontsize=12)
plt.tight_layout()
plt.savefig('Fig_4a_PL_Delay.pdf', format='pdf', dpi=600)
plt.close()

# ==========================================
# 绘制 Fig 4(b): PF 计算开销 (Verification Delay vs M)
# ==========================================
# 调整 M 的展示范围，使其覆盖我们的 target = 6
M_vals = np.arange(2, 13, 2)
PF_delay = (M_vals + 2) * T_hash

plt.figure(figsize=(7, 5))
plt.plot(M_vals, PF_delay, marker='s', markersize=8, linewidth=2.5, color='#2ca02c', label='PF Verification Delay')
# 标出最优设定点 M=6
PF_target_delay = (M_target + 2) * T_hash
plt.plot(M_target, PF_target_delay, marker='*', markersize=15, color='#e3000f', label=f'Optimal M={M_target} ({PF_target_delay:.2f} $\mu$s)')
plt.axvline(x=M_target, color='gray', linestyle='--', alpha=0.7)

plt.xlabel('Local Subset Size $M$', fontweight='bold')
plt.ylabel('Verification Time ($\mu$s)', fontweight='bold')
plt.xticks(np.arange(2, 13, 2))
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend(loc='lower right', fontsize=12)
plt.tight_layout()
plt.savefig('Fig_4b_PF_Delay.pdf', format='pdf', dpi=600)
plt.close()

# ==========================================
# 绘制 Fig 5: PL 通信开销 (Packet Size vs K)
# ==========================================
packet_size = base_payload + 3 * K_vals # 每个 MAC 3 字节 (24 bits)

plt.figure(figsize=(7, 5))
plt.plot(K_vals, packet_size, marker='^', markersize=8, linewidth=2.5, color='#8c564b', label='Total Packet Size')
# 标出最优设定点 K=31
target_packet_size = base_payload + 3 * K_target
plt.plot(K_target, target_packet_size, marker='*', markersize=15, color='#e3000f', label=f'Optimal K={K_target} ({target_packet_size} Bytes)')
plt.axvline(x=K_target, color='gray', linestyle='--', alpha=0.7)
plt.axhline(y=1500, color='black', linestyle=':', linewidth=2, label='Typical MTU (1500 Bytes)')

plt.xlabel('Global Secret Pool Size $K$', fontweight='bold')
plt.ylabel('Communication Overhead (Bytes)', fontweight='bold')
plt.xticks(np.arange(10, 71, 10))
plt.grid(True, linestyle='--', alpha=0.7)   
plt.legend(loc='best', fontsize=12)
plt.tight_layout()
plt.savefig('Fig_5_Comm_Overhead.pdf', format='pdf', dpi=600)
plt.close()

print("Figures 4a, 4b, and 5 generated successfully.")