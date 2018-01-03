import json
class Block:
    def __init__(self, index, timestamp, transactions, proof, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.transactions = transactions or []
        self.proof = proof
        self.previous_hash = previous_hash

    def json(self):
        return {
            'index': self.index,
            'timestamp': self.timestamp,
            'proof': self.proof,
            'previous_hash': self.previous_hash,
            'transactions': [transaction.json() for transaction in self.transactions],
        }
    def __str__(self):
        return json.dumps(self.json()).encode()