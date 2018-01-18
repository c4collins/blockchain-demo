# Standard Library

# Third-Party
from flask import Flask, jsonify, request, render_template, send_from_directory, url_for, redirect
# Helpers
# Project
from components.block import Block
from components.chain import Chain
from components.address import Address

app = Flask(__name__)
main_address = Address()
node_id = main_address.address
print(node_id)
blockchain = Chain(node_id) # TODO: make address configurable instead of always using node_id


@app.route('/mine', methods=['GET', 'POST'])
def mine():
    if request.method == "POST":
        # 1. Calculate PoW
        last_block = blockchain.last_block
        last_proof = last_block.proof
        proof = blockchain.proof_of_work(last_proof)

        # 2. Reward Miner
        blockchain.new_transaction(
            sender="mining_reward_generator",
            recipient=node_id,
            amount=1
        )

        # 3. Add Block to Chain
        previous_hash = blockchain.hash(last_block)
        # TODO: Make the address configurable rather than always the node_id
        block = blockchain.new_block(previous_hash=previous_hash, proof=proof, address=node_id)

        response = {
            'message': 'New block forged',
            'index': block.index,
            'transactions': [transaction.json() for transaction in block.transactions],
            'proof': block.proof,
            'previous_hash': block.previous_hash
        }

        response = __full_chain_data()
        response['message'] = 'New block mined!'
        return render_template('page/full_chain.html', data=response)

    else:
        # show button
        return render_template('page/initiate_mining.html')



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
        # TODO: Verify amount is possible (not enough info yet on possible amounts)

        blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])
        response = __pending_transaction_data()

        response['message'] = "Transaction Added"

        return render_template('page/pending_transactions.html', data=response)

    else:
        return render_template('form/new_transaction.html')

def __pending_transaction_data():
    return {
        'transactions': list(reversed([transaction.json() for transaction in blockchain.current_transactions])),
        'length': len(blockchain.current_transactions)
    }
@app.route('/transactions', methods=['GET'])
def pending_transactions():
    response = __pending_transaction_data()
    return render_template('page/pending_transactions.html', data=response)


def __full_chain_data():
    return {
        'chain': list(reversed([block.json() if type(block) == Block else block for block in blockchain.chain])),
        'length': len(blockchain.chain)
    }
@app.route('/chain', methods=['GET'])
def full_chain():
    response = __full_chain_data()
    return render_template('page/full_chain.html', data=response)


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
    response = {
        'chain': {
            'length': len(blockchain.chain),
            'num_of_transactions': sum([len(block.transactions) for block in blockchain.chain]),
            'last_id': blockchain.last_block.index
        },
        'message': 'My chain was replaced' if replaced else 'My chain is authoritative',
    }
    return render_template('page/conflict_resolution.html', data=response)


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
