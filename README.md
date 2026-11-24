# LSPC-Data-Sharing
hash.cpp: Benchmarks the SHA-256 execution time (T_hash) required by the proposed LSPC scheme.

main.cpp: Benchmarks fundamental cryptographic primitives (e.g., ECC scalar multiplication, modular exponentiation).

bench_test.cpp: Specifically benchmarks the cryptographic primitives used in the ALI comparative scheme (e.g., ECDSA, AES, HMAC).

pairing_bench.cpp: Specifically benchmarks the bilinear pairing operations used in the CLSS comparative scheme.

computation_cost.py: Plots the comparison bar charts for message generation and verification overhead across different schemes, using the data obtained from the C++ benchmarks.
