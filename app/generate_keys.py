from eth_keys import keys
from eth_typing import Address
from eth_utils import decode_hex

#set up addresses first
SENDER_PRIVATE_KEY = keys.PrivateKey(
    decode_hex('0x45a915e4d060149eb4365960e6a7a45f334393093061116b197e3240065ff2d8')
)

SENDER = Address(SENDER_PRIVATE_KEY.public_key.to_canonical_address())

print(SENDER_PRIVATE_KEY.public_key.to_canonical_address())