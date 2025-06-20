import requests
import json

class Node:
    def __init__(self, address):
        self.address = address
        self.peers = set()

    def add_peer(self, peer_address):
        self.peers.add(peer_address)

    def broadcast_block(self, block_data):
        for peer in list(self.peers):
            try:
                requests.post(f"{peer}/add_block", json=block_data, timeout=3)
            except requests.exceptions.RequestException:
                self.peers.remove(peer)

    def broadcast_transaction(self, tx_data):
        for peer in list(self.peers):
            try:
                requests.post(f"{peer}/new_transaction", json=tx_data, timeout=3)
            except requests.exceptions.RequestException:
                self.peers.remove(peer)