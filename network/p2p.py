import requests
from blockchain.chain import Blockchain

class P2PNetwork:
    def __init__(self, node, blockchain: Blockchain):
        self.node = node
        self.blockchain = blockchain

    def sync_chain(self):
        # Fetch chains from peers, replace if longer and valid
        longest = self.blockchain.chain
        for peer in self.node.peers:
            try:
                response = requests.get(f"{peer}/chain", timeout=3).json()
                length = response['length']
                chain_data = response['chain']
                candidate_chain = self._deserialize_chain(chain_data)
                if length > len(longest) and self._is_valid_chain(candidate_chain):
                    longest = candidate_chain
            except Exception:
                continue
        self.blockchain.chain = longest

    def _deserialize_chain(self, chain_data):
        from blockchain.block import Block
        chain = []
        for block_dict in chain_data:
            block = Block(
                block_dict['index'],
                block_dict['transactions'],
                block_dict['previous_hash'],
                timestamp=block_dict['timestamp'],
                nonce=block_dict['nonce']
            )
            block.hash = block_dict['hash']
            chain.append(block)
        return chain

    def _is_valid_chain(self, chain):
        if not chain:
            return False
        for i in range(1, len(chain)):
            prev = chain[i-1]
            curr = chain[i]
            if curr.previous_hash != prev.hash:
                return False
            if curr.hash != curr.compute_hash():
                return False
        return True