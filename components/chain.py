# Standard Library
import hashlib
import json
import time
import urllib.parse
# Third-Party
import requests
# Project
from components.block import Block
from components.transaction import Transaction


class Chain:
    def __init__(self, address):
        self.chain = []
        self.current_transactions = []
        self.new_block(proof=100, address=address, previous_hash="1")
        self.nodes = set()

    # Components
    def new_block(self, proof, address, previous_hash=None):
        """
        Create a new Block in the Blockchain
        """

        block = Block(
            index=len(self.chain) + 1,
            timestamp=time.time(),
            transactions=self.current_transactions,
            proof=proof,
            previous_hash=previous_hash or self.hash(self.chain[-1]),
            miner_address=address,
        )

        self.current_transactions = []
        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        """
        Creates a new transaction to go into the next mined Block
        """
        transaction = Transaction(
            sender=sender,
            recipient=recipient,
            amount=amount
        )
        self.current_transactions.append(transaction)

        return self.last_block.index + 1

    @property
    def last_block(self):
        return self.chain[-1]

    # Mining
    @staticmethod
    def hash(block):
        """
        Creates a SHA-256 hash of a block
        """

        # We must make sure the object is consistent or the hashes will be inconsistent
        if type(block) == Block:
            block_data = block.json()
        else:
            block_data = block
        block_string = json.dumps(block_data, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, last_proof):
        """
        Simple PoW algorithm:
        - Find a number 'p such that hash(pp') contains rome number of leading 0s, where p is the old p'
        - p is the previous proof, and p' is the new proof
        """

        proof = 0
        while not self.valid_proof(last_proof, proof):
            proof += 1

    @staticmethod
    def valid_proof(last_proof, proof):
        """
        Validates the proof: Does proof(last_proof, proof) contain a number of leading 0s?
        """

        guess = '{}{}'.format(last_proof, proof).encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    # Nodes
    def register_node(self, address):
        """
        Add new node to list of nodes
        """

        parsed_url = urllib.parse.urlparse(address)
        self.nodes.add(parsed_url.path)

    def valid_chain(self, chain, verbose=False):
        """
        Determine if a given blockchain is valid
        """

        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]

            if verbose:
                print('{}'.format(last_block))
                print('{}'.format(block))
                print("\n------------\n")

            # Check that the hash of the last block is correct
            if block.previous_hash != self.hash(last_block):
                return False

            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self):
        """
        This is the Consensus Algorithm -
        it resolves conflicts by replacing our chain with the longest one in the network.
        """

        new_chain = None
        max_length = len(self.chain)  # Only look for a chain longer than your own

        for node in self.nodes:
            response = requests.get(
                'http://{}/chain'.format(node)
            )

            if response.status_code == 200:
                resp_json = response.json()
                length = resp_json['length']
                chain = resp_json['chain']

                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        if new_chain is not None:
            self.chain = new_chain
            return True
        return False
