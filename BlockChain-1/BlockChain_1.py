import time, json, numpy as np, flask
from hashlib import sha256
from uuid import uuid4
from textwrap import dedent

class BlockChain(object):
    def __init__(self):
        self.chain=[]
        self.current_transaction=[]
        #genesis block
        self.new_block(previous_hash=1, proof=100)

    def new_block(self, proof, previous_hash):
        block={
            'index': len(self.chain)+1,
            'timestamp': time.time(),
            'transactions': self.current_transaction,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1])
            }
        self.current_transaction=[]
        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        self.current_transaction.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount
            })
        return self.last_block['index']+1

    def proof_of_work(self, last_proof):
        proof=0
        while self.valid_proof(last_proof,proof) is False:
            proof+=1
        return proof

    @staticmethod
    def hash(block):
        block_string=json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @staticmethod
    def valid_proof(last_proof, proof):
        guess=f'{last_proof}{proof}'.encode()
        guess_hash=hashlib.sha256(guess).hexdigest()
        return guess_hash[:4]=='0000'

    @property
    def last_block(self):
        return self.chain[-1]

app=flask.Flask(__name__)
node_identifier=str(uuid4()).replace('-','')
blockchain=BlockChain()

@app.route('/mine',methods=['GET'])
def mine():
    blockchain.new_transaction(sender='0',recipient=node_identifier,amount=1)
    previous_hash=blockchain.hash(blockchain.last_block)
    block=blockchain.new_block(blockchain.proof_of_work(blockchain.last_block['proof']), previous_hash)
    response={
        'message': 'new block forged',
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash']
        }
    return flask.jsonify(response), 200

@app.route('/transactions/new',methods=['POST'])
def new_transaction():
    values = flask.request.get_json()
    required=['sender','recipient','amount']
    if not all (k in values for k in required):
        return 'missing values', 400
    index=blockchain.new_transaction(values['sender'],values['recipient'],values['amount'])
    response={'message': f'transaction will be aded to blockchain {index}'}
    return flask.jsonify(response), 201

@app.route('/chain',methods=['GET'])
def full_chain():
    response={
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
        }
    return flask.jsonify(response), 200

if __name__=='__main__':
    app.run(host='0.0.0.0', port=5000)