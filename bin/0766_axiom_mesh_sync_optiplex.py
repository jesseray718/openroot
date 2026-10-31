
# Append to pack() function before closing brace
def pack_full():
    """Pack engine + proof cache."""
    from pathlib import Path
    STORE = Path("/home/jesse/openroot/axiom_engine/store")
    OUT = STORE.parent / "inbox" / "axiom_engine_optiplex.tar.gz"
    tmp = OUT.with_suffix(".tar.tmp")
    with tarfile.open(tmp, "w:gz") as tf:
        tf.add(STORE.parent / "axiom_engine", arcname="axiom_engine")
        cache = STORE / "proof_cache.json"
        if cache.exists():
            tf.add(cache, arcname="proof_cache.json")
    shutil.move(str(tmp), str(OUT))
    return {"tarball": str(OUT), "cache_included": cache.exists()}
