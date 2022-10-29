from eth_account import Account
from eth_account.signers.local import LocalAccount
from eth_account.messages import encode_defunct, _hash_eip191_message
from web3.auto import w3
from eip712_structs import EIP712Struct, Address, Boolean, Bytes, Int, String, Uint, make_domain


PRIVATE_KEY = "0x4d9e599423f0a37115c35f1dc4b749a4754545e4172d3901260a484512eee4d6"


def hash_712(value, timestamp, receiver, receiver_type, custody_option, salt):
    """
    Hashes a message using the EIP712 standard
    """
    domain = make_domain(name="Garlique", version="0.1", chainId=5)

    class Cheque(EIP712Struct):
        value = Uint(256)
        timestamp = Uint(256)
        receiver = Address()
        receiver_type = Bytes(1)
        custody_option = Bytes(1)
        salt = Bytes(4)
    # Create an instance with some data
    mine = Cheque(value=value, timestamp=timestamp, receiver=receiver, receiver_type=receiver_type, custody_option=custody_option, salt=salt)
    # Into signable bytes - domain required
    my_bytes = mine.signable_bytes(domain)
    return my_bytes


def sign_message(message):
    """
    Signs a message and returns r, s, v
    """
    message = encode_defunct(text=message)
    signed_message = w3.eth.account.sign_message(message, private_key=PRIVATE_KEY)
    r = signed_message.r
    s = signed_message.s
    v = signed_message.v
    return r, s, v
    



def verify_signature(address, message, signature):
    """
    Verifies a signature for a given ethereum address
    """
    message = encode_defunct(text=message)
    recovered_message = w3.eth.account.recover_message(message, signature=signature)
    return recovered_message == address



if __name__ == "__main__":
    # run on local network
    print(sign_message("hello"))


# def hash_payload_eip712(payload):
#     """
#     Hashes a payload according to EIP712
#     """
    
#     return _hash_eip191_message(payload)

# def hash_message(value32b, redeemFromUnixTime32b, rcvr32b, rcvr_type1b, custody_option1b, salt4b):
#     """
#     Hashes message using EIP-191
#     value32b,redeemFromUnixTime32b, rcvr32b, rcvr_type1b {0..4}, custody_option1b {0..}, salt4b
#     """
#     # format
    


# from ecdsa import SigningKey
# import ecdsa
# signing_key = SigningKey.from_string(
#     bytes.fromhex(SERVER_PRIVATE_KEY), curve=ecdsa.SECP256k1
# )
# verify_key = signing_key.get_verifying_key()

# def sign_message(message):
#     """
#     Signs a message with the server's private key
#     """
#     message = json.dumps(message, sort_keys=True)
#     signature = signing_key.sign(message.encode())
#     # get v,r,s
#     v, r, s = ecdsa.util.sigdecode_string(signature, ecdsa.SECP256k1.order)
#     return v, r, s
#     return signature.hex()