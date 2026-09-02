#!/bin/bash
set -e; source ~/.openroot-secrets
A=~/openroot/archive; S=$A/genesis-state.env; touch $S; source $S
cd ~/openroot

# 1) BUNDLE + HASH (the canonical object)
if [ -z "$HASH" ]; then
  tar -czf $A/openroot-genesis.tar.gz -C ~/openroot archive/conversation.md BRIDGE.md docs/PHILOSOPHY.md docs/FINANCE-PLAN.md 2>/dev/null || tar -czf $A/openroot-genesis.tar.gz -C ~/openroot archive/conversation.md BRIDGE.md
  HASH=$(sha256sum $A/openroot-genesis.tar.gz | cut -d' ' -f1)
  echo "HASH=$HASH" >> $S; fi
echo "sha256: $HASH"

# 2) IPFS via Pinata (returns CID = permanent address)
if [ -z "$CID" ] && [ "$PINATA_JWT" != "PASTE_HERE" ]; then
  CID=$(curl -s -X POST https://api.pinata.cloud/pinning/pinFileToIPFS \
    -H "Authorization: Bearer $PINATA_JWT" \
    -F "file=@$A/openroot-genesis.tar.gz" | jq -r .IpfsHash)
  [ "$CID" != "null" ] && echo "CID=$CID" >> $S || { echo "Pinata failed"; CID=""; }; fi
echo "ipfs://${CID:-pending}"

# 3) ZENODO DOI (permanent — confirm gate)
if [ -z "$DOI" ] && [ "$ZENODO_TOKEN" != "PASTE_HERE" ] && [ -n "$CID" ]; then
  read -r -p "Publish PERMANENTLY to Zenodo? (y/N) " ok
  if [ "$ok" = "y" ]; then
    D=$(curl -s -X POST "https://zenodo.org/api/deposit/depositions" -H "Authorization: Bearer $ZENODO_TOKEN" -H "Content-Type: application/json" -d '{}')
    ID=$(echo "$D"|jq -r .id); BUCKET=$(echo "$D"|jq -r .links.bucket)
    curl -s -H "Authorization: Bearer $ZENODO_TOKEN" --upload-file $A/openroot-genesis.tar.gz "$BUCKET/openroot-genesis.tar.gz" > /dev/null
    META=$(jq -n --arg d "OpenRoot Genesis Archive: founding conversation + doctrine. sha256:$HASH ipfs://$CID github.com/jesseray718" \
      '{metadata:{title:"OpenRoot Genesis Archive v1",upload_type:"other",description:$d,creators:[{name:"Ray, Jesse"}],license:"cc-by-sa-4.0",keywords:["appropriate-technology","open-source-hardware","permaculture"],related_identifiers:[{relation:"isSupplementTo",identifier:"10.5281/zenodo.20639511"}]}}')
    curl -s -X PUT "https://zenodo.org/api/deposit/depositions/$ID" -H "Authorization: Bearer $ZENODO_TOKEN" -H "Content-Type: application/json" -d "$META" > /dev/null
    DOI=$(curl -s -X POST "https://zenodo.org/api/deposit/depositions/$ID/actions/publish" -H "Authorization: Bearer $ZENODO_TOKEN" | jq -r .doi)
    echo "DOI=$DOI" >> $S; fi; fi
echo "doi:${DOI:-pending}"

# 4) SOLANA MEMO (immutable fingerprint, mainnet, ~\$0.001 fee)
if [ -z "$TX" ] && [ -n "$CID" ]; then
  [ -d ~/openroot/solmemo ] || { mkdir -p ~/openroot/solmemo; cd ~/openroot/solmemo; npm init -y >/dev/null; npm i @solana/web3.js@1 >/dev/null 2>&1; cd ~/openroot; }
  cat > ~/openroot/solmemo/memo.js << 'JS'
const {Connection,Keypair,Transaction,TransactionInstruction,PublicKey,sendAndConfirmTransaction}=require('@solana/web3.js');
const fs=require('fs'),os=require('os');const kp=os.homedir()+'/.openroot-sol.json';
let k;if(fs.existsSync(kp)){k=Keypair.fromSecretKey(Uint8Array.from(JSON.parse(fs.readFileSync(kp))))}else{k=Keypair.generate();fs.writeFileSync(kp,JSON.stringify(Array.from(k.secretKey)),{mode:0o600})}
(async()=>{const c=new Connection(process.env.SOL_RPC||'https://api.mainnet-beta.solana.com','confirmed');
const b=await c.getBalance(k.publicKey);
if(b<50000){console.log('FUND_ME '+k.publicKey.toBase58());process.exit(2)}
const ix=new TransactionInstruction({keys:[],programId:new PublicKey('MemoSq4gqABAXKb96qnH8TysNcWxMyWCqXgDLGmfcHr'),data:Buffer.from(process.argv[2],'utf8')});
console.log('TX_SIG '+await sendAndConfirmTransaction(c,new Transaction().add(ix),[k]))})();
JS
  OUT=$(node ~/openroot/solmemo/memo.js "OpenRoot Genesis|sha256:$HASH|ipfs://$CID|doi:${DOI:-pending}|github.com/jesseray718|CC-BY-SA-4.0" || true)
  case "$OUT" in
    FUND_ME*) echo "Send ~0.001 SOL (a few cents) to: ${OUT#FUND_ME } then re-run";;
    TX_SIG*)  TX=${OUT#TX_SIG }; echo "TX=$TX" >> $S;;
  esac; fi
[ -n "$TX" ] && echo "https://solscan.io/tx/$TX"

# 5) DISTRIBUTE (git = fifth anchor + the share blurb)
if [ -n "$CID" ] && [ -n "$TX" ] && [ -z "$PUSHED" ]; then
  printf '\nGENESIS: sha256:%s · ipfs://%s · doi:%s · sol:%s\n' "$HASH" "$CID" "$DOI" "$TX" >> BRIDGE.md
  cp $S $A/  # state travels with repo
  git add -A && git commit -m "Genesis archive anchored: IPFS+Zenodo+Solana" && git push && echo "PUSHED=1" >> $S
  echo "---- SHARE THIS ----"
  echo "OpenRoot's founding archive is now permanent & verifiable:"
  echo "DOI: https://doi.org/$DOI"
  echo "IPFS: https://gateway.pinata.cloud/ipfs/$CID"
  echo "Proof on Solana: https://solscan.io/tx/$TX"
  echo "Build with us: github.com/jesseray718/openroot"; fi
