from eth_keys import keys
from eth_utils import decode_hex, encode_hex, to_wei
from eth_typing import Address
from eth import constants
from eth.chains.base import MiningChain
from eth.consensus.pow import mine_pow_nonce
from eth.vm.forks.byzantium import ByzantiumVM
from eth.db.atomic import AtomicDB


#set up addresses first
SENDER_PRIVATE_KEY = keys.PrivateKey(
    decode_hex('0x45a915e4d060149eb4365960e6a7a45f334393093061116b197e3240065ff2d8')
)

SENDER = Address(SENDER_PRIVATE_KEY.public_key.to_canonical_address())

RECEIVER = Address(b'\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\x01')

#sender balance
DEFAULT_INITIAL_BALANCE = to_wei(10, 'ether')

#set up chain
GENESIS_PARAMS = {
    'parent_hash': constants.GENESIS_PARENT_HASH,
    'uncles_hash': constants.EMPTY_UNCLE_HASH,
    'coinbase': constants.ZERO_ADDRESS,
    'transaction_root': constants.BLANK_ROOT_HASH,
    'receipt_root': constants.BLANK_ROOT_HASH,
    'difficulty': 1,
    'block_number': constants.GENESIS_BLOCK_NUMBER,
    'gas_limit': 3141592,
    'timestamp': 1514764800,
    'extra_data': constants.GENESIS_EXTRA_DATA,
    'nonce': constants.GENESIS_NONCE
}

GENESIS_STATE = {
    SENDER: {
        "balance": DEFAULT_INITIAL_BALANCE,
        "nonce": 0,
        "code": b'',
        "storage": {}
    }
}

klass = MiningChain.configure(
    __name__='TestChain',
    vm_configuration=(
        (constants.GENESIS_BLOCK_NUMBER, ByzantiumVM),
    ))

chain = klass.from_genesis(AtomicDB(), GENESIS_PARAMS, GENESIS_STATE)

vm = chain.get_vm()

#print sender initial balance
sender_balance = chain.get_vm().state.account_db.get_balance(SENDER)

print("The initial balance of address {} is {} wei".format(
    encode_hex(SENDER),
    sender_balance)
)

nonce = vm.state.account_db.get_nonce(SENDER)

tx = vm.create_unsigned_transaction(
    nonce=nonce,
    gas_price=0,
    gas=100000,
    to=RECEIVER,
    value=to_wei(1, 'ether'),
    data=b'',
)

signed_tx = tx.as_signed_transaction(SENDER_PRIVATE_KEY)

chain.apply_transaction(signed_tx)

# We have to finalize the block first in order to be able read the
# attributes that are important for the PoW algorithm
block = chain.get_vm().finalize_block(chain.get_block())

# based on mining_hash, block number and difficulty we can perform
# the actual Proof of Work (PoW) mechanism to mine the correct
# nonce and mix_hash for this block
nonce, mix_hash = mine_pow_nonce(
    block.number,
    block.header.mining_hash,
    block.header.difficulty
)

chain.mine_block(mix_hash=mix_hash, nonce=nonce)

print(block)

receiver_balance = chain.get_vm().state.account_db.get_balance(RECEIVER)

print("The balance of address {} is {} wei".format(
    encode_hex(RECEIVER),
    receiver_balance)
)

sender_balance = chain.get_vm().state.account_db.get_balance(SENDER)

print("The balance of address {} is {} wei".format(
    encode_hex(SENDER),
    sender_balance)
)

