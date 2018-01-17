# Standard Library

# Third-Party
from flask import Flask, jsonify, request, render_template, send_from_directory
# Helpers
# Project
from components.block import Block
from components.chain import Chain
from components.address import Address

app = Flask(__name__)
main_address = Address()
node_id = main_address.address
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


@app.route('/transactions/new', methods=['GET', 'POST'])
def new_transaction():
    if request.method == "POST":
        try:
            values = request.get_json(force=True) # API
        except:
            values = {
                'sender': request.form['from'],
                'recipient': request.form['to'],
                'amount': request.form['amount']
            } # Website Form

        required_fields = ['sender', 'recipient', 'amount']

        if not all(k in values for k in required_fields):
            return 'Missing values', 400

        # TODO: Verify addresses
        # TODO: Verify sender has enough balance
        # TODO: Add transaction fees?
        # TODO: Verify amount is possible (not enough info yet)

        block_index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])
        response = {'message': 'Transaction will be added to Block {}'.format(block_index)}
        return jsonify(response), 200

    else:
        return render_template('form/new_transaction.html')


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
        'message': '{} New nodes have been added'.format(
            len(list(blockchain.nodes)) - start_node_count
        ),
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


@app.route('/')
def index():
    return render_template('page/home.html')


# STATIC FILES START ##
@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('staticfiles/styles', path)


@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('staticfiles/scripts', path)


@app.route('/images/<path:path>')
def send_images(path):
    return send_from_directory('staticfiles/images', path)
# END STATIC FILES ##

# CONTEXT PROCESSORS START ##
@app.context_processor
def inject_globals():
    return dict(
        coin_name = "KhanCoin",
    )
# END CONTEXT PROCESSORS ##

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
