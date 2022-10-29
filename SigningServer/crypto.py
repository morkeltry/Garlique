from eth_account import Account
from eth_account.signers.local import LocalAccount
from eth_account.messages import encode_defunct, _hash_eip191_message
from web3.auto import w3

private_key = "0x4d9e599423f0a37115c35f1dc4b749a4754545e4172d3901260a484512eee4d6"
assert private_key is not None, "You must set PRIVATE_KEY environment variable"
assert private_key.startswith("0x"), "Private key must start with 0x hex prefix"

account: LocalAccount = Account.from_key(private_key)


def sign_message(message):
    """
    Signs a message and returns r, s, v
    """
    message = encode_defunct(text=message)
    signed_message = w3.eth.account.sign_message(message, private_key=private_key)
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


def hash_message(message):
    """
    Hashes a message using EIP-191
    """
    message = encode_defunct(text=message)
    return _hash_eip191_message(message)


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