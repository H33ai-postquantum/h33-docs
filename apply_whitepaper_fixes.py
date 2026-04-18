#!/usr/bin/env python3
"""
Apply 7 whitepaper improvements to all 8 H33-74 whitepaper HTML files.

Fixes:
1. Add timestamp authenticity note to §1.2 (item 5 to "does not prove" list)
2. Normalize FALCON hardness description to "NTRU-SIS"
3. Move lattice-independence argument from §11 to §6
4. Add verification cost reconciliation note to §7.5
5. Add key binding/rotation note to §3.1
6. Abstract em-dash cleanup
7. §10.2 DSSE fairness tighten
"""

import os
import re
import sys

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

def apply_fix_1(content):
    """Add timestamp authenticity note to §1.2 — item (5) to 'does not prove' list."""
    old = ('the primitive commits to a digest, not to storage.</p>')
    new = ('the primitive commits to a digest, not to storage; '
           'or (5) that the timestamp &tau; reflects the actual time of computation &mdash; '
           'the timestamp is signer-asserted and a compromised signer can backdate primitives. '
           'The Bitcoin anchor proves commitment to chain by a specific block height, not production at time &tau;.</p>')
    if old not in content:
        print("    FIX 1: WARNING - target text not found (may already be applied)")
        return content
    content = content.replace(old, new)
    print("    FIX 1: Added timestamp authenticity note to §1.2")
    return content


def apply_fix_2(content):
    """Normalize FALCON hardness description to NTRU-SIS.

    First occurrence in §2.2 gets the gloss: "NTRU-SIS (the Short Integer Solution problem over NTRU lattices)"
    All other occurrences become just "NTRU-SIS".
    Do NOT touch text inside Theorem 1 or Corollary 1.
    """
    count = 0

    # §2.2 first occurrence: "Short Integer Solution (SIS) assumption over NTRU lattices"
    # This is the FALCON-512 description paragraph
    old_2_2 = 'Security rests on the Short Integer Solution (SIS) assumption over NTRU lattices'
    new_2_2 = 'Security rests on NTRU-SIS (the Short Integer Solution problem over NTRU lattices)'
    if old_2_2 in content:
        content = content.replace(old_2_2, new_2_2)
        count += 1
        print("    FIX 2a: Glossed first NTRU-SIS occurrence in §2.2")

    # §1 contributions list: "the NTRU assumption and SIS over NTRU lattices"
    # This appears in line 420 (contributions list) and line 1305 (§11.1)
    old_contrib = 'MLWE, the NTRU assumption and SIS over NTRU lattices, and the one-wayness'
    new_contrib = 'MLWE, NTRU-SIS, and the one-wayness'
    if old_contrib in content:
        content = content.replace(old_contrib, new_contrib)
        count += 1
        print("    FIX 2b: Normalized 'the NTRU assumption and SIS over NTRU lattices' in contributions/§11")

    # §11.1: "MLWE, the NTRU assumption and SIS over NTRU lattices, and hash pre-image resistance"
    old_11 = 'MLWE, the NTRU assumption and SIS over NTRU lattices, and hash pre-image resistance'
    new_11 = 'MLWE, NTRU-SIS, and hash pre-image resistance'
    if old_11 in content:
        content = content.replace(old_11, new_11)
        count += 1
        print("    FIX 2c: Normalized in §11.1 opening")

    # Abstract line 278: "Short Integer Solution over NTRU lattices (FALCON)"
    old_abs = 'Short Integer Solution over NTRU lattices (FALCON)'
    new_abs = 'NTRU-SIS (FALCON)'
    if old_abs in content:
        content = content.replace(old_abs, new_abs)
        count += 1
        print("    FIX 2d: Normalized in abstract")

    # §6.4 "Why these three families": "Short Integer Solution (SIS) problem over NTRU lattice rings"
    old_64 = 'the Short Integer Solution (SIS) problem over NTRU lattice rings'
    new_64 = 'NTRU-SIS (the Short Integer Solution problem over NTRU lattice rings)'
    if old_64 in content:
        content = content.replace(old_64, new_64)
        count += 1
        print("    FIX 2e: Normalized in §6.4")

    # Check for any remaining "SIS over NTRU" that isn't inside Theorem 1 or Corollary 1
    # and isn't already "NTRU-SIS"
    remaining = [m.start() for m in re.finditer(r'SIS over NTRU', content)]
    # Filter out ones inside theorem-box or that are part of "NTRU-SIS"
    for pos in remaining:
        context = content[max(0, pos-200):pos+200]
        if 'NTRU-SIS' not in context[180:220]:  # not already prefixed
            if 'thm-label' not in context and 'Theorem 1' not in context:
                print(f"    FIX 2: WARNING - remaining 'SIS over NTRU' at pos {pos}")

    if count == 0:
        print("    FIX 2: WARNING - no substitutions made (may already be applied)")
    else:
        print(f"    FIX 2: Total {count} NTRU-SIS normalizations applied")

    return content


def apply_fix_3(content):
    """Move lattice-independence argument from §11 to §6.

    Insert new paragraph into §6 after Corollary 1 discussion.
    Add forward reference to §11.1.
    """
    # Check if already applied
    if 'Structural separation of the two lattice families' in content:
        print("    FIX 3: Already applied (structural separation paragraph found in content)")
        return content

    # INSERT into §6: after the paragraph that says "We do not claim a formal composition theorem"
    # which ends with "We consider this a reasonable engineering bet, not a provable theorem.</p>"
    insertion_marker = 'We consider this a reasonable engineering bet, not a provable theorem.</p>'

    new_paragraph = """

<p><strong>Structural separation of the two lattice families.</strong> A natural objection is that ML-DSA and FALCON are both &ldquo;lattice-based&rdquo; and therefore not truly independent. We address this directly. ML-DSA&rsquo;s security rests on Module-LWE over structured module lattices; FALCON&rsquo;s rests on NTRU-SIS over NTRU lattices. These are algebraically distinct objects: MLWE operates over the module Z<sub>q</sub><sup>k</sup>[x]/(x<sup>n</sup>+1), while NTRU-SIS operates over the quotient ring Z<sub>q</sub>[x]/(x<sup>n</sup>+1) with the NTRU structure f&middot;g<sup>&minus;1</sup>. No polynomial-time reduction between MLWE and NTRU-SIS is known at cryptographically useful parameters. The best known attacks against each use different algorithmic strategies: BKZ-style lattice reduction for MLWE, and NTRU-specific combinatorial attacks for FALCON. A cryptanalytic advance against one does not imply progress against the other. We treat this as an engineering observation, not a formal independence proof, and flag it as an open problem in &sect;11.1.</p>"""

    if insertion_marker not in content:
        print("    FIX 3: WARNING - §6 insertion marker not found")
        return content

    content = content.replace(insertion_marker, insertion_marker + new_paragraph)
    print("    FIX 3a: Inserted structural separation paragraph into §6")

    # Add forward reference at start of §11.1
    old_11_1_opening = ('<p>The three-family security argument of Section 6 relies on the informal claim that')
    new_11_1_opening = ('<p>The structural separation argument is presented in &sect;6; here we discuss the formal open question. '
                        'The three-family security argument of Section 6 relies on the informal claim that')

    if old_11_1_opening in content:
        content = content.replace(old_11_1_opening, new_11_1_opening)
        print("    FIX 3b: Added forward reference to §11.1")
    else:
        print("    FIX 3b: WARNING - §11.1 opening not found for forward reference")

    return content


def apply_fix_4(content):
    """Add verification cost reconciliation note to §7.5."""
    # Check if already applied
    if 'scheduling overhead, memory allocation' in content:
        print("    FIX 4: Already applied")
        return content

    old = '<p>The verification cost is dominated by the three individual signature verifications, which are independent and parallelizable.</p>'
    new = ('<p>The verification cost is dominated by the three individual signature verifications, which are independent and parallelizable. '
           '(The difference between the component sum and the measured total reflects scheduling overhead, memory allocation, '
           'and serialization costs not attributable to any single cryptographic operation.)</p>')

    if old not in content:
        print("    FIX 4: WARNING - target text not found")
        return content

    content = content.replace(old, new)
    print("    FIX 4: Added verification cost reconciliation note to §7.5")
    return content


def apply_fix_5(content):
    """Add key binding/rotation note to §3.1."""
    # Check if already applied
    if 'bound to a specific public key set via the verification digest' in content:
        print("    FIX 5: Already applied")
        return content

    # Insert after the §3.1 lifecycle paragraph that discusses re-verification.
    # The paragraph ends with "The primitive S is not reconstructible from the 32-byte on-chain anchor alone.</p>"
    marker = 'The primitive S is not reconstructible from the 32-byte on-chain anchor alone.</p>'

    new_sentence = """

<p>Note that the compact receipt R is bound to a specific public key set via the verification digest c. After key rotation, old receipts can only be reverified against the original public keys; the new key set produces distinct receipts.</p>"""

    if marker not in content:
        print("    FIX 5: WARNING - §3.1 insertion marker not found")
        return content

    content = content.replace(marker, marker + new_sentence)
    print("    FIX 5: Added key binding/rotation note to §3.1")
    return content


def apply_fix_6(content):
    """Abstract em-dash cleanup — replace 3rd em-dash in the abstract sentence with a period."""
    old = ('not merely the weakest &mdash; the security design relies on assumption diversity '
           'rather than NIST-level parity (&sect;6.3)')
    new = ('not merely the weakest. The security design relies on assumption diversity '
           'rather than NIST-level parity (&sect;6.3)')

    if old not in content:
        print("    FIX 6: WARNING - target text not found (may already be applied)")
        return content

    content = content.replace(old, new)
    print("    FIX 6: Cleaned up abstract em-dash")
    return content


def apply_fix_7(content):
    """§10.2 DSSE fairness tighten.

    DSSE does support payload-type context strings (payloadType field).
    Change comparison to focus on: no batch aggregation, single-family signing, no chain anchoring.
    """
    old = 'DSSE (no batching, no domain separation)'
    new = 'DSSE (no batch aggregation, single-family signing, no chain anchoring)'

    if old not in content:
        print("    FIX 7: WARNING - target text not found (may already be applied)")
        return content

    content = content.replace(old, new)
    print("    FIX 7: Tightened DSSE comparison in §10.2")
    return content


def process_file(filepath):
    """Apply all 7 fixes to a single file."""
    print(f"\n  Processing: {filepath}")

    if not os.path.exists(filepath):
        print(f"    ERROR: File not found!")
        return False

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    content = apply_fix_1(content)
    content = apply_fix_2(content)
    content = apply_fix_3(content)
    content = apply_fix_4(content)
    content = apply_fix_5(content)
    content = apply_fix_6(content)
    content = apply_fix_7(content)

    if content == original:
        print("    NO CHANGES (all fixes may already be applied)")
        return True

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"    SAVED ({len(content)} bytes)")
    return True


def verify_file(filepath):
    """Verify all 7 fixes were applied to a file."""
    print(f"\n  Verifying: {os.path.basename(filepath)}")

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    checks = {
        "Fix 1 (timestamp note)": "the timestamp is signer-asserted" in content,
        "Fix 2 (NTRU-SIS gloss)": "NTRU-SIS (the Short Integer Solution problem over NTRU lattice" in content,
        "Fix 3 (structural separation in §6)": "Structural separation of the two lattice families" in content,
        "Fix 3b (§11.1 forward ref)": "The structural separation argument is presented in" in content,
        "Fix 4 (verification cost)": "scheduling overhead, memory allocation" in content,
        "Fix 5 (key binding note)": "bound to a specific public key set via the verification digest" in content,
        "Fix 6 (abstract em-dash)": "not merely the weakest. The security design" in content,
        "Fix 7 (DSSE tighten)": "DSSE (no batch aggregation, single-family signing, no chain anchoring)" in content,
    }

    all_pass = True
    for name, result in checks.items():
        status = "PASS" if result else "FAIL"
        if not result:
            all_pass = False
        print(f"    {status}: {name}")

    # Negative checks
    neg_checks = {
        "No old DSSE text": "DSSE (no batching, no domain separation)" not in content,
        "No old abstract em-dash": ("not merely the weakest &mdash; the security design" not in content),
        "Old §1 contrib normalized": ("the NTRU assumption and SIS over NTRU lattices, and the one-wayness" not in content),
    }

    for name, result in neg_checks.items():
        status = "PASS" if result else "FAIL"
        if not result:
            all_pass = False
        print(f"    {status}: {name}")

    return all_pass


def main():
    print("=" * 70)
    print("H33-74 Whitepaper — Applying 7 improvements to 8 files")
    print("=" * 70)

    # Apply fixes
    success_count = 0
    for f in FILES:
        if process_file(f):
            success_count += 1

    print(f"\n{'=' * 70}")
    print(f"Applied to {success_count}/{len(FILES)} files")
    print(f"{'=' * 70}")

    # Verify
    print("\n\nVERIFICATION")
    print("=" * 70)

    all_pass = True
    for f in FILES:
        if not verify_file(f):
            all_pass = False

    print(f"\n{'=' * 70}")
    if all_pass:
        print("ALL CHECKS PASSED across all 8 files.")
    else:
        print("SOME CHECKS FAILED — review output above.")
    print(f"{'=' * 70}")

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
