#include <iostream>
#include <vector>
#include <chrono>
#include <iomanip>
#include <openssl/evp.h>

using namespace std;
using namespace std::chrono;

// 模拟计算 SHA-256 哈希 (对应方案中的 T_hash)
void compute_sha256(const vector<unsigned char>& message, vector<unsigned char>& digest) {
    unsigned int digest_len;
    EVP_MD_CTX* mdctx = EVP_MD_CTX_new();

    if (mdctx == nullptr) {
        cerr << "Failed to create OpenSSL EVP context" << endl;
        return;
    }

    // 初始化 SHA-256
    EVP_DigestInit_ex(mdctx, EVP_sha256(), nullptr);
    // 输入数据
    EVP_DigestUpdate(mdctx, message.data(), message.size());
    // 获取哈希结果
    EVP_DigestFinal_ex(mdctx, digest.data(), &digest_len);

    EVP_MD_CTX_free(mdctx);
}

int main() {
    // ==========================================
    // 1. 最新方案参数配置 (n=2, q=5)
    // ==========================================
    const int K = 31; // 全局秘密份额总数 (PL 需要计算的 MAC 数量)
    const int M = 6;  // 跟随车局部秘密份额子集 (PF 需要计算的 MAC 数量)
    const int ITERATIONS = 100000; // 迭代次数

    // 模拟控制包数据负载
    vector<unsigned char> msg(249, 'A');
    vector<unsigned char> digest(32); // SHA-256 输出 32 字节

    cout << "=====================================================" << endl;
    cout << "   Simulation for Platoon Authentication Scheme      " << endl;
    cout << "=====================================================" << endl;
    cout << "Cryptographic Primitive : SHA-256 (OpenSSL 3.x EVP)" << endl;
    cout << "Global Secret Pool (K)  : " << K << endl;
    cout << "Local Secret Subset (M) : " << M << endl;
    cout << "Iterations              : " << ITERATIONS << endl;
    cout << "Payload Size            : " << msg.size() << " Bytes" << endl;
    cout << "-----------------------------------------------------" << endl;

    // ==========================================
    // 2. 基础哈希性能基准测试 (测量 T_hash)
    // ==========================================
    auto start_time_base = high_resolution_clock::now();
    for (int i = 0; i < ITERATIONS; ++i) {
        compute_sha256(msg, digest);
    }
    auto end_time_base = high_resolution_clock::now();

    double total_base_us = duration_cast<microseconds>(end_time_base - start_time_base).count();
    double T_hash = total_base_us / ITERATIONS;

    // ==========================================
    // 3. 领航车 (PL) 生成开销测试
    // 理论值: (K + 2) * T_hash
    // ==========================================
    auto start_time_PL = high_resolution_clock::now();
    for (int i = 0; i < ITERATIONS; ++i) {
        // 哈希链派生 (2次)
        compute_sha256(msg, digest);
        compute_sha256(msg, digest);
        // 多重 MAC 计算 (K次)
        for (int j = 0; j < K; ++j) {
            compute_sha256(msg, digest);
        }
    }
    auto end_time_PL = high_resolution_clock::now();

    double total_PL_us = duration_cast<microseconds>(end_time_PL - start_time_PL).count();
    double T_PL_generation = total_PL_us / ITERATIONS;

    // ==========================================
    // 4. 跟随车 (PF) 校验开销测试
    // 理论值: (M + 2) * T_hash
    // ==========================================
    auto start_time_PF = high_resolution_clock::now();
    for (int i = 0; i < ITERATIONS; ++i) {
        // 短链状态校验 (2次)
        compute_sha256(msg, digest);
        compute_sha256(msg, digest);
        // 多重 MAC 交叉验证 (M次)
        for (int j = 0; j < M; ++j) {
            compute_sha256(msg, digest);
        }
    }
    auto end_time_PF = high_resolution_clock::now();

    double total_PF_us = duration_cast<microseconds>(end_time_PF - start_time_PF).count();
    double T_PF_verification = total_PF_us / ITERATIONS;

    // ==========================================
    cout << fixed << setprecision(4);
    cout << "1. Base Operation Cost:" << endl;
    cout << "   -> T_hash             : " << T_hash << " us" << endl;
    cout << "-----------------------------------------------------" << endl;
    cout << "2. Platoon Leader (PL) Overhead:" << endl;
    cout << "   -> Generation Time    : " << T_PL_generation << " us" << endl;
    cout << "   -> Theoretical Value  : " << (K + 2) * T_hash << " us" << endl;
    cout << "-----------------------------------------------------" << endl;
    cout << "3. Platoon Follower (PF) Overhead:" << endl;
    cout << "   -> Verification Time  : " << T_PF_verification << " us" << endl;
    cout << "   -> Theoretical Value  : " << (M + 2) * T_hash << " us" << endl;
    cout << "=====================================================" << endl;

    return 0;
}
