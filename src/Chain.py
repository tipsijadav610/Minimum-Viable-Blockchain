#Tipsi Jadav - 201801091
#Rahil Shah - 201801252 

import random
from txGenerator import generate_hash, User, generateTransaction
from Transaction import Transaction
from Block import Block
import copy

class Chain:
    def __init__(self, genesisBlock: Block):
        self.blocks = [genesisBlock]
        self.unspentCoin2BlockIdx = {}
        for output in genesisBlock.tx.output+genesisBlock.CoinTx.output:
            key = generate_hash([genesisBlock.tx.number.encode("utf-8"), output['pubkey'].encode("utf-8")])
            self.unspentCoin2BlockIdx[key] = 0

        names = ['miner_1', 'miner_2', 'miner_3', 'miner_4']
        self.block_reward = 25
        self.miner_node = []
        self.coin_base = User('coin_base')

        # make miner objects from list of names and append to list of miners
        for n in names:
            self.miner_node.append(User(n))

    def addTx(self, tx: Transaction):
        lastBlockHash = self.blocks[len(self.blocks) - 1].hash()
        CoinTx = self.coinBaseTx()
        newBlock = Block(tx, CoinTx, lastBlockHash)
        self.unspentCoin2BlockIdx = Chain.validateBlock(self.blocks, newBlock, self.unspentCoin2BlockIdx)
        self.blocks.append(newBlock)
        return True

    def coinBaseTx(self):
        miner = random.choice(self.miner_node)
        Tx = generateTransaction([self.coin_base], [self.blocks[0].tx.number], [miner], [0], [self.block_reward], False)
        tx = dict()
        tx['input'], tx['number'], tx['output'], tx['sig'], tx['lockTime'] = Tx.input, Tx.number, Tx.output, Tx.sig, Tx.lockTime
        tx = Transaction(tx)
        return tx

    def validateBlock(blocks, newBlock: Block, unspentCoin2BlockIdx):
        assert len(blocks) > 0
        newUnspentCoin2BlockIdx = copy.deepcopy(unspentCoin2BlockIdx)
        newTx = newBlock.tx

        senderPk  = newTx.input[0]['output']['pubkey']
        for nextTxInput in newTx.input:
            newTxInputNum  = nextTxInput['number']
            key = generate_hash([newTxInputNum.encode('utf-8'),senderPk.encode('utf-8')])

            # i am claiming to use this coin
            if(key not in unspentCoin2BlockIdx):
                raise Exception("Either a double spend or new block is spending money that was never made")
            claimedBlockIndex = unspentCoin2BlockIdx[key]
            claimedBlock = blocks[claimedBlockIndex]
            # the output they recieved is equal to what they want to spend
            claimedTxOuputs = claimedBlock.tx.output
            foundOutput = False
            for output in claimedTxOuputs:
                print()
                if(output['pubkey'] == nextTxInput['output']['pubkey'] and output['value'] == nextTxInput['output']['value']):
                    foundOutput = True
            if(not foundOutput):
                raise Exception("user " + nextTxInput['pubkey'] + " does not have money they are claiming")
            # remove the spend coin from this tx
            del newUnspentCoin2BlockIdx[key]
        # and we add back all the coins in this tx output
        for output in newBlock.tx.output:

            recieverKey= output['pubkey']
            newKey = generate_hash([newTx.number.encode("utf-8"), recieverKey.encode("utf-8")])

            newUnspentCoin2BlockIdx[newKey] = len(blocks)

        for output in newBlock.CoinTx.output:

            recieverKey= output['pubkey']
            newKey = generate_hash([newBlock.CoinTx.number.encode("utf-8"), recieverKey.encode("utf-8")])

            newUnspentCoin2BlockIdx[newKey] = len(blocks)

        return newUnspentCoin2BlockIdx

    def validateChain(blocks, genesisBlock):
        try:
            if (blocks[0].hash() != genesisBlock.hash()):
                return False
            # we have the same genesis
            builtBlocks = [genesisBlock]
            unspentCoin2BlockIdx = {}
            for block in blocks[1:]:
                if block.pow < 0x07FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF:
                    unspentCoin2BlockIdx = Chain.validateBlock(builtBlocks, block, unspentCoin2BlockIdx)
                    if(not unspentCoin2BlockIdx):
                        raise Exception("Incoming chain was found to have invalid block")
                    else:
                        builtBlocks.append(block)
            return True
        except:
            return False

    def asString(self, asTx = False):
        res = "[\n"
        for i, block in enumerate(self.blocks):
            if(asTx):
                res+=block.asTx()
            else:
                res+=block.asBlock()
            res+=',\n'
            
        return res[:-2] + "\n]\n"