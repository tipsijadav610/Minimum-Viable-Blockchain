#Tipsi Jadav - 201801091
#Rahil Shah - 201801252 

from Block import Block
import threading
import time
import json
import sys
import random
import string
import txGenerator
from nacl.signing import VerifyKey
from nacl.encoding import HexEncoder
from txGenerator import generate_hash, generateSignature, User
import threading
from Chain import Chain
from Transaction import Transaction
import queue
import copy
import time
import random
class HonestNode(threading.Thread):
    def __init__(self, name, genesisBlock):
        threading.Thread.__init__(self)
        self.name = name
        # Each Node has a Queue to track incoming chains from others
        self.q = queue.Queue()
        # we use these two to determine which unverified transaction we should look at next...
        self.invalidTx = set()
        self.unverifiableTx = set()
        self.txInChain = set()
        # each node holds their own chain
        self.chain = Chain(genesisBlock)

    def run(self):
        # target function of the thread class
        try:
            print(self.name + " running...")
            while True:
                # process all new chains in queue
                while not self.q.empty():
                    self.receiveChain()
                # process any new unverified transactions
                self.processUnverifiedTx()
                global stop_threads
                if stop_threads:
                    break
        finally:
            print(self.name + " stopped")

    # gets a new unverified transaction not already in out chain
    def processUnverifiedTx(self):
        global unverifiedTxs
        # loop over all unverified Tx
        for (unverifiedTxNum, unverifiedTx) in list(unverifiedTxs.items()):
            # until we find possible valid Tx that we do not already have in our chain
            if unverifiedTxNum not in self.txInChain and unverifiedTxNum not in self.invalidTx and unverifiedTxNum not in self.unverifiableTx:
                try:
                    tx = Transaction(unverifiedTx)
                    print(unverifiedTxNum + " is well formatted")
                except:
                    # this was an invalidTX, mark it as such
                    self.invalidTx.add(unverifiedTxNum)
                    print(unverifiedTxNum + " is not well formatted")
                    # lets see if we got new chains from our neighbors
                    break
                if tx.lockTime>len(self.chain.blocks):
                    continue
                try:
                    self.chain.addTx(tx)
                    self.txInChain.add(tx.number)
                    self.unverifiableTx = set()
                    self.broadcastChain()
                except:
                    print(unverifiedTxNum + " is unverifiable")
                    self.unverifiableTx.add(unverifiedTxNum)
                    break

    def sendChain(self, chain):
        self.q.put(chain)

    def receiveChain(self):
        newChain = self.q.get()
        if len(newChain.blocks) >= len(self.chain.blocks):
            if Chain.validateChain(newChain, self.chain.blocks[0]):
                self.unverifiableTx = {}
                self.txInChain = {}
                self.chain = copy.deepcopy(newChain)
                for block in self.chain.blocks:
                    self.txInChain.add(block.tx.number)
                return True
        return False

    def broadcastChain(self):
        print(self.name + " broadcasting chain ")
        global nodes
        for nodeKey, node in nodes.items():
            if nodeKey != self.name:
                node.sendChain(self.chain)
    
    def print(self):
        with open('output/'+self.name+".json", 'w') as outfile:
            outfile.write(self.chain.asString(asTx=True))
            outfile.close()

    def printBlockChain(self):
        with open('output/'+self.name+"'s_chain"+".json", 'w') as outfile:
            outfile.write(self.chain.asString())
            outfile.close()
class MaliciousNode(threading.Thread):
    def __init__(self, name, genesisBlock):
        threading.Thread.__init__(self)
        self.name = name
        # Each Node has a Queue to track incoming chains from others
        self.q = queue.Queue()
        # each node holds their own chain
        self.chain = Chain(genesisBlock)
        self.badBlocks = [RandomBlock, MissingNonceBlock, MissingPowBlock, MissingPrevBlock, MissingTxBlock, MissingCoinTxBlock]

    def run(self):
        # target function of the thread class
        global stop_threads
        global stop_malicious
        try:
            print(self.name + " running...")
            while True:
                # process all new chains in queue
                time.sleep(1)
                if stop_threads or stop_malicious:
                    break
                while not self.q.empty():
                    if stop_threads:
                        break
                    self.receiveChain()
                # process any new unverified transactions
        finally:
            print(self.name + " stopped")

    def malleability_attack(self):
        Txnum = random.choice(list(unverifiedTxs.keys()))
        tx = unverifiedTxs[Txnum]
        s=string.ascii_letters+string.digits
        user = User(''.join(random.sample(s,8)))
        signature = generateSignature(json.dumps(tx['input']), json.dumps(tx['output']), user)
        concatSig = signature.signature + signature.message
        tx['input'][0]['output']['pubkey'] = str(user.vk)
        number = generate_hash([json.dumps(tx['input']).encode('utf-8'), json.dumps(tx['output']).encode('utf-8'), concatSig])
        tx['number'] = number
        tx['sig'] = concatSig.decode('utf-8')
        unverifiedTxs[number] = tx
        print(Txnum + " has been changed to " + number)

    def sendChain(self, chain):
        self.q.put(chain)

    def receiveChain(self):
        newChain = self.q.get()
        if len(newChain.blocks) >= len(self.chain.blocks):
            newChain = copy.deepcopy(newChain)
            blocks  = newChain.blocks
            numBlocksToAdd = 3
            for i in range(numBlocksToAdd):
                badBlockClass = random.choice(self.badBlocks)
                blocks.append(badBlockClass())
            self.broadcastChain(newChain)
            number = random.randint(0, 19)
            if number==0:
                self.malleability_attack()

    def broadcastChain(self,chain):
        print(self.name + " broadcasting chain ")
        global nodes
        for nodeKey, node in nodes.items():
            if nodeKey != self.name:
                node.sendChain(chain)

def generate_nonce(length):
    """Generate pseudorandom number."""
    return ''.join([str(random.randint(0, 9)) for i in range(length)])

class RandomBlock():
    def __init__(self):
        self.tx = generate_nonce(64)
        self.CoinTx = generate_nonce(64)
        self.prev = generate_nonce(64)
        self.nonce = generate_nonce(64)
        self.pow = generate_nonce(128)

class MissingTxBlock():
    def __init__(self):
        self.CoinTx = generate_nonce(64)
        self.prev = generate_nonce(64)
        self.nonce = generate_nonce(64)
        self.pow = generate_nonce(128)

class MissingCoinTxBlock():
    def __init__(self):
        self.tx = generate_nonce(64)
        self.prev = generate_nonce(64)
        self.nonce = generate_nonce(64)
        self.pow = generate_nonce(128)

class MissingPrevBlock():
    def __init__(self):
        self.tx = generate_nonce(64)
        self.CoinTx = generate_nonce(64)
        self.nonce = generate_nonce(64)
        self.pow = generate_nonce(128)

class MissingNonceBlock():
    def __init__(self):
        self.tx = generate_nonce(64)
        self.CoinTx = generate_nonce(64)
        self.prev = generate_nonce(64)
        self.pow = generate_nonce(128)

class MissingPowBlock():
    def __init__(self):
        self.tx = generate_nonce(64)
        self.CoinTx = generate_nonce(64)
        self.prev = generate_nonce(64)
        self.nonce = generate_nonce(64)

# these variables are globally accessible to all nodes
stop_threads = False
stop_malicious = False
nodes = {}
unverifiedTxs = {}
STOP_LENGTH_CHAIN = 16

def driver(txs, numHonestNodes, numMaliciousNodes, genesisBlock):
    honest_nodes = startNodes(numHonestNodes, numMaliciousNodes, genesisBlock)
    # add transactions, which causes nodes to process them
    global unverifiedTxs
    for tx in txs:
        randomSleepTime = random.uniform(0, 1)
        time.sleep(randomSleepTime)
        unverifiedTxs[tx['number']] = tx
    time.sleep(5)
    global stop_malicious
    stop_malicious = True
    while True:
        lengths = set([len(nodes[id].txInChain) for id in honest_nodes])
        if len(lengths)==1:
            global stop_threads
            stop_threads = True
            print("Node length: ", list(lengths)[0])
            break
        print(lengths)
    nodes['Node0'].printBlockChain()

    # wait for all nodes to stop
    for id, node in nodes.items():
        if id in honest_nodes:
            node.print()
        node.join()
    print('all done!')

def idxToKey(idx):
    return 'Node' + str(idx)

def startNodes(numHonest, numMalicious, genesisBlock):
    global nodes
    honest_node_ids = set()
    for i in range(numHonest):
        key = idxToKey(i)
        honest_node_ids.add(key)
        # Create node in thread
        nodes[key] = HonestNode(key, genesisBlock)
        # Start it
        nodes[key].start()
    
    for i in range(numMalicious):
        key = idxToKey(numHonest+i)
        # Create node in thread
        nodes[key] = MaliciousNode(key, genesisBlock)
        # Start it
        nodes[key].start()
    return honest_node_ids


def setupTxs(file_name):
    return txGenerator.main(file_name)

NUM_HONEST_NODES = 5
NUM_MALICIOUS_NODES = 2

if __name__ == "__main__":
    # create genesis block
    # validate user input
    if len(sys.argv) < 2:
        print("you must specify a path to your input json")
        exit(0)
    # get data
    file_name = sys.argv[1]
    genesisTx = setupTxs(file_name)
    genesisBlock = Block(genesisTx, genesisTx, "")
    with open(file_name) as json_file:
        txs = json.loads(json_file.read())
    driver(txs, NUM_HONEST_NODES,NUM_MALICIOUS_NODES, genesisBlock)

