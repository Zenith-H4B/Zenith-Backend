
import time

class Transaction:
    def __init__(self, sender, recipient, payload, timestamp=None):
        self.sender = sender
        self.recipient = recipient
        self.payload = payload
        self.timestamp = timestamp or time.time()

    def to_dict(self):
        return {
            'sender': self.sender,
            'recipient': self.recipient,
            'payload': self.payload,
            'timestamp': self.timestamp
        }