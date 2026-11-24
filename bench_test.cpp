#include <iostream>
#include <chrono>
#include <iomanip>
#include <cstring>
#include <vector>
#include <openssl/evp.h>
#include <openssl/hmac.h>
#include <openssl/kdf.h>
#include <openssl/rand.h>
#include <openssl/ec.h>

using namespace std;
using namespace std::chrono;

int main() {
    const int ITERATIONS = 10000;
    const int PAYLOAD_SIZE = 207;

    cout << "=====================================================" << endl;
    cout << "  ALI Scheme Cryptographic Primitives Benchmark      " << endl;
    cout << "  Iterations: " << ITERATIONS << " | Payload: " << PAYLOAD_SIZE << " Bytes" << endl;
    cout << "=====================================================" << endl;

    // ==========================================
    // 阶段一：ECDSA (EVP_PKEY - NIST P-256) 与 HKDF 初始化
    // ==========================================
    EVP_PKEY_CTX *kctx = EVP_PKEY_CTX_new_id(EVP_PKEY_EC, NULL);
    EVP_PKEY_keygen_init(kctx);
    EVP_PKEY_CTX_set_ec_paramgen_curve_nid(kctx, NID_X9_62_prime256v1);
    EVP_PKEY *pkey = NULL;
    EVP_PKEY_keygen(kctx, &pkey);
    EVP_PKEY_CTX_free(kctx);

    unsigned char digest[32];
    RAND_bytes(digest, sizeof(digest));

    EVP_PKEY_CTX *sctx = EVP_PKEY_CTX_new(pkey, NULL);
    EVP_PKEY_sign_init(sctx);
    size_t max_sig_len = 0;
    EVP_PKEY_sign(sctx, NULL, &max_sig_len, digest, sizeof(digest));
    vector<unsigned char> sig_buf(max_sig_len);
    size_t sig_len = max_sig_len;

    unsigned char ikm[32], salt[16], info[16], okm[32];
    RAND_bytes(ikm, sizeof(ikm));
    RAND_bytes(salt, sizeof(salt));
    RAND_bytes(info, sizeof(info));
    size_t okm_len = sizeof(okm);
    EVP_PKEY_CTX *hkdf_ctx = EVP_PKEY_CTX_new_id(EVP_PKEY_HKDF, NULL);

    // ==========================================
    // 测试 1: ECDSA-256 签名生成 (T_sign_ecdsa)
    // ==========================================
    auto start = high_resolution_clock::now();
    for (int i = 0; i < ITERATIONS; i++) {
        sig_len = max_sig_len;
        EVP_PKEY_sign(sctx, sig_buf.data(), &sig_len, digest, sizeof(digest));
    }
    auto end = high_resolution_clock::now();
    double T_sign_ecdsa = duration_cast<microseconds>(end - start).count() / (double)ITERATIONS;

    // ==========================================
    // 测试 2: HKDF-256 密钥导出 (T_sha_hkdf)
    // ==========================================
    start = high_resolution_clock::now();
    for (int i = 0; i < ITERATIONS; i++) {
        EVP_PKEY_derive_init(hkdf_ctx);
        EVP_PKEY_CTX_set_hkdf_md(hkdf_ctx, EVP_sha256());
        EVP_PKEY_CTX_set1_hkdf_salt(hkdf_ctx, salt, sizeof(salt));
        EVP_PKEY_CTX_set1_hkdf_key(hkdf_ctx, ikm, sizeof(ikm));
        EVP_PKEY_CTX_add1_hkdf_info(hkdf_ctx, info, sizeof(info));
        EVP_PKEY_derive(hkdf_ctx, okm, &okm_len);
    }
    end = high_resolution_clock::now();
    double T_sha_hkdf = duration_cast<microseconds>(end - start).count() / (double)ITERATIONS;

    // ==========================================
    // 阶段二：AES-128-CTR 与 HMAC-SHA256 初始化 (207 Bytes)
    // ==========================================
    unsigned char aes_key[16], iv[16];
    RAND_bytes(aes_key, sizeof(aes_key));
    RAND_bytes(iv, sizeof(iv));

    unsigned char plaintext[PAYLOAD_SIZE];
    RAND_bytes(plaintext, PAYLOAD_SIZE);
    unsigned char ciphertext[PAYLOAD_SIZE + 16];
    unsigned char decrypted[PAYLOAD_SIZE + 16];
    int len = 0;

    EVP_CIPHER_CTX *enc_ctx = EVP_CIPHER_CTX_new();
    EVP_CIPHER_CTX *dec_ctx = EVP_CIPHER_CTX_new();

    unsigned char hmac_key[32];
    RAND_bytes(hmac_key, sizeof(hmac_key));
    unsigned char mac[EVP_MAX_MD_SIZE];
    unsigned int mac_len = 0;

    // ==========================================
    // 测试 3: AES-128-CTR 加密 (T_enc_aes)
    // ==========================================
    start = high_resolution_clock::now();
    for (int i = 0; i < ITERATIONS; i++) {
        EVP_EncryptInit_ex(enc_ctx, EVP_aes_128_ctr(), NULL, aes_key, iv);
        EVP_EncryptUpdate(enc_ctx, ciphertext, &len, plaintext, PAYLOAD_SIZE);
        EVP_EncryptFinal_ex(enc_ctx, ciphertext + len, &len);
    }
    end = high_resolution_clock::now();
    double T_enc_aes = duration_cast<microseconds>(end - start).count() / (double)ITERATIONS;

    // ==========================================
    // 测试 4: AES-128-CTR 解密 (T_dec_aes)
    // ==========================================
    start = high_resolution_clock::now();
    for (int i = 0; i < ITERATIONS; i++) {
        EVP_DecryptInit_ex(dec_ctx, EVP_aes_128_ctr(), NULL, aes_key, iv);
        EVP_DecryptUpdate(dec_ctx, decrypted, &len, ciphertext, PAYLOAD_SIZE);
        EVP_DecryptFinal_ex(dec_ctx, decrypted + len, &len);
    }
    end = high_resolution_clock::now();
    double T_dec_aes = duration_cast<microseconds>(end - start).count() / (double)ITERATIONS;

    // ==========================================
    // 测试 5: HMAC-SHA256 认证码生成 (T_sha_hmac)
    // ==========================================
    start = high_resolution_clock::now();
    for (int i = 0; i < ITERATIONS; i++) {
        HMAC(EVP_sha256(), hmac_key, sizeof(hmac_key), plaintext, PAYLOAD_SIZE, mac, &mac_len);
    }
    end = high_resolution_clock::now();
    double T_sha_hmac = duration_cast<microseconds>(end - start).count() / (double)ITERATIONS;

    // ==========================================
    // 打印输出结果
    // ==========================================
    cout << fixed << setprecision(4);
    cout << "1. ECDSA-256 Sign        (T_sign_ecdsa) : " << T_sign_ecdsa << " us (" << T_sign_ecdsa / 1000.0 << " ms)" << endl;
    cout << "2. HKDF-256 Derivation   (T_sha_hkdf)   : " << T_sha_hkdf   << " us (" << T_sha_hkdf   / 1000.0 << " ms)" << endl;
    cout << "3. AES-128-CTR Encrypt   (T_enc_aes)    : " << T_enc_aes    << " us (" << T_enc_aes    / 1000.0 << " ms)" << endl;
    cout << "4. AES-128-CTR Decrypt   (T_dec_aes)    : " << T_dec_aes    << " us (" << T_dec_aes    / 1000.0 << " ms)" << endl;
    cout << "5. HMAC-SHA256 Generate  (T_sha_hmac)   : " << T_sha_hmac   << " us (" << T_sha_hmac   / 1000.0 << " ms)" << endl;
    cout << "=====================================================" << endl;

    EVP_PKEY_CTX_free(sctx);
    EVP_PKEY_free(pkey);
    EVP_PKEY_CTX_free(hkdf_ctx);
    EVP_CIPHER_CTX_free(enc_ctx);
    EVP_CIPHER_CTX_free(dec_ctx);

    return 0;
}