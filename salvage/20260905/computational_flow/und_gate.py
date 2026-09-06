#!/usr/bin/env python3
"""und physics gate — R_equilibrium = 0.8158. Reject ΔR > threshold. Offline only."""
import json, time, hashlib
R_EQ = 0.8158

def encode_frame(tokens, r_measured=0.82):
    if abs(r_measured - R_EQ) > 0.05:
        return None  # rejected
    frame = {"t": tokens, "r": r_measured, "ts": time.time_ns()}
    frame["h"] = hashlib.sha256(json.dumps(frame, sort_keys=True).encode()).hexdigest()[:16]
    return frame

def decode_and_verify(frame):
    if not frame or abs(frame.get("r", 0) - R_EQ) > 0.05:
        return None
    return frame["t"]

if __name__ == "__main__":
    f = encode_frame(["community_lung", "delta_t", "raise_lowest"], 0.82)
    print(f)
    print(decode_and_verify(f))
