#Tipsi Jadav - 201801091
#Rahil Shah - 201801252 

import json
from txGenerator import generate_hash
from Transaction import Transaction
import random

class Block:
    def __init__(self, tx: Transaction, ctx: Transaction, prev: str):
        self.tx = tx
        self.CoinTx = ctx
        self.prev = prev
        self.nonce = self.generate_nonce(64)
        self.pow = self.generate_pow()

    @staticmethod
    def generate_nonce(length):
        """Generate pseudorandom number."""
        return ''.join([str(random.randint(0, 9)) for i in range(length)])

    def generate_pow(self):
        return generate_hash([str(self.CoinTx).encode('utf-8'), str(self.tx).encode('utf-8'), self.prev.encode('utf-8'), self.nonce.encode('utf-8')])

    def hash(self):
        return self.pow
    
    def asTx(self):
        return json.dumps({'CoinTx':{'number':self.CoinTx.number, 'output':self.CoinTx.output, 'input':self.CoinTx.input, 'sig':self.CoinTx.sig}, 'tx':{'number':self.tx.number, 'output':self.tx.output, 'input':self.tx.input, 'sig':self.tx.sig}, 'prev':self.prev, 'nonce':self.nonce, 'pow':self.pow})
        # return json.dumps({'tx':{'number':self.tx.number, 'output':self.tx.output, 'input':self.tx.input, 'sig':self.tx.sig}})

    def asBlock(self):
        return json.dumps({'CoinTx':{'number':self.CoinTx.number, 'output':self.CoinTx.output, 'input':self.CoinTx.input, 'sig':self.CoinTx.sig}, 'tx':{'number':self.tx.number, 'output':self.tx.output, 'input':self.tx.input, 'sig':self.tx.sig}, 'prev':self.prev, 'nonce':self.nonce, 'pow':self.pow})
        # return json.dumps({'tx':{'number':self.tx.number, 'output':self.tx.output, 'input':self.tx.input, 'sig':self.tx.sig}})