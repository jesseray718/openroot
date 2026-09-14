# ACRE PoPW Attestation Spec (DRAFT)
1. thermal_sim / physical node emits joule event -> synthesis capabilities row (grade <= MODEL)
2. MEASURED row (3B-grader gate passes) -> acre_attest.py signs claim hash
3. claim hash -> acre_attest.rs mint_attestation on Solana devnet (rejects non-MEASURED)
4. minted ACRE credits the contributions blockchain block that anchored the yield row
5. bounty board prices future work in ACRE; STEP settles fills
