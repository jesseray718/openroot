#!/usr/bin/env python3
"""Test Suite for ACRE Validator"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from acre_validator import ACREValidator

def run_tests():
    print("=== ACRE Validator Test Suite ===\n")
    v = ACREValidator()

    print("Test 1: Submit claim...")
    cid = v.submit_claim("test_user", "First thermal node in Zone 5b", 9, ["https://ipfs.io/test"])
    assert cid.startswith("CLM-")
    print("PASS\n")

    print("Test 2: First approval...")
    assert v.approve_claim(cid, "alice")
    print("PASS\n")

    print("Test 3: Second approval (mint-ready)...")
    assert v.approve_claim(cid, "bob")
    assert v.claims[-1].status == "approved_for_mint"
    print("PASS\n")

    print("Test 4: Duplicate approval rejected...")
    assert not v.approve_claim(cid, "alice")
    print("PASS\n")

    print("Test 5: Invalid score rejected...")
    try:
        v.submit_claim("u2", "test", 15, [])
        print("FAIL\n")
    except ValueError:
        print("PASS\n")

    print("=== ALL TESTS PASSED ===")

if __name__ == "__main__":
    run_tests()
