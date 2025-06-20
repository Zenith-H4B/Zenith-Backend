from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from blockchain.chain import Blockchain
from blockchain.transaction import Transaction
from network.node import Node
from network.p2p import P2PNetwork
import requests

app = FastAPI()
blockchain = Blockchain()
node = Node(address="http://localhost:8000")  # override per instance

class TxModel(BaseModel):
    sender: str
    recipient: str
    payload: dict

@app.post("/new_transaction")
def new_transaction(tx: TxModel):
    transaction = Transaction(
        sender=tx.sender,
        recipient=tx.recipient,
        payload=tx.payload
    )
    blockchain.add_transaction(transaction.to_dict())
    return {"message": "Transaction added"}

@app.get("/mine")
def mine_block():
    block = blockchain.mine()
    if not block:
        raise HTTPException(status_code=400, detail="No transactions to mine")
    node.broadcast_block(block.__dict__)
    return block.__dict__

@app.post("/add_block")
def add_block(block_data: dict):
    from blockchain.block import Block
    last_block = blockchain.chain[-1]
    new_block = Block(
        index=block_data['index'],
        transactions=block_data['transactions'],
        previous_hash=block_data['previous_hash'],
        timestamp=block_data['timestamp'],
        nonce=block_data['nonce']
    )
    # Validate hash and proof of work
    if new_block.previous_hash != last_block.hash:
        raise HTTPException(status_code=400, detail="Invalid previous hash")
    if new_block.hash != block_data['hash']:
        raise HTTPException(status_code=400, detail="Block hash mismatch")
    if not new_block.hash.startswith('0' * blockchain.difficulty):
        raise HTTPException(status_code=400, detail="Invalid proof of work")
    blockchain.chain.append(new_block)
    return {"message": "Block added to chain"}

@app.get("/chain")
def get_chain():
    chain_data = [block.__dict__ for block in blockchain.chain]
    return {"length": len(chain_data), "chain": chain_data}

@app.on_event("startup")
def startup_event():
    p2p = P2PNetwork(node, blockchain)
    p2p.sync_chain()

class PeerModel(BaseModel):
    address: str

@app.post("/add_peer")
def add_peer(peer: PeerModel):
    node.add_peer(peer.address)
    return {"message": f"Peer {peer.address} added"}

@app.get("/peers")
def get_peers():
    return {"peers": list(node.peers)}

@app.post("/broadcast_transaction")
def broadcast_transaction(tx: TxModel):
    transaction = Transaction(
        sender=tx.sender,
        recipient=tx.recipient,
        payload=tx.payload
    )
    blockchain.add_transaction(transaction.to_dict())
    for peer in node.peers:
        try:
            requests.post(f"{peer}/new_transaction", json=tx.dict(), timeout=3)
        except requests.exceptions.RequestException:
            continue
    return {"message": "Transaction broadcasted"}