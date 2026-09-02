#!/data/data/com.termux/files/usr/bin/bash
set -e

# ACRE Token — Solana Devnet Deployment
# Prerequisites: solana CLI, anchor, rust toolchain
# Install if missing: sh -c "$(curl -sSfL https://release.solana.com/stable/install)"

echo "═══ ACRE DEVNET DEPLOY ═══"

# Check for solana CLI
if ! command -v solana &>/dev/null; then
  echo "❌ solana CLI not found"
  echo "Install: sh -c \"\$(curl -sSfL https://release.solana.com/stable/install)\""
  echo "Then: export PATH=\"~/.local/share/solana/install/active_release/bin:\$PATH\""
  exit 1
fi

# Configure devnet
solana config set --url https://api.devnet.solana.com
echo "✅ Network: devnet"

# Check/create keypair
KEYPAIR=~/.config/solana/id.json
if [ ! -f "$KEYPAIR" ]; then
  mkdir -p ~/.config/solana
  solana-keygen new -o "$KEYPAIR" --no-bip39-passphrase
  echo "✅ New keypair generated"
else
  echo "✅ Existing keypair found"
fi

# Get balance
BALANCE=$(solana balance | awk '{print $1}')
echo "Balance: $BALANCE SOL"

# Airdrop if low (devnet allows 2 SOL per request)
if (( $(echo "$BALANCE < 2" | bc -l 2>/dev/null || echo 1) )); then
  echo "Requesting devnet airdrop..."
  solana airdrop 2
  sleep 5
  solana balance
fi

# Navigate to ACRE program
ACRE_DIR=${ACRE_DIR:-~/projects/openroot/programs/acre}
if [ ! -d "$ACRE_DIR" ]; then
  echo "⚠️  ACRE program dir not found at $ACRE_DIR"
  echo "Creating scaffold..."
  mkdir -p "$ACRE_DIR"
  
  # Generate Anchor.toml
  cat > "$ACRE_DIR/Anchor.toml" << 'TOML'
[provider]
cluster = "devnet"
wallet = "~/.config/solana/id.json"

[programs.devnet]
acre = "Replace_with_deployed_address"

[scripts]
test = "yarn test"
TOML
  
  # Generate lib.rs (ACRE Anchor program)
  mkdir -p "$ACRE_DIR/programs/acre/src"
  cat > "$ACRE_DIR/programs/acre/src/lib.rs" << 'RUST'
use anchor_lang::prelude::*;

declare_id!("11111111111111111111111111111111");

#[program]
pub mod acre {
    use super::*;

    pub fn initialize(ctx: Context<Initialize>) -> Result<()> {
        let state = &mut ctx.accounts.state;
        state.authority = ctx.accounts.authority.key();
        state.total_minted = 0;
        state.work_units_joules = 0;
        Ok(())
    }

    pub fn submit_claim(
        ctx: Context<SubmitClaim>,
        claim_type: String,
        description: String,
        evidence_uris: Vec<String>,
        work_joules: u64,
    ) -> Result<()> {
        let claim = &mut ctx.accounts.claim;
        claim.authority = ctx.accounts.authority.key();
        claim.claim_type = claim_type;
        claim.description = description;
        evidence_uris.clone_into(&mut claim.evidence_uris);
        claim.work_joules = work_joules;
        claim.status = ClaimStatus::Pending;
        claim.bump = *ctx.bumps.get("claim").unwrap();

        msg!("Claim submitted: {} joules", work_joules);
        Ok(())
    }

    pub fn approve_claim(ctx: Context<ApproveClaim>, _claim_bump: u8) -> Result<()> {
        let claim = &mut ctx.accounts.claim;
        require!(claim.status == ClaimStatus::Pending, InvalidStatus);
        claim.status = ClaimStatus::ApprovedForMint;

        let state = &mut ctx.accounts.state;
        state.work_units_joules = state.work_units_joules.checked_add(claim.work_joules).unwrap();

        msg!("Claim approved for mint: {} joules", claim.work_joules);
        Ok(())
    }

    pub fn mint_tokens(ctx: Context<MintTokens>, amount: u64) -> Result<()> {
        let state = &mut ctx.accounts.state;
        require!(state.authority == ctx.accounts.authority.key(), Unauthorized);

        // 1 ACRE per 1000 joules (adjustable)
        let tokens = amount.checked_div(1000).unwrap_or(0);
        if tokens == 0 {
            return err!(InsufficientWork);
        }

        // Mint to recipient
        // (Implementation depends on SPL token setup)
        state.total_minted = state.total_minted.checked_add(tokens).unwrap();
        msg!("Minted {} ACRE ({} joules)", tokens, amount);
        Ok(())
    }
}

#[account]
pub struct SystemState {
    pub authority: Pubkey,
    pub total_minted: u64,
    pub work_units_joules: u64,
}

#[account]
pub struct Claim {
    pub authority: Pubkey,
    pub claim_type: String,
    pub description: String,
    pub evidence_uris: Vec<String>,
    pub work_joules: u64,
    pub status: ClaimStatus,
    pub bump: u8,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, PartialEq)]
pub enum ClaimStatus {
    Pending,
    ApprovedForMint,
    Minted,
    Rejected,
}

#[derive(Accounts)]
pub struct Initialize<'info> {
    #[account(mut)]
    pub authority: Signer<'info>,
    #[account(
        init,
        payer = authority,
        space = 8 + 32 + 8 + 8,
        seeds = [b"state"],
        bump
    )]
    pub state: Account<'info, SystemState>,
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct SubmitClaim<'info> {
    #[account(mut)]
    pub authority: Signer<'info>,
    #[account(
        init,
        payer = authority,
        space = 8 + 32 + 4 + 100 + 4 + 400 + 8 + 1 + 1,
        seeds = [b"claim", authority.key().as_ref()],
        bump
    )]
    pub claim: Account<'info, Claim>,
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct ApproveClaim<'info> {
    #[account(mut)]
    pub authority: Signer<'info>,
    #[account(
        mut,
        seeds = [b"state"],
        bump
    )]
    pub state: Account<'info, SystemState>,
    #[account(
        mut,
        seeds = [b"claim", claim.authority.as_ref()],
        bump = claim.bump
    )]
    pub claim: Account<'info, Claim>,
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct MintTokens<'info> {
    #[account(mut)]
    pub authority: Signer<'info>,
    #[account(
        mut,
        seeds = [b"state"],
        bump
    )]
    pub state: Account<'info, SystemState>,
    pub system_program: Program<'info, System>,
}

#[error_code]
pub enum ErrorCode {
    Unauthorized,
    InvalidStatus,
    InsufficientWork,
}
RUST
  
  # Generate Cargo.toml
  cat > "$ACRE_DIR/programs/acre/Cargo.toml" << 'CARGO'
[package]
name = "acre"
version = "0.1.0"
edition = "2021"

[lib]
crate-type = ["cdylib", "lib"]

[dependencies]
anchor-lang = "0.29.0"
CARGO
  
  cat > "$ACRE_DIR/Cargo.toml" << 'CARGO'
[workspace]
members = ["programs/*"]

[resolver]
version = "2"
CARGO
  
  echo "✅ Scaffold created at $ACRE_DIR"
fi

# Check for anchor CLI
if ! command -v anchor &>/dev/null; then
  echo "❌ anchor CLI not found"
  echo "Install: cargo install --git https://github.com/coral-xyz/anchor anchor-cli --locked"
  echo ""
  echo "Or use Solang (lighter, no Rust needed):"
  echo "  cargo install solang-cli"
  exit 1
fi

# Build
cd "$ACRE_DIR"
echo "🔨 Building ACRE program..."
anchor build

# Get program ID
PROG_ID=$(solana address -k target/deploy/acre-keypair.json 2>/dev/null || echo "")
if [ -z "$PROG_ID" ]; then
  echo "⚠️  No deploy keypair found. Generating..."
  mkdir -p target/deploy
  solana-keygen new -o target/deploy/acre-keypair.json --no-bip39-passphrase
  PROG_ID=$(solana address -k target/deploy/acre-keypair.json)
  echo "Program ID: $PROG_ID"
  echo "⚠️  Update declare_id! in src/lib.rs with: $PROG_ID"
  echo "⚠️  Then rebuild: anchor build"
  exit 0
fi

echo "Program ID: $PROG_ID"

# Deploy
echo "🚀 Deploying to devnet..."
anchor deploy --provider.cluster devnet

echo ""
echo "═══ DEPLOY COMPLETE ═══"
echo "Program ID: $PROG_ID"
echo "Network: devnet"
echo "Explorer: https://explorer.solana.com/address/$PROG_ID?cluster=devnet"
echo ""
echo "Update declare_id!(\"$PROG_ID\") in lib.rs and rebuild for final version."
