
# Create an EXAMPLE instance with some data

# value32b,redeemFromUnixTime32b, rcvr32b, rcvr_type1b {0..4}, custody_option1b {0..}, salt4b
# EXAMPLE
from web3 import Web3
# value (format 1 Eth with web3)
value = Web3.toWei(1, "ether")
# format timestamp to bytes32
# get current timestamp
import time
timestamp = int(time.time())
timestamp = timestamp.to_bytes(32, byteorder="big")

receiver = "0x064bd35c9064fc3e628a3be3310a1cf65488103d"
# receiver to bytes32
receiver = receiver[2:]
receiver = receiver.zfill(64)

receiver_type = "0"

custody_option = "0"

salt = "1234"