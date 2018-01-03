import time
import json
import hashlib
import urllib.parse

import requests

from block import Block
from transaction import Transaction

class Chain:
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.new_block(previous_hash="1", proof=100)
        self.nodes = set()

    # Components
    def new_block(self, proof, previous_hash=None):
        """
        Create a new Block in the Blockchain
        :param proof: The proof given by the PoW algorithm
        :type proof: int
        :param previous_hash: Hash of previous Block (optional)
        :type previous_hash: str
        :return: New Block
        :rtype: Block
        """

        block = Block(
            index = len(self.chain) + 1,
            timestamp = time.time(),
            transactions = self.current_transactions,
            proof = proof,
            previous_hash = previous_hash or self.hash(self.chain[-1]),
        )

        self.current_transactions = []
        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        """
        Creates a new transaction to go into the next mined Block
        :param sender: Address of the sender
        :type sender: str
        :param recipient: Address of the recipient
        :type recipient: str
        :param amount: Amount to transfer from sender to recipient
        :type amount: int
        :return: The index of the block that will hold this transaction
        :rtype: int
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
        :param block: Block
        :type block: Block
        :return: Hash of Block
        :rtype: str
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

        :param last_proof: Last block's proof
        :type last_proof: int
        :return: new Proof
        :rtype: int
        """

        proof = 0
        while not self.valid_proof(last_proof, proof):
            proof += 1

    @staticmethod
    def valid_proof(last_proof, proof):
        """
        Validates the proof: Does proof(last_proof, proof) contain a number of leading 0s?
        :param last_proof: Previous Proof
        :type last_proof: int
        :param proof: Current Proof
        :type proof: int
        :return: True if valid, False if invalid
        :rtype: bool
        """

        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "00000"

    # Nodes
    def register_node(self, address):
        """
        Add new node to list of nodes
        :param address: Address of node e.g. "http://192.168.0.1:5000"
        :type address: str
        :return: None
        :rtype: None
        """

        parsed_url = urllib.parse.urlparse(address)
        self.nodes.add(parsed_url.path)


    def valid_chain(self, chain, verbose=False):
        """
        Determine if a given blockchain is valid
        :param chain: Chain.chain
        :type chain: list
        :return:  True if valid, else False
        :rtype: bool
        """

        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]

            if verbose:
                print(f'{last_block}')
                print(f'{block}')
                print("\n------------\n")

            # Check that the hash of the last block is correct
            if block['previous_hash'] != self.hash(last_block):
                return False

            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self):
        """
        This is the Consensus Algorithm - it resolves conflicts by replacing our chain with the longest one in the network.
        :return: True if chain was replaced, else False
        :rtype: bool
        """

        new_chain = None
        max_length = len(self.chain) # Only look for a chain longer than your own

        for node in self.nodes:
            response = requests.get(f'http://{node}/chain')

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