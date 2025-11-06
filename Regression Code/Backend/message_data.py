#data/message_data.py
from dataclasses import dataclass, field
from typing import Any, Dict, Optional
import cantools

@dataclass
class MessageData:
    message: cantools.db.Message
    data: Dict[str, Any] = field(default_factory=dict) #we use default_factiry=dict so that each object ahs a different dictionary and there is no sharing between objects
    raw_data: Optional[bytes] = None

    '''
    encode_data will encode the data that exists in the message object
    @return: raw_data
    '''
    def encode_data(self):
        self.raw_data = self.message.encode(self.data)
        return self.raw_data
    
    '''
    deode_data will decode the data that is passed in
    @raw_data: bytes of the raw data you want decoded
    @return: data
    '''
    def decode_data(self, raw_data: bytes):
        self.raw_data = raw_data
        self.data = self.message.decode(raw_data)
        return self.data