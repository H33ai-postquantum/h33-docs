# Security Policy

## Reporting Vulnerabilities

Email: security@h33.ai

We respond to all reports within 24 hours. Do not open public issues for security vulnerabilities.

## Bug Bounty

Contact security@h33.ai for our bug bounty program details.

## Architecture

- All cryptographic operations use NIST-standardized post-quantum algorithms
- FHE: BFV (lattice-based), CKKS (lattice-based)
- Signatures: Dilithium ML-DSA-65 (FIPS 204), Falcon-512, SPHINCS+ SLH-DSA
- Key Exchange: Kyber ML-KEM-768 (FIPS 203)
- Hashing: SHA3-256 (FIPS 202)
- ZKP: STARK (transparent, no trusted setup)
