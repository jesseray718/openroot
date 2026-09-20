== STAGE A [truth-scan] 36 candidate repos via git ls-remote ==
[banked] jesseray718/.github :: master GONE (earlier 'PRESENT' was API redirect)
[banked] jesseray718/AeroCement_Ecosystem :: master GONE (earlier 'PRESENT' was API redirect)
[banked] jesseray718/OpenCell-Thermal-System :: master GONE (earlier 'PRESENT' was API redirect)
[banked] jesseray718/aerocement :: master GONE (earlier 'PRESENT' was API redirect)
[banked] jesseray718/aerocement-calc :: master GONE (earlier 'PRESENT' was API redirect)
[banked] jesseray718/agape-coordination :: master GONE (earlier 'PRESENT' was API redirect)
[banked] jesseray718/agape-crossover-key :: master GONE (earlier 'PRESENT' was API redirect)
[banked] jesseray718/agape-ipfs :: master GONE (earlier 'PRESENT' was API redirect)
[banked] jesseray718/agape-primitives :: master GONE (earlier 'PRESENT' was API redirect)
[banked] jesseray718/agape-une :: master GONE (earlier 'PRESENT' was API redirect)
[banked] jesseray718/agapenet :: master GONE (earlier 'PRESENT' was API redirect)
[banked] jesseray718/agaperesonance :: master GONE (earlier 'PRESENT' was API redirect)
[banked] jesseray718/axiom-library :: master GONE (earlier 'PRESENT' was API redirect)
[banked] jesseray718/black-locust-rmh :: master GONE (earlier 'PRESENT' was API redirect)
[banked] jesseray718/canonical :: master GONE (earlier 'PRESENT' was API redirect)
[banked] jesseray718/civilization2.0 :: master GONE (earlier 'PRESENT' was API redirect)
[banked] jesseray718/etaledger :: master GONE (earlier 'PRESENT' was API redirect)
[banked] jesseray718/fractallattice :: master GONE (earlier 'PRESENT' was API redirect)
[banked] jesseray718/jesseray718 :: master GONE (earlier 'PRESENT' was API redirect)
[banked] jesseray718/jesseray718-archive :: master GONE (earlier 'PRESENT' was API redirect)
[banked] jesseray718/jesseray718.github.io :: master GONE (earlier 'PRESENT' was API redirect)
[banked] jesseray718/kai-memory :: master GONE (earlier 'PRESENT' was API redirect)
[banked] jesseray718/kai9000 :: master GONE (earlier 'PRESENT' was API redirect)
[banked] jesseray718/openroot :: master GONE (earlier 'PRESENT' was API redirect)
[banked] jesseray718/openroot-canon :: master GONE (earlier 'PRESENT' was API redirect)
[banked] jesseray718/openroot-ecosystem :: master GONE (earlier 'PRESENT' was API redirect)
[banked] jesseray718/openroot-foundation :: master GONE (earlier 'PRESENT' was API redirect)
[banked] jesseray718/openroot-product :: master GONE (earlier 'PRESENT' was API redirect)
[banked] jesseray718/openroot-spoke-template :: master GONE (earlier 'PRESENT' was API redirect)
[banked] jesseray718/openroot-thesis :: master GONE (earlier 'PRESENT' was API redirect)
[banked] jesseray718/oscillation-mesh :: master GONE (earlier 'PRESENT' was API redirect)
[banked] jesseray718/renaissance-protocol :: master GONE (earlier 'PRESENT' was API redirect)
[banked] jesseray718/skills-introduction-to-github :: master GONE (earlier 'PRESENT' was API redirect)
[banked] jesseray718/und-protocol :: master GONE (earlier 'PRESENT' was API redirect)
[banked] jesseray718/une :: master GONE (earlier 'PRESENT' was API redirect)
[banked] jesseray718/wisdom-scaffold :: master GONE (earlier 'PRESENT' was API redirect)
== STAGE B [delete] 0 real masters, 0 unscannable ==
== STAGE C [final-truth] ls-remote recheck ==

## Handoff 20260920_024736
mode=DRY-RUN
real=0 errs=0 ok=0 fail=0 still_non_gone=0
CONCLUSION: branches endpoint shows redirect phantoms; refs endpoint + ls-remote are ground truth.
RULE: never existence-check via /branches/ after renames.
next: if still_non_gone>0 inspect those repos manually (likely branch protection); else fleet is clean, close the master purge campaign.
