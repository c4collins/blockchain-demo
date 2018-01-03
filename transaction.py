import json
class Transaction:
    def __init__(self, sender, recipient, amount):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount

    def json(self):
        return {
            'sender': self.sender,
            'recipient': self.recipient,
            'amount': self.amount
        }
    def __str__(self):
        return json.dumps(self.json()).encode()
