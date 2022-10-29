# Make a unique domain
from eip712_structs import make_domain
from web3 import Web3
from app import hash_712, sign_message, verify_signature

# Define your struct type
from eip712_structs import EIP712Struct, Address, Boolean, Bytes, Int, String, Uint

import time
name = "Garlique"
version = "0.1"
domain = make_domain(name=name, version=version, chainId=5)


value = Web3.toWei(1, "ether") # bytes32
redeemFromUnixTime = int(time.time()) # bytes32
rcvr = "0x064bd35c9064fc3e628a3be3310a1cf65488103d" # bytes32
rcvr_type = "0"  # 1 byte
custody_option = "0"  # 1 byte
salt = "1234"  # 12 bytes


bytes_712 = hash_712(value, redeemFromUnixTime, rcvr, rcvr_type, custody_option, salt)
print(bytes_712.hex())


# save all values and the hash to a file
with open("example_cheque.txt", "w") as f:
    f.write(f"value: {value}\n")
    f.write(f"redeemFromUnixTime: {redeemFromUnixTime}\n")
    f.write(f"rcvr: {rcvr}\n")
    f.write(f"rcvr_type: {rcvr_type}\n")
    f.write(f"custody_option: {custody_option}\n")
    f.write(f"salt: {salt}\n")
    f.write(f"domain inputs: 'name': {name}, 'version': {version}, 'chainId': 5\n")

    f.write(f"\nOUTPUTS:\n")
    f.write(f"hash: {bytes_712.hex()}\n")


# Sign the message
from eth_account.messages import encode_defunct
from eth_account import Account

# Sign the message
account = Account.from_key("0x0000000000000000000000000000000000000000000000000000000000000001")