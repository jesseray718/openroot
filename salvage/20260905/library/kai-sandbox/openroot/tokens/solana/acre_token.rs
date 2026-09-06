use anchor_lang::prelude::*;
use anchor_spl::token::{self, Mint, Token, TokenAccount, MintTo};

declare_id!("3fF26gcj1ednMUASxJxo1dt5rQ2ZegXbH7k4ynJazerk");

#[program]
pub mod acre_token {
    use super::*;

    pub fn initialize(ctx: Context<Initialize>) -> Result<()> {
        Ok(())
    }

    // PoPW verified mint - two-approval flow enforced off-chain via Kingdom Engine
    // or future multisig/PDA. Matches Python validator logic.
    pub fn mint_ppw_verified(
        ctx: Context<MintPpwVerified>,
        amount: u64,
        work_units: u64,      // joules saved, sq ft built, food lbs, etc.
        proof_hash: String,   // hash of physical work attestation
    ) -> Result<()> {
        let cpi_accounts = MintTo {
            mint: ctx.accounts.mint.to_account_info(),
            to: ctx.accounts.to.to_account_info(),
            authority: ctx.accounts.authority.to_account_info(),
        };
        let cpi_program = ctx.accounts.token_program.to_account_info();
        let cpi_ctx = CpiContext::new(cpi_program, cpi_accounts);
        token::mint_to(cpi_ctx, amount)?;

        emit!(PpwMinted {
            work_units,
            proof_hash,
            amount,
        });
        Ok(())
    }
}

#[derive(Accounts)]
pub struct Initialize<'info> {
    #[account(init, payer = payer, mint::decimals = 9, mint::authority = authority)]
    pub mint: Account<'info, Mint>,
    #[account(mut)]
    pub payer: Signer<'info>,
    pub authority: Signer<'info>,
    pub system_program: Program<'info, System>,
    pub token_program: Program<'info, Token>,
    pub rent: Sysvar<'info, Rent>,
}

#[derive(Accounts)]
pub struct MintPpwVerified<'info> {
    #[account(mut)]
    pub mint: Account<'info, Mint>,
    #[account(mut)]
    pub to: Account<'info, TokenAccount>,
    pub authority: Signer<'info>,  // expand to two-authority or PDA in next iteration
    pub token_program: Program<'info, Token>,
}

#[event]
pub struct PpwMinted {
    pub work_units: u64,
    pub proof_hash: String,
    pub amount: u64,
}
