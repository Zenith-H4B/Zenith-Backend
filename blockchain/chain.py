from .block import Block

class Blockchain:
    difficulty = 2

    def __init__(self):
        self.chain = []
        self.unconfirmed_transactions = []
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_block = Block(0, [], "0", timestamp=0, nonce=0)
        self.chain.append(genesis_block)

    def add_transaction(self, tx_data):
        self.unconfirmed_transactions.append(tx_data)

    def mine(self):
        if not self.unconfirmed_transactions:
            return False

        last_block = self.chain[-1]
        new_block = Block(len(self.chain), self.unconfirmed_transactions, last_block.hash)
        while not new_block.hash.startswith('0' * self.difficulty):
            new_block.nonce += 1
            new_block.hash = new_block.compute_hash()

        self.chain.append(new_block)
        self.unconfirmed_transactions = []
        return new_block
