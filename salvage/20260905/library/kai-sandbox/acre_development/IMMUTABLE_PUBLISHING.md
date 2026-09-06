# ACRE Immutable Publishing System

## Overview
Publish ACRE content to multiple immutable, uncensorable platforms simultaneously:
- **IPFS** - InterPlanetary File System (decentralized storage)
- **Arweave** - Permanent on-chain storage
- **Ethereum** - Blockchain timestamping
- **Filecoin** - Decentralized storage marketplace

## Publishing Workflow

### 1. Prepare Content
```bash
cd ~/acre_development
# Create your content file (JSON, text, etc.)
echo '{"acre_version": "1.0", "content": "Your immutable content"}' > content.json
```

### 2. Install Dependencies
```bash
# IPFS
pkg install ipfs
ipfs init
ipfs daemon &

# Arweave (Node.js)
npm install -g arweave-cli

# Ethereum
pip install web3

# Filecoin (optional)
# pkg install lotus
```

### 3. Run Publisher
```bash
python3 publish_system.py content.json
```

### 4. Verify Publication
The script will output:
- IPFS CID and URLs
- Arweave transaction ID and URLs
- Ethereum transaction hash
- Filecoin CID (if available)
- Manifest file with all references

## Platform Details

### IPFS (InterPlanetary File System)
- **Type**: Decentralized storage network
- **Immutability**: Content-addressed (hash-based)
- **Access**: Multiple public gateways
- **URL Format**: `https://ipfs.io/ipfs/{CID}`

### Arweave
- **Type**: Permanent on-chain storage
- **Immutability**: Blockchain-based permanence
- **Access**: Arweave gateways and explorers
- **URL Format**: `https://arweave.net/{TXID}`

### Ethereum
- **Type**: Blockchain transaction
- **Immutability**: Cryptographic proof in blockchain
- **Access**: Block explorers (Etherscan, etc.)
- **URL Format**: `https://etherscan.io/tx/{TXID}`

### Filecoin
- **Type**: Decentralized storage marketplace
- **Immutability**: Content-addressed with economic incentives
- **Access**: Filecoin gateways and explorers
- **URL Format**: `https://filfox.io/ipfs/{CID}`

## Manifest Structure

The system creates a comprehensive manifest with:
```json
{
  "content_hash": "sha256:...",
  "content_size": 1234,
  "timestamp": "2024-01-01T00:00:00Z",
  "sources": {
    "ipfs": {
      "cid": "Qm...",
      "url": "https://ipfs.io/ipfs/Qm...",
      "gateway": "https://cloudflare-ipfs.com/ipfs/Qm..."
    },
    "arweave": {
      "txid": "abc123...",
      "url": "https://arweave.net/abc123...",
      "viewblock": "https://viewblock.io/arweave/tx/abc123..."
    },
    "ethereum": {
      "txid": "0x123...",
      "url": "https://etherscan.io/tx/0x123...",
      "explorer": "https://blockchain.com/eth/tx/0x123..."
    }
  },
  "metadata": {
    "type": "ACRE Publication",
    "version": "1.0",
    "immutable": true
  }
}
```

## Verification Process

### Verify IPFS Content
```bash
ipfs cat {CID}
# or
curl https://ipfs.io/ipfs/{CID}
```

### Verify Arweave Content
```bash
arweave tx {TXID}
# or visit
https://arweave.net/{TXID}
```

### Verify Ethereum Transaction
```bash
# Check transaction on Etherscan
https://etherscan.io/tx/{TXID}
```

## Best Practices

1. **Always verify** published content across multiple platforms
2. **Store manifest securely** - it contains all references
3. **Use multiple gateways** for IPFS content access
4. **Monitor transaction confirmations** for blockchain publications
5. **Backup manifest** in multiple locations

## Troubleshooting

### IPFS Issues
- Ensure IPFS daemon is running: `ipfs daemon`
- Check connectivity: `ipfs swarm peers`
- Use public gateways if local node has issues

### Arweave Issues
- Check wallet balance: `arweave wallet get_balance`
- Verify node connection: `arweave net info`
- Use Arweave web interface as backup

### Ethereum Issues
- Check gas prices and adjust accordingly
- Verify network connection to Ethereum node
- Use testnet for development (Rinkeby, Goerli)

## Security Considerations

1. **Private Keys**: Never commit private keys to version control
2. **Content Validation**: Always verify published content matches original
3. **Network Security**: Use VPNs when publishing sensitive content
4. **Backup**: Maintain local backups of all published content

## Next Steps

1. ✅ Set up publishing environment
2. ✅ Prepare ACRE content for publication
3. ✅ Run multi-platform publisher
4. ✅ Verify publications on all platforms
5. ✅ Integrate with ACRE governance system
