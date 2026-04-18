#!/usr/bin/env python3
"""Apply all 10 whitepaper fixes to all 8 files."""

import re
import os

FILES = [
    "/Users/ericbeans/Desktop/H33-74-Whitepaper-Source.html",
    "/Users/ericbeans/Desktop/Companies/H33/h33-deploy-correct/h33-74/whitepaper/index.html",
    "/Users/ericbeans/Desktop/Companies/H33/h33-deploy-correct/h33-74/whitepaper/interactive.html",
    "/Users/ericbeans/Desktop/Companies/H33/h33-deploy-correct/h33-74/whitepaper/print.html",
    "/Users/ericbeans/Desktop/Companies/H33/h33-deploy-correct/substrate/whitepaper/index.html",
    "/Users/ericbeans/Desktop/Companies/H33/h33-deploy-correct/substrate/whitepaper/interactive.html",
    "/Users/ericbeans/Desktop/Companies/H33/h33-deploy-correct/substrate/whitepaper/print.html",
    "/tmp/h33-docs-check/whitepaper/H33-74-Whitepaper.html",
]

def apply_fixes(content, filename):
    changes = []

    # === FIX 1: Remove SNARK comparison entirely ===
    old_snark = '<p><strong>SNARK/STARK-based attestations.</strong> A ZK-SNARK or ZK-STARK proof of correct computation, without a signature bundle, could provide computation-result attestation with succinctness. However, SNARKs require a trusted setup (which H33-74 avoids), and STARKs at the scale required for general computation verification are not yet practical for arbitrary computation types (&sect;11.9). The proof-of-life construction in &sect;9.9 demonstrates a STARK-based attestation for a specific computation (secp256k1 discrete log), but generalizing this to the full range of computation types H33-74 supports remains an open problem. Additionally, neither SNARKs nor STARKs provide assumption diversity &mdash; they rely on a single hardness assumption (knowledge-of-exponent or collision resistance, respectively).</p>'

    new_stark = '<p><strong>STARK-based attestations.</strong> A ZK-STARK proof of correct computation, without a signature bundle, could provide computation-result attestation with succinctness. STARKs require no trusted setup and rely on collision resistance of hash functions, which aligns with H33&rsquo;s design principles. However, STARKs at the scale required for general computation verification are not yet practical for arbitrary computation types (&sect;11.9). The proof-of-life construction in &sect;9.9 demonstrates a STARK-based attestation for a specific computation (secp256k1 discrete log), but generalizing this to the full range of computation types H33-74 supports remains an open problem. H33 uses ZK-STARKs exclusively; no SNARK or pairing-based construction appears anywhere in the H33 stack.</p>'

    if old_snark in content:
        content = content.replace(old_snark, new_stark)
        changes.append("FIX 1: Replaced SNARK/STARK paragraph with STARK-only version")
    else:
        changes.append("FIX 1: WARNING - SNARK/STARK paragraph not found")

    # === FIX 2: Fix FALCON Level 3 error ===
    # The old text: "A straightforward upgrade path to uniform NIST Level 3 uses FALCON-1024 and SLH-DSA-SHA2-192f in place of the Level 1 variants. For deployments requiring uniform NIST Level 5"
    old_falcon = 'A straightforward upgrade path to uniform NIST Level 3 uses FALCON-1024 and SLH-DSA-SHA2-192f in place of the Level 1 variants. For deployments requiring uniform NIST Level 5'

    new_falcon = 'An intermediate composition using ML-DSA-65 (Level 3), FALCON-1024 (Level 5), and SLH-DSA-SHA2-192f (Level 3) raises the minimum family level but does not achieve uniformity &mdash; FALCON-1024 is Level 5, not Level 3, and no Level 3 FALCON parameter set exists. For deployments requiring uniform NIST Level 5'

    if old_falcon in content:
        content = content.replace(old_falcon, new_falcon)
        changes.append("FIX 2: Fixed FALCON Level 3 error")
    else:
        changes.append("FIX 2: WARNING - FALCON Level 3 text not found")

    # === FIX 3: Fix "the the" typo ===
    old_thethe = 'the the one-wayness'
    new_thethe = 'the one-wayness'

    count_thethe = content.count(old_thethe)
    if count_thethe > 0:
        content = content.replace(old_thethe, new_thethe)
        changes.append(f"FIX 3: Fixed 'the the' typo ({count_thethe} occurrences)")
    else:
        changes.append("FIX 3: 'the the one-wayness' not found (may already be fixed)")

    # === FIX 4: Fix §7.2 vs §7.4 inconsistency ===
    # 4a: In the §7.2 table, change raw DashMap baseline from 2,216,488 to 2,258,800
    # The row: <td>Metal, full pipeline, raw DashMap data structure</td> followed by <td><strong>2,216,488</strong></td>
    old_raw_row = 'raw DashMap data structure</td>\n      <td><strong>2,216,488</strong></td>'
    new_raw_row = 'raw DashMap data structure</td>\n      <td><strong>2,258,800</strong></td>'

    if old_raw_row in content:
        content = content.replace(old_raw_row, new_raw_row)
        changes.append("FIX 4a: Changed raw baseline in §7.2 table to 2,258,800")
    else:
        changes.append("FIX 4a: WARNING - raw DashMap row pattern not found in table")

    # 4b: In §7.4, fix "raw baseline of 2,216,488" or "raw DashMap baseline of 2,216,488"
    # Different files have different wording here
    old_74_v1 = 'the raw baseline of 2,216,488 auth/sec'
    new_74_v1 = 'the raw baseline of 2,258,800 auth/sec'
    old_74_v2 = 'the raw DashMap baseline of 2,216,488 auth/sec'
    new_74_v2 = 'the raw DashMap baseline of 2,258,800 auth/sec'

    if old_74_v1 in content:
        content = content.replace(old_74_v1, new_74_v1)
        changes.append("FIX 4b: Changed §7.4 'raw baseline' to 2,258,800")
    elif old_74_v2 in content:
        content = content.replace(old_74_v2, new_74_v2)
        changes.append("FIX 4b: Changed §7.4 'raw DashMap baseline' to 2,258,800")
    else:
        changes.append("FIX 4b: WARNING - §7.4 raw baseline text not found")

    # === FIX 5: Fix §9.9 limb/doubling inconsistency ===
    old_limb = '64 individual doublings per limb (512 total conditional subtractions per multiplication)'
    new_limb = '64 individual doublings per 64-bit intermediate word (512 total conditional subtractions per multiplication in the original 64-bit limb representation, which was subsequently replaced with the current 32-bit limb scheme)'

    # Also handle variant without "per multiplication"
    old_limb_v2 = '64 individual doublings per limb (512 total conditional subtractions)'
    new_limb_v2 = '64 individual doublings per 64-bit intermediate word (512 total conditional subtractions per multiplication in the original 64-bit limb representation, which was subsequently replaced with the current 32-bit limb scheme)'

    if old_limb in content:
        content = content.replace(old_limb, new_limb)
        changes.append("FIX 5: Fixed §9.9 limb/doubling text (variant 1)")
    elif old_limb_v2 in content:
        content = content.replace(old_limb_v2, new_limb_v2)
        changes.append("FIX 5: Fixed §9.9 limb/doubling text (variant 2)")
    else:
        changes.append("FIX 5: WARNING - §9.9 limb text not found")

    # === FIX 6: Fix §9.9 SLH-DSA 12ms timing ===
    old_12ms = 'SLH-DSA-SHA2-128f signing is the bottleneck at approximately 12 ms per invocation'
    new_12ms = 'SLH-DSA-SHA2-128f signing is the bottleneck at approximately 5 ms per invocation on Graviton4 (approximately 12 ms on Apple Silicon development hardware)'

    if old_12ms in content:
        content = content.replace(old_12ms, new_12ms)
        changes.append("FIX 6: Fixed SLH-DSA 12ms timing")
    else:
        changes.append("FIX 6: SLH-DSA 12ms text not found (may already be fixed or different wording)")

    # === FIX 7: Fix "Softfork" → "Soft fork" ===
    count_sf_upper = content.count('Softfork')
    count_sf_lower = content.count('softfork')

    if count_sf_upper > 0:
        content = content.replace('Softfork', 'Soft fork')
        changes.append(f"FIX 7: Replaced 'Softfork' ({count_sf_upper} occurrences)")
    if count_sf_lower > 0:
        content = content.replace('softfork', 'soft fork')
        changes.append(f"FIX 7: Replaced 'softfork' ({count_sf_lower} occurrences)")
    if count_sf_upper == 0 and count_sf_lower == 0:
        changes.append("FIX 7: No 'Softfork'/'softfork' found")

    # === FIX 8: Fix Corollary 1 SLH-DSA shorthand ===
    # In Corollary 1: "SHA2-256 pre-image resistance" → "SHA2-256 one-wayness and PRF properties (FIPS 205)"
    # Corollary 1 is inside a theorem-box with "Corollary 1"
    # The exact text: "the EUF-CMA security of SLH-DSA-SHA2-128f (SHA2-256 pre-image resistance)"
    old_cor1 = 'the EUF-CMA security of SLH-DSA-SHA2-128f (SHA2-256 pre-image resistance)'
    new_cor1 = 'the EUF-CMA security of SLH-DSA-SHA2-128f (SHA2-256 one-wayness and PRF properties (FIPS 205))'

    if old_cor1 in content:
        content = content.replace(old_cor1, new_cor1)
        changes.append("FIX 8: Fixed Corollary 1 SLH-DSA shorthand")
    else:
        changes.append("FIX 8: WARNING - Corollary 1 SLH-DSA text not found")

    # === FIX 9: Fix FALCON security description ===
    # "SIS over NTRU lattices" → "the NTRU assumption and SIS over NTRU lattices"
    # But ONLY in descriptive text, NOT in formal theorem (Theorem 1)
    # We need to be careful: don't touch Theorem 1
    # The descriptive instances:
    #   - In the contributions list: "break MLWE, SIS over NTRU lattices, and the one-wayness"
    #   - In §11 open problems: "MLWE, SIS over NTRU, and hash pre-image resistance"
    #   - In FALCON description (§2.2): "Security rests on the Short Integer Solution (SIS) assumption over NTRU lattices"

    # Instance in contributions list (line ~420)
    old_falcon_desc1 = 'break MLWE, SIS over NTRU lattices, and the one-wayness'
    new_falcon_desc1 = 'break MLWE, the NTRU assumption and SIS over NTRU lattices, and the one-wayness'

    if old_falcon_desc1 in content:
        content = content.replace(old_falcon_desc1, new_falcon_desc1)
        changes.append("FIX 9a: Fixed FALCON security description in contributions list")
    else:
        changes.append("FIX 9a: Contributions list FALCON text not found")

    # Instance in §11 open problems: "MLWE, SIS over NTRU, and hash"
    old_falcon_desc2 = 'MLWE, SIS over NTRU, and hash pre-image resistance'
    new_falcon_desc2 = 'MLWE, the NTRU assumption and SIS over NTRU lattices, and hash pre-image resistance'

    if old_falcon_desc2 in content:
        content = content.replace(old_falcon_desc2, new_falcon_desc2)
        changes.append("FIX 9b: Fixed FALCON security description in §11")
    else:
        changes.append("FIX 9b: §11 FALCON text not found")

    # === FIX 10: Fix ML-DSA description completeness ===
    # Where ML-DSA is described as resting on "MLWE" alone, change to "MLWE and MSIS (Module-SIS)"
    # But only in descriptive text, not formal statements

    # §2.2 ML-DSA description: "Security rests on the Module Learning With Errors (MLWE) assumption over module lattices"
    old_mldsa = 'Security rests on the Module Learning With Errors (MLWE) assumption over module lattices'
    new_mldsa = 'Security rests on the Module Learning With Errors (MLWE) and Module-SIS (MSIS) assumptions over module lattices'

    if old_mldsa in content:
        content = content.replace(old_mldsa, new_mldsa)
        changes.append("FIX 10a: Fixed ML-DSA description in §2.2")
    else:
        changes.append("FIX 10a: §2.2 ML-DSA description not found")

    # §6.4 "Why these three families": "ML-DSA-65 relies on the Module Learning With Errors (MLWE) problem over structured polynomial modules"
    old_mldsa2 = 'ML-DSA-65 relies on the Module Learning With Errors (MLWE) problem over structured polynomial modules'
    new_mldsa2 = 'ML-DSA-65 relies on the Module Learning With Errors (MLWE) and Module-SIS (MSIS) problems over structured polynomial modules'

    if old_mldsa2 in content:
        content = content.replace(old_mldsa2, new_mldsa2)
        changes.append("FIX 10b: Fixed ML-DSA description in §6.4")
    else:
        changes.append("FIX 10b: §6.4 ML-DSA description not found")

    return content, changes


def main():
    total_changes = 0
    for filepath in FILES:
        if not os.path.exists(filepath):
            print(f"\nSKIPPED (not found): {filepath}")
            continue

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        new_content, changes = apply_fixes(content, filepath)

        short_name = os.path.basename(filepath)
        parent = os.path.basename(os.path.dirname(filepath))
        display = f"{parent}/{short_name}"

        print(f"\n{'='*60}")
        print(f"FILE: {display}")
        print(f"{'='*60}")
        for c in changes:
            print(f"  {c}")
            if "WARNING" not in c and "not found" not in c.lower():
                total_changes += 1

        if new_content != content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"  >>> FILE WRITTEN")
        else:
            print(f"  >>> NO CHANGES MADE")

    print(f"\n{'='*60}")
    print(f"TOTAL INDIVIDUAL FIX APPLICATIONS: {total_changes}")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
