# Claims Registry
| id | claim | grade | evidence | n |
|----|-------|-------|----------|---|
| A01 | Flag is FLAG-XX-sha256[:16] over {kind,id,statement,premises,proof} | MODEL | axiom_engine.py content_hash | N10 |
| A02 | Second prove of the same body returns hit true recomputed false | MODEL | axiom_engine.py prove_and_flag | N08 |
| A03 | C(6,1,1.0)=0.0 is a HARD theorem hung at seed | MODEL | eval_c + TH-C0 | N03 |
| A04 | 7B cannot hang a new axiom without hang-axiom --confirm | MODEL | upsert axiom guard + N16 | N16 |
| A05 | Soft-rule proofs hang as postulates not theorems | MODEL | prove_and_flag used_soft | N14 |
| A06 | llama-server 7-8B Q4 on OptiPlex is the proposer | OPEN | coder_loop.py default URL | N07 |
| A07 | Phone 7B coder is a waste of Helio G99 joules | OPEN | openroot-stack one-hot RAM | N01 |
