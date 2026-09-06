import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from acre_validator import submit_claim, approve_claim, finalize_mint_ready

def test_submit_and_two_approvals_mint_ready():
    c = submit_claim("HW.VAL.NODE.ZERO", "First thermal node in Zone 5b", ["https://ipfs.io/test"], "test_user")
    assert c.claim_id.startswith("ACRE-")
    c = approve_claim(c, "alice")
    c = approve_claim(c, "bob")
    assert c.status == "approved"
    rec = finalize_mint_ready(c)
    assert rec["claim"]["status"] == "mint_ready"

def test_duplicate_approval_ignored():
    c = submit_claim("SW.TOOL.NEW", "new tool", ["https://example.com/e"], "u")
    c = approve_claim(c, "alice")
    c = approve_claim(c, "alice")
    assert c.validators == ["alice"]
    assert c.status == "pending"

def test_invalid_score_rejected():
    try:
        submit_claim("NOT.A.TYPE", "test", [], "u2")
        assert False
    except ValueError:
        pass
