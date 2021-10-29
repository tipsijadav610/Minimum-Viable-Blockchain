# Minimum Viable Blockchain

A simplified version of the technology underlying Bitcoin. You have nodes which validate transactions, perform proofs of work, and communicate in order to process transactions. This emulates the mining and transaction verification process of Bitcoin.

The MVB implements the following:
- Authentic transactions that are resistant to theft
- Open competition amongst nodes to validate transactions
- Detection of double spending
- Use of proof-of-work to raise the cost of running attacks against the network
- Detection of and reaction to forks in the chain
- Coinbase transaction to miners
- Locked time on transaction
- One malicious user who changes ECDSA signature
