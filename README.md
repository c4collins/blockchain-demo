# Blockchain Demo

## Run
```
python3 blockchain.py
```

## Details
### block.py
Describes the Block object.
### transaction.py
Describes the Transaction object.
### chain.py
Defines the composition of the Chain object, including all functions that manipulate the chain in any way (adding transactions to be included in the next block, hashing, PoW, verifying chains and blocks, and determining the longest valid chain)
### blockchain.py
Is a JSON API server capable of mining new blocks, showing the current state of the blockchain, and registering nodes.  Some of these functions overlap with the Chain object: this is the interface, but the Chain is the action-taker.