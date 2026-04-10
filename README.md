# H33 API Documentation

Official documentation for the H33 Post-Quantum Cryptographic Infrastructure API.

## Quick Start

```bash
# Get your API key
curl https://h33.ai/pricing/

# Test authentication
curl -X POST https://api.h33.ai/api/v2/biometric/enroll \
  -H "X-API-Key: YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user_001", "embedding": [...], "product": "h33"}'
```

## Products

| Product | Description | Docs |
|---------|-------------|------|
| H33-128 | BFV FHE biometric auth (NIST L1) | [h33.ai/h33-128](https://h33.ai/h33-128/) |
| H33-256 | BFV FHE biometric auth (NIST L5) | [h33.ai/h33-256](https://h33.ai/h33-256/) |
| H33-CKKS | Approximate FHE for ML inference | [h33.ai/h33-ckks](https://h33.ai/h33-ckks/) |
| ZK-STARK | Zero-knowledge proof verification | [h33.ai/zk](https://h33.ai/zk/) |
| BotShield | Proof-of-work bot prevention | [h33.ai/botshield](https://h33.ai/botshield/) |
| HICS | Code security scoring (open source) | [h33.ai/hics](https://h33.ai/hics/) |

## Pipeline

Every API call executes the full post-quantum pipeline:

1. **FHE** — BFV encrypt + SIMD inner product (32 users/ciphertext)
2. **STARK** — Zero-knowledge proof verification (SHA3-256)
3. **Dilithium** — ML-DSA-65 post-quantum attestation signature
4. **3-Key** — Nested Dilithium + Falcon + SPHINCS+ (three mathematical families)

**2,209,429 auth/sec sustained. 35.25µs per auth. Single ARM CPU.**

## SDKs

- [Python](https://h33.ai/docs/sdk/python/)
- [JavaScript/TypeScript](https://h33.ai/docs/sdk/javascript/)
- [Rust](https://h33.ai/docs/sdk/rust/)
- [Go](https://h33.ai/docs/sdk/go/)

## Links

- **API Reference:** [h33.ai/docs/api](https://h33.ai/docs/api/)
- **Pricing:** [h33.ai/pricing](https://h33.ai/pricing/)
- **Benchmarks:** [h33.ai/benchmarks](https://h33.ai/benchmarks/)
- **Live Demo:** [h33.ai/demo/live-fhe](https://h33.ai/demo/live-fhe/)
- **Status:** [status.h33.ai](https://status.h33.ai)

## License

Documentation: CC BY 4.0. API: Commercial license. See [h33.ai/terms](https://h33.ai/terms/).

---

**H33.ai, Inc.** — Post-Quantum Privacy-as-a-Service
