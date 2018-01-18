# Standard Library
import json
import time

class Transaction:
    def __init__(self, sender, recipient, amount):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.initiation_timestamp = time.time()
        self.resolved_in = None

    def json(self):
        return {
            'sender': self.sender,
            'recipient': self.recipient,
            'amount': self.amount,
            'initiation_timestamp': self.initiation_timestamp,
            'resolved_in': self.resolved_in,
        }

    def __str__(self):
        return json.dumps(self.json()).encode()

    def resolve(self, block_id):
        self.resolved_in = block_id

        return self