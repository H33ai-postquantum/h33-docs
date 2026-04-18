#!/usr/bin/env python3
"""Apply 6 targeted fixes to all 8 H33 whitepaper HTML files."""

import re
import os
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

def apply_fixes(content, filename):
    changes = []

    # FIX 1: Definition 6 length prefix specification
    old1 = "length-prefixed construction that prevents concatenation ambiguity. The canonical byte encoding"
    new1 = "length-prefixed construction that prevents concatenation ambiguity. All len() fields are encoded as 4-byte big-endian unsigned integers. The canonical byte encoding"
    if old1 in content:
        content = content.replace(old1, new1)
        changes.append("FIX 1: Added len() field encoding specification to Definition 6")
    elif "All len() fields are encoded as 4-byte big-endian unsigned integers" in content:
        changes.append("FIX 1: Already applied")
    else:
        changes.append("FIX 1: WARNING - pattern not found!")

    # FIX 2: Timestamp overflow year
    old2 = "584,942,417"
    new2 = "584,944,387"
    count2 = content.count(old2)
    if count2 > 0:
        content = content.replace(old2, new2)
        changes.append(f"FIX 2: Replaced {count2} occurrence(s) of 584,942,417 -> 584,944,387")
    elif new2 in content:
        changes.append("FIX 2: Already applied")
    else:
        changes.append("FIX 2: WARNING - pattern not found!")

    # FIX 3a: KAT count 18 -> 17+1 (first pattern)
    old3a = "18 Known Answer Test (KAT) validations"
    new3a = "17 per-family Known Answer Test (KAT) validations plus 1 cross-family independence check (18 total)"
    if old3a in content:
        content = content.replace(old3a, new3a)
        changes.append("FIX 3a: Updated KAT count description")
    elif "17 per-family Known Answer Test" in content:
        changes.append("FIX 3a: Already applied")
    else:
        changes.append("FIX 3a: WARNING - pattern not found!")

    # FIX 3b: "All 18 tests pass."
    old3b = "All 18 tests pass."
    new3b = "All 18 tests pass (17 per-family KATs + 1 three-family independence verification)."
    if old3b in content:
        content = content.replace(old3b, new3b)
        changes.append("FIX 3b: Updated 'All 18 tests pass' sentence")
    elif "17 per-family KATs + 1 three-family independence verification" in content:
        changes.append("FIX 3b: Already applied")
    else:
        changes.append("FIX 3b: WARNING - pattern not found!")

    # FIX 4: Rendering artifact — unrendered HTML entities
    old4 = "(2&sup3;&sup2; &minus; 1)&sup2; &asymp; 2&sup6;&sup4;"
    new4 = "(2<sup>32</sup> &minus; 1)<sup>2</sup> &asymp; 2<sup>64</sup>"
    if old4 in content:
        content = content.replace(old4, new4)
        changes.append("FIX 4: Replaced broken &sup entities with proper <sup> tags")
    elif new4 in content:
        changes.append("FIX 4: Already applied")
    else:
        changes.append("FIX 4: Pattern not found (may not be in this file)")

    # Also replace any other remaining standalone &supX; entities
    remaining_sup = re.findall(r'&sup(\d);', content)
    if remaining_sup:
        changes.append(f"  FIX 4 extra: Found {len(remaining_sup)} remaining &sup entities, replacing")
        content = re.sub(r'&sup(\d);', r'<sup>\1</sup>', content)

    # FIX 5: QSB table row hardness description
    old5 = "One assumption (hash pre-image)"
    new5 = "Single hardness class (hash one-wayness)"
    if old5 in content:
        content = content.replace(old5, new5)
        changes.append("FIX 5: Updated hardness description in QSB table")
    elif new5 in content:
        changes.append("FIX 5: Already applied")
    else:
        changes.append("FIX 5: WARNING - pattern not found!")

    # FIX 6: FindAndDelete reference
    old6 = "Bitcoin-specific primitives like FindAndDelete"
    new6 = "Bitcoin-specific script facilities such as OP_CHECKSIG and Taproot tagged hashes"
    if old6 in content:
        content = content.replace(old6, new6)
        changes.append("FIX 6: Replaced FindAndDelete reference")
    elif new6 in content:
        changes.append("FIX 6: Already applied")
    else:
        changes.append("FIX 6: WARNING - pattern not found!")

    return content, changes


def verify(content, filename):
    """Run verification checks on the modified content."""
    issues = []

    if "584,942,417" in content:
        issues.append("FAIL: Still contains 584,942,417")
    if "584,944,387" not in content:
        issues.append("FAIL: Does not contain 584,944,387")
    if "18 Known Answer Test (KAT) validations" in content:
        issues.append("FAIL: Still contains old '18 Known Answer' text")
    if "FindAndDelete" in content:
        issues.append("FAIL: Still contains FindAndDelete")
    sup_entities = re.findall(r'&sup\d;', content)
    if sup_entities:
        issues.append(f"FAIL: Still contains &sup entities: {sup_entities[:5]}")
    if "One assumption (hash pre-image)" in content:
        issues.append("FAIL: Still contains old hardness description")

    return issues


def main():
    total_errors = 0

    for filepath in FILES:
        print(f"\n{'='*80}")
        print(f"Processing: {filepath}")
        print(f"{'='*80}")

        if not os.path.exists(filepath):
            print(f"  ERROR: File not found!")
            total_errors += 1
            continue

        with open(filepath, 'r', encoding='utf-8') as f:
            original = f.read()

        modified, changes = apply_fixes(original, filepath)

        for change in changes:
            print(f"  {change}")

        # Verify
        issues = verify(modified, filepath)
        if issues:
            for issue in issues:
                print(f"  VERIFY {issue}")
            total_errors += len(issues)
        else:
            print(f"  VERIFY: All checks passed")

        # Write back
        if modified != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(modified)
            print(f"  WRITTEN: {len(original)} -> {len(modified)} bytes")
        else:
            print(f"  NO CHANGES (all fixes already applied or patterns missing)")

    print(f"\n{'='*80}")
    print(f"SUMMARY: {total_errors} verification errors")
    print(f"{'='*80}")

    return total_errors


if __name__ == "__main__":
    sys.exit(main())
