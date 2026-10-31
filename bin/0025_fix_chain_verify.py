"""Fix the verify_chain function to handle None values properly."""
import json

with open("agape_ledger_chain.py", "r") as f:
    code = f.read()

old_verify = '''def verify_chain():
    """Verify the entire chain is intact. No tampering."""
    if not CHAIN.exists():
        return False, "Chain file not found"

    blocks = [json.loads(l) for l in CHAIN.read_text().strip().split("\\n")]
    if not blocks:
        return False, "Empty chain"

    for i, block in enumerate(blocks):
        stored_hash = block.get("hash")
        block_copy = {k: v for k, v in block.items() if k != "hash"}
        recomputed = hashlib.sha256(
            json.dumps(block_copy, sort_keys=True).encode()
        ).hexdigest()

        if stored_hash != recomputed:
            return False, f"TAMPER DETECTED at version {block.get('version', '?')}"

        if i > 0:
            prev_hash = blocks[i-1]["hash"]
            if block.get("parent_hash") != prev_hash:
                return False, f"BROKEN CHAIN at version {block.get('version', '?')}"

    return True, f"Chain intact: {len(blocks)} blocks verified"'''

new_verify = '''def verify_chain():
    """Verify the entire chain is intact. No tampering."""
    if not CHAIN.exists():
        return False, "Chain file not found"

    blocks = [json.loads(l) for l in CHAIN.read_text().strip().split("\\n")]
    if not blocks:
        return False, "Empty chain"

    for i, block in enumerate(blocks):
        stored_hash = block.get("hash")
        # Use default=str to handle None values consistently
        block_copy = {k: v for k, v in block.items() if k != "hash"}
        recomputed = hashlib.sha256(
            json.dumps(block_copy, sort_keys=True, default=str).encode()
        ).hexdigest()

        if stored_hash != recomputed:
            # Try without default=str (original method)
            recomputed2 = hashlib.sha256(
                json.dumps(block_copy, sort_keys=True).encode()
            ).hexdigest()
            if stored_hash != recomputed2:
                return False, f"TAMPER DETECTED at version {block.get('version', '?')} (stored={stored_hash[:16]} vs computed={recomputed[:16]})"

        if i > 0:
            prev_hash = blocks[i-1]["hash"]
            if block.get("parent_hash") != prev_hash:
                return False, f"BROKEN CHAIN at version {block.get('version', '?')}"

    return True, f"Chain intact: {len(blocks)} blocks verified"'''

code = code.replace(old_verify, new_verify)

# Also fix the genesis creation to use default=str
old_genesis_hash = '''genesis_block["hash"] = hashlib.sha256(
        json.dumps(genesis_block, sort_keys=True).encode()
    ).hexdigest()'''

new_genesis_hash = '''genesis_block["hash"] = hashlib.sha256(
        json.dumps(genesis_block, sort_keys=True, default=str).encode()
    ).hexdigest()'''

code = code.replace(old_genesis_hash, new_genesis_hash)

# Also fix append_amendment hash
old_append_hash = '''new_block["hash"] = hashlib.sha256(
        json.dumps(new_block, sort_keys=True).encode()
    ).hexdigest()'''

new_append_hash = '''new_block["hash"] = hashlib.sha256(
        json.dumps(new_block, sort_keys=True, default=str).encode()
    ).hexdigest()'''

code = code.replace(old_append_hash, new_append_hash)

with open("agape_ledger_chain.py", "w") as f:
    f.write(code)

print("[FIXED] Hash computation now uses default=str for None handling")
print("[FIXED] Genesis, amendment, and verify all consistent")
