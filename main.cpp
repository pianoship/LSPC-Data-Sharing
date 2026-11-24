#include <iostream>
#include <chrono>
#include <iomanip>
#include <openssl/bn.h>
#include <openssl/ec.h>
#include <openssl/obj_mac.h>

using namespace std;
using namespace std::chrono;

int main() {
    const int ITERATIONS = 10000;
    BN_CTX *ctx = BN_CTX_new();

    cout << "=====================================================" << endl;
    cout << "  Cryptographic Primitives Benchmark (OpenSSL)       " << endl;
    cout << "  Iterations: " << ITERATIONS << endl;
    cout << "=====================================================" << endl;

    // ==========================================
    // 阶段一：椭圆曲线 ECC (256-bit) 参数初始化
    // ==========================================
    EC_GROUP *group = EC_GROUP_new_by_curve_name(NID_X9_62_prime256v1); // secp256r1
    EC_POINT *P = EC_POINT_new(group);
    EC_POINT *Q = EC_POINT_new(group);
    EC_POINT *R_ec = EC_POINT_new(group);
    
    BIGNUM *k = BN_new();
    BIGNUM *k2 = BN_new();
    BN_rand(k, 256, BN_RAND_TOP_ANY, BN_RAND_BOTTOM_ANY);
    BN_rand(k2, 256, BN_RAND_TOP_ANY, BN_RAND_BOTTOM_ANY);
    
    const EC_POINT *G = EC_GROUP_get0_generator(group);
    // 生成两个随机点 P 和 Q 用于测试
    EC_POINT_mul(group, P, NULL, G, k, ctx);
    EC_POINT_mul(group, Q, NULL, G, k2, ctx);

    // ==========================================
    // 测试 1: ECC 标量乘法 / 点乘 (T_sm)
    // ==========================================
    auto start = high_resolution_clock::now();
    for(int i = 0; i < ITERATIONS; i++) {
        // 计算 R_ec = k * P
        EC_POINT_mul(group, R_ec, NULL, P, k, ctx);
    }
    auto end = high_resolution_clock::now();
    double T_sm = duration_cast<microseconds>(end - start).count() / (double)ITERATIONS;

    // ==========================================
    // 测试 2: ECC 点加法 (T_add)
    // ==========================================
    start = high_resolution_clock::now();
    for(int i = 0; i < ITERATIONS; i++) {
        // 计算 R_ec = P + Q
        EC_POINT_add(group, R_ec, P, Q, ctx);
    }
    end = high_resolution_clock::now();
    double T_add = duration_cast<microseconds>(end - start).count() / (double)ITERATIONS;

    // ==========================================
    // 阶段二：大数 Big Number (1024-bit) 参数初始化
    // ==========================================
    BIGNUM *p = BN_new();
    BIGNUM *g = BN_new();
    BIGNUM *x = BN_new();
    BIGNUM *a = BN_new();
    BIGNUM *b = BN_new();
    BIGNUM *R_bn = BN_new();

    // 生成 1024 位的大素数 p
    BN_generate_prime_ex(p, 1024, 0, NULL, NULL, NULL);
    // 在模 p 范围内生成随机大数
    BN_rand_range(g, p);
    BN_rand_range(x, p);
    BN_rand_range(a, p);
    BN_rand_range(b, p);

    // ==========================================
    // 测试 3: 大数模幂运算 (T_exp)
    // ==========================================
    start = high_resolution_clock::now();
    for(int i = 0; i < ITERATIONS; i++) {
        // 计算 R_bn = g^x mod p
        BN_mod_exp(R_bn, g, x, p, ctx);
    }
    end = high_resolution_clock::now();
    double T_exp = duration_cast<microseconds>(end - start).count() / (double)ITERATIONS;

    // ==========================================
    // 测试 4: 大数模乘运算 (T_mul)
    // ==========================================
    start = high_resolution_clock::now();
    for(int i = 0; i < ITERATIONS; i++) {
        // 计算 R_bn = (a * b) mod p
        BN_mod_mul(R_bn, a, b, p, ctx);
    }
    end = high_resolution_clock::now();
    double T_mul = duration_cast<microseconds>(end - start).count() / (double)ITERATIONS;

    // ==========================================
    // 打印输出结果
    // ==========================================
    cout << fixed << setprecision(4);
    cout << "1. ECC Scalar Multiplication (T_sm) : " << T_sm << " us (" << T_sm / 1000.0 << " ms)" << endl;
    cout << "2. ECC Point Addition (T_add)       : " << T_add << " us (" << T_add / 1000.0 << " ms)" << endl;
    cout << "3. Modular Exponentiation (T_exp)   : " << T_exp << " us (" << T_exp / 1000.0 << " ms)" << endl;
    cout << "4. Modular Multiplication (T_mul)   : " << T_mul << " us (" << T_mul / 1000.0 << " ms)" << endl;
    cout << "=====================================================" << endl;

    // 释放内存
    EC_POINT_free(P); EC_POINT_free(Q); EC_POINT_free(R_ec);
    EC_GROUP_free(group);
    BN_free(k); BN_free(k2); BN_free(p); BN_free(g); 
    BN_free(x); BN_free(a); BN_free(b); BN_free(R_bn);
    BN_CTX_free(ctx);

    return 0;
}