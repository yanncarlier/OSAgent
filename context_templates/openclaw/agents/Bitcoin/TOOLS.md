# TOOLS.md - Bitcoin Expert Tools & Resources

Skills define *how* tools work. This file is for *Bitcoin-specific* tools, APIs, explorers, and resources.

## Blockchain Explorers

### Mainnet
- **mempool.space** — Best for fee estimation, Lightning, privacy analysis
- **blockchain.com** — Classic, good for beginners
- **blockstream.info** — Blockstream's explorer, privacy-focused
- **btc.com** — Mining pool explorer, good for mining stats

### Testnet
- **blockstream.info/testnet** — Testnet explorer
- **mempool.space/testnet** — Testnet version

## Node Management

### Software
- **Bitcoin Core** — Reference implementation
- **btcpayserver** — Merchant-focused stack
- **umbrel** — Home node OS
- **myNode** — Another home node solution

### Monitoring
- **Ride The Lightning** — Lightning node management
- **ThunderHub** — Lightning node UI
- **BTC RPC Explorer** — Self-hosted block explorer

## Wallets

### Hardware (Cold Storage)
- **Ledger** — Popular, multi-coin
- **Trezor** — Open-source, Bitcoin-focused
- **Coldcard** — Air-gapped, Bitcoin-only
- **BitBox02** — Swiss, open-source

### Software (Hot Wallets)
- **Sparrow** — Desktop, privacy-focused
- **Electrum** — Classic, feature-rich
- **BlueWallet** — Mobile, Lightning support
- **Phoenix** — Mobile Lightning wallet

### Custodial (Beginners/Convenience)
- **Coinbase** — Exchange wallet
- **Cash App** — Simple buying/spending
- **Strike** — Lightning-focused

## Lightning Network

### Nodes
- **LND** — Lightning Labs implementation
- **c-lightning** — Blockstream implementation
- **Eclair** — ACINQ implementation

### Services
- **Lightning Network+** — Channel management
- **lnmarkets** — Trading on Lightning
- **Breez** — Non-custodial mobile wallet

## APIs & Data Sources

### Market Data
- **CoinGecko API** — Prices, market caps
- **CoinMetrics API** — On-chain metrics
- **Glassnode API** — Advanced analytics
- **TradingView** — Charts, technical analysis

### Blockchain Data
- **Blockchain.com API** — Basic blockchain data
- **Blockcypher API** — Webhooks, TX broadcasting
- **Mempool.space API** — Fee estimation, mempool

## Development Tools

### Libraries
- **bitcoinjs-lib** — JavaScript Bitcoin library
- **python-bitcoinlib** — Python Bitcoin library
- **BDK** — Bitcoin Dev Kit (wallets)

### Testing
- **regtest** — Local Bitcoin network
- **bitcoin-inquisitor** — Transaction debugging
- **LibWally** — Cryptography library

## Security Tools

### Address Validation
- **iancoleman.io/bip39** — Offline seed generation
- **bitaddress.org** — Paper wallet generation
- **WalletScrutiny** — Wallet verification

### Transaction Analysis
- **OXT.me** — Blockchain analysis
- **WalletExplorer** — Wallet clustering
- **Blockchair** — Advanced search

## Educational Resources

### Documentation
- **Bitcoin.org** — Official website
- **Bitcoin Wiki** — Technical wiki
- **Learn Me A Bitcoin** — Visual explanations

### Courses
- **Andreas Antonopoulos videos** — YouTube
- **Saylor Academy Bitcoin Course** — Free course
- **Bitcoin Technical Workshops** — Conference talks

## Your Notes

Add your own discoveries here:

### Favorite Commands
```bash
# Bitcoin Core RPC examples
bitcoin-cli getblockchaininfo
bitcoin-cli estimaterawfee
bitcoin-cli getmempoolinfo
```

### Script Snippits
```python
# Add your own Bitcoin Python scripts here
```

### Common Analyses
- Mempool congestion patterns
- Fee rate strategies
- UTXO management tips

---

*Update this as you discover new Bitcoin tools and resources. The ecosystem evolves rapidly.*