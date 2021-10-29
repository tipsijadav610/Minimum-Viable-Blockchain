#Tipsi Jadav - 201801091
#Rahil Shah - 201801252 

from nacl.signing import VerifyKey
from nacl.encoding import HexEncoder
from txGenerator import generate_hash, generateSignature
import json
import numpy as np

class Transaction:
    def __init__(self, tx):
        # print("creating tx from " + str(tx))
        self.input = tx['input']
        self.number = tx['number']
        self.output = tx['output']
        self.sig = tx['sig']
        self.lockTime = tx['lockTime']
        self.validate()

    def netTx(self):
        net = {}
        for i in self.input:
            output = i['output']
            senderPk = output['pubkey']
            sendAmount = output['value']
            if senderPk not in net:
                net[senderPk] = 0
            net[senderPk] -= sendAmount
        for o in self.output:
            receiverPk = o['pubkey']
            receiveAmount = o['value']
            if receiverPk not in net:
                net[receiverPk] = 0
            net[receiverPk] += receiveAmount
        return net

    def validate(self):
        # if not valid, throw error
        if len(self.input) == 0:
            raise Exception
        elif len(self.output) == 0:
            raise Exception
        elif not self.sig:
            raise Exception
        elif not self.number:
            raise Exception
        hexHash = generate_hash(
            [json.dumps(self.input).encode('utf-8'), json.dumps(self.output).encode('utf-8'), self.sig.encode('utf-8')])
        if self.number != hexHash:
            raise Exception
        totalInOut = 0
        res = self.netTx()
        for val in res.values():
            totalInOut += val
        if len(res.values())==2 and np.array_equal(np.array(list(res.values())).sort(), np.array([-25, 0]).sort()):
            pass
        elif totalInOut != 0:
            raise Exception
        vk = VerifyKey(self.input[0]['output']['pubkey'], encoder=HexEncoder)
        try:
            vk.verify(self.sig, encoder=HexEncoder)
        except:
            print("\n\n\n\nWrong Signature\n\n\n\n")
            raise Exception
