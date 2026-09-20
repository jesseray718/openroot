"""Exponent validation: routing contrast, not random-ratio.
Hypothesis: weight(p) = (1 - p/100)^k. Contrast = weight(10th)/weight(90th).
Predicted: k=1 -> 9x, k=2 -> 81x. Observed demo claim ~26x implies effective
k ~ 1.54. Question for v2: is quadratic justified, or is measured reality sub-quadratic?
Pure-python (no numpy): fits Termux + OptiPlex."""
def contrast(k, p_lo=10, p_hi=90):
    w_lo = (1 - p_lo/100) ** k
    w_hi = (1 - p_hi/100) ** k
    return w_lo / w_hi if w_hi else float("inf")

def implied_exponent(observed, p_lo=10, p_hi=90):
    lo, hi = 0.0, 4.0
    for _ in range(100):
        mid = (lo + hi) / 2
        if contrast(mid, p_lo, p_hi) < observed: lo = mid
        else: hi = mid
    return (lo + hi) / 2

if __name__ == "__main__":
    print("[PREDICTED] k=1 (linear): %.1fx | k=2 (quadratic): %.1fx bottom-vs-top routing contrast" % (contrast(1), contrast(2)))
    print("[DEMO] contribution_tier_v2 observed 67.05 vs 2.5 = %.1fx apparent contrast" % (67.05/2.5))
    print("[IMPLIED] demo effective exponent k ~= %.2f" % implied_exponent(67.05/2.5))
    print("[NOTE] demo contrast mixes unequal benefit splits too — v2 sim must isolate routing from volume before concluding")
