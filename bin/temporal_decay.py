import sqlite3, time

def apply_decay(chunks):
    now = time.time()
    scored_chunks = []
    for c in chunks:
        mtime = c.get('mtime', now)
        age = now - mtime
        weight = 1.0 / (1.0 + (age / 86400)) # Decay per day
        scored_chunks.append((weight, c))
    return sorted(scored_chunks, key=lambda x: x[0], reverse=True)

if __name__ == "__main__":
    print("[banked] Temporal Decay weighting active. Freshness > Legacy.")
