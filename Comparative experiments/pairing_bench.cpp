#include <iostream>
#include <chrono>
#include <iomanip>
#include <pbc/pbc.h>

using namespace std;
using namespace std::chrono;

int main() {
    // ==========================================
    // 1. 初始化配对参数
    // 曲线类型: Type A 
    // r = 160 bits
    // q = 512 bits
    // ==========================================
    pbc_param_t param;
    pairing_t pairing;
    pbc_param_init_a_gen(param, 160, 512);
    pairing_init_pbc_param(pairing, param);

    // 2. 初始化群元素并赋值
    element_t P, Q, res;
    element_init_G1(P, pairing);
    element_init_G2(Q, pairing);
    element_init_GT(res, pairing);

    element_random(P);
    element_random(Q);

    const int ITERATIONS = 10000; // 迭代 10000 次求平均值

    cout << "=====================================================" << endl;
    cout << "   Bilinear Pairing Benchmark (CLSS Paper Specs)     " << endl;
    cout << "=====================================================" << endl;
    cout << "Library         : PBC (Pairing-Based Cryptography)" << endl;
    cout << "Curve Type      : Supersingular (Type A)" << endl;
    cout << "Security Level  : 80-bit Equivalent" << endl;
    cout << "Prime Order (r) : 160-bit" << endl;
    cout << "Base Field (q)  : 512-bit" << endl;
    cout << "Target Group    : 1024-bit (q^2, Embedding Degree k=2)" << endl;
    cout << "Iterations      : " << ITERATIONS << endl;
    cout << "-----------------------------------------------------" << endl;

    // 3. 开始基准测试: T_bp
    auto start_time = high_resolution_clock::now();
    for (int i = 0; i < ITERATIONS; ++i) {
        // 执行 e(P, Q)
        element_pairing(res, P, Q);
    }
    auto end_time = high_resolution_clock::now();
    
    double total_us = duration_cast<microseconds>(end_time - start_time).count();
    // 转换为毫秒(ms)方便直接对标传统文献
    double T_bp_ms = (total_us / ITERATIONS) / 1000.0;

    cout << fixed << setprecision(4);
    cout << "Result:" << endl;
    cout << " -> T_bp (Bilinear Pairing) : " << T_bp_ms << " ms" << endl;
    cout << "=====================================================" << endl;

    // 清理内存
    element_clear(P);
    element_clear(Q);
    element_clear(res);
    pairing_clear(pairing);
    pbc_param_clear(param);

    return 0;
}
