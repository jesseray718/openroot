// acre_attest.rs — ACRE PoPW Anchor program STUB (DRAFT; not yet compiled)
use anchor_lang::prelude::*;
declare_id!("ACRE11111111111111111111111111111111111111111");

#[program]
pub mod acre_attest {
    use super::*;
    pub fn mint_attestation(ctx: Context<MintAttest>, source: String,
                            joules: f64, claim_hash: String, grade: String) -> Result<()> {
        require!(grade == String::from("MEASURED"), AttestError::NotMeasured);
        emit!(Attested { source, joules, claim_hash });
        Ok(())
    }
}
#[derive(Accounts)] pub struct MintAttest<'info> { #[account(mut)] pub payer: Signer<'info> }
#[event] pub struct Attested { pub source: String, pub joules: f64, pub claim_hash: String }
#[error_code] pub enum AttestError { #[msg("only MEASURED rows may mint")] NotMeasured }
