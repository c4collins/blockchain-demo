import hashlib
import json
import textwrap
import time
import uuid

from flask import Flask, jsonify, request

from chain import Chain
from block import Block

app = Flask(__name__)
node_id = str(uuid.uuid4()).replace('-', '')
blockchain = Chain()

@app.route('/mine', methods=['GET'])
def mine():
    # 1. Calculate PoW
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    # 2. Reward Miner
    blockchain.new_transaction(
        sender="mining_reward_generator",
        recipient=node_id,
        amount=1
    )

    # 3. Add Block to Chain
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': 'New block forged',
        'index': block.index,
        'transactions': [transaction.json() for transaction in block.transactions],
        'proof': block.proof,
        'previous_hash': block.previous_hash
    }
    return jsonify(response), 200

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json(force=True)
    required_fields = ['sender', 'recipient', 'amount']

    if not all(k in values for k in required_fields):
        return 'Missing values', 400

    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])
    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 200


@app.route('/chain', methods=['GET'])
def full_chain():

    response = {
        'chain': [block.json() if type(block) == Block else block for block in blockchain.chain],
        'length': len(blockchain.chain)
    }
    return jsonify(response), 200


@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json(force=True)
    nodes = values.get('nodes')
    start_node_count = len(list(blockchain.nodes))

    if nodes is None:
        return "Error: please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': f'{len(list(blockchain.nodes)) - start_node_count} New nodes have been added',
        'total_nodes': list(blockchain.nodes)
    }

    return jsonify(response), 201

@app.route('/nodes/resolve', methods=['GET'])
def resolve_conflicts():
    replaced = blockchain.resolve_conflicts()
    if replaced:
        response = {
            'message': 'My chain was replaced',
            'chain': blockchain.chain
        }
    else:
        response = {
            'message': 'My chain is authoritative',
            'chain': blockchain.chain
        }

    return jsonify(response), 200






if __name__ == '__main__':
    app.run('0.0.0.0', port=5000)
