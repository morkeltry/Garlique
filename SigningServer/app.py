#####################################################
# The Garlic Signing Server API
#
# Functionality:
#   - internal cheques
#   - issue external cheques
#####################################################

from flask import (
    Flask,
    Response,
    jsonify,
    make_response,
    redirect,
    request,
)
import json
from werkzeug.exceptions import HTTPException
import requests
import w3storage
from web3 import Web3
from web3.auto import w3
from hexbytes import HexBytes
from eth_account.messages import encode_defunct
from config import *
from eip712_structs import (
    EIP712Struct,
    Address,
    Boolean,
    Bytes,
    Int,
    String,
    Uint,
    make_domain,
)


# init Flask App
app = Flask(__name__)


internal_cheques = []  # array of internal cheques (for splitting and merging)
external_cheques = []  # array of external cheques (for user claiming)
ipfs_cheques = []  # array of IPFS hashes of cheques


# ensure https (don't want leaked cheques)
@app.before_request
def before_request():
    if (
        request.url.startswith("http://")
        and not "127.0."
        and not "192.168." in request.url
        and not "10.1." in request.url
    ):
        return redirect(request.url.replace("http://", "https://", 301))


@app.route("/", methods=["GET"])
def index():
    """
    Index page
    """
    return "Garlic Signing Server"


@app.route("/sign", methods=["POST"])
def sign():
    """
    Signs a message if tx has been done on the blockchain
    json params:
        @txhash
        @value
        @receiver
        @salt
        @blocknumber
    returns:
        @signature
    """
    print(request.json)
    if request.method == "POST":
        # value32b,redeemFromUnixTime32b, rcvr32b, rcvr_type1b {0..4}, custody_option1b {0..}, salt4b

        data = request.get_json()
        txhash = data["txhash"]  # txhash

        value = data["value"]
        redeemFromUnixTime = data["redeemFromUnixTime"]
        rcvr = data["rcvr"]
        rcvr_type = data["rcvr_type"]
        custody_option = data["custody_option"]
        salt = data["salt"]

        blockexplorer_url = f"https://api.etherscan.io/api?module=proxy&action=eth_getTransactionByHash&txhash={txhash}&apikey={ETHERSCAN_API_KEY}"
        r = requests.get(blockexplorer_url)
        if r.status_code != 200:
            return make_response(
                jsonify({"error": "Could not get transaction from blockexplorer"}), 400
            )

        if "result" not in r.json():
            return make_response(jsonify({"error": "tx not found"}), 400)

        result = r.json()["result"]

        # TODO: some validation logic that makes sense here
        # if result["blockNumber"] != blocknumber:
        #     return make_response(jsonify({"error": "tx not confirmed"}), 400)

        # BLOCK IS VALIDATED, let's issue a cheque

        # hash the cheque
        # cast value & redeemFromUnixTime to
        value = Web3.toWei(float(value), "ether")
        redeemFromUnixTime = int(redeemFromUnixTime)
        hashed_cheque = hash_712(
            value, redeemFromUnixTime, rcvr, rcvr_type, custody_option, salt
        )
        hashed_cheque = hashed_cheque.hex()
        print(hashed_cheque, type(hashed_cheque))

        # sign the cheque
        r, s, v = sign_message(hashed_cheque)

        cheque = {
            "cheque": {
                "value": value,
                "redeemFromUnixTime": redeemFromUnixTime,
                "rcvr": rcvr,
                "rcvr_type": rcvr_type,
                "custody_option": custody_option,
                "salt": salt,
            },
            "hashed_cheque": hashed_cheque,
            "signature": {"r": r, "s": s, "v": v},
        }

        # store the cheque on IPFS
        cheque = json.dumps(cheque) # make into string
        cid = store_on_IPFS(cheque)

        # return the signature
        return make_response(
            jsonify( 
                {
                    "hashed_cheque": hashed_cheque,
                    "signature": {"r": r, "s": s, "v": v},
                    "ipfs_cid": cid,
                }
            ),
            200,
        )
    else:
        return jsonify({"error": "invalid request"})


def store_on_IPFS(payload):
    """
    Encrypts and stores a cheque on IPFS
    returns the CID of the IPFS file
    """
    w3_storage = w3storage.API(token=WEB3_STORAGE_API_KEY)

    # encrypt cheque
    # pass

    # store on IPFS
    cid = w3_storage.post_upload(payload)
    return cid


def merge_internal_cheques(**kwargs):
    """
    Merges n internal (valid) cheques, deletes them from storage and returns a new cheque
    """
    pass


def split_internal_cheque(cheque, **kwargs):
    """
    Splits an internal cheque into n new cheques
    """
    pass


def redeem_internal_cheque(cheque):
    """
    Converts an internal cheque into an external cheque
    """
    pass


@app.route("/delete", methods=["POST"])
def delete_cheque(cheque):
    """
    Deletes a cheque from persistent storage
    """
    pass


@app.route("/cheques", methods=["GET"])
def get_cheques():
    """
    Returns all cheques for a given address (if signature is valid)
    @params:
        @address
        @message
        @signature
    """
    # params from request
    address = request.args.get("address")
    message = request.args.get("message")
    signature = request.args.get("signature")

    # validate signature
    if not verify_signature(address, message, signature):
        return make_response(jsonify({"error": "invalid signature"}), 400)
    pass


def verify_signature(address, message, signature):
    """
    Verifies a signature for a given ethereum address
    """
    w3 = Web3(Web3.HTTPProvider(""))
    message = encode_defunct(text="6875972781")
    address = w3.eth.account.recover_message(
        message,
        signature=HexBytes(
            "0x0293cc0d4eb416ca95349b7e63dc9d1c9a7aab4865b5cd6d6f2c36fb1dce12d34a05039aedf0bc64931a439def451bcf313abbcc72e9172f7fd51ecca30b41dd1b"
        ),
    )
    print(address)
    # use


def hash_712(value, redeemFromUnixTime, rcvr, rcvr_type, custody_option, salt):
    """
    Hashes a cheque using the EIP712 standard
    Assumes
    """

    domain = make_domain(name="Garlique", version="0.1", chainId=5)

    class Cheque(EIP712Struct):
        value = Uint(256)
        redeemFromUnixTime = Uint(256)
        rcvr = Address()
        rcvr_type = Bytes(1)
        custody_option = Bytes(1)
        salt = Bytes(4)

    # Create an instance with some data
    cheque = Cheque(
        value=value,
        redeemFromUnixTime=redeemFromUnixTime,
        rcvr=rcvr,
        rcvr_type=rcvr_type,
        custody_option=custody_option,
        salt=salt,
    )
    # Into signable bytes - domain required
    my_bytes = cheque.signable_bytes(domain)
    return my_bytes


def sign_message(message):
    """
    Signs a cheque hash using the private key
    """
    # sign message
    message = encode_defunct(text=message)
    signature = w3.eth.account.sign_message(message, private_key=PRIVATE_KEY)
    r = signature.r
    s = signature.s
    v = signature.v
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

    import socket

    hostname = socket.gethostname()
    IPAddr = socket.gethostbyname(hostname)
    print("Your Computer Name is:" + hostname)
    print("Your Computer IP Address is:" + IPAddr)

    app.run(host="0.0.0.0", debug=True)

    # test with curl
    """ 
    curl -H "Content-Type: application/json" -X POST -d '{"txhash":"0xadb037f6d8d2f31c39d3ac14ab2590956b74ddb8fbf9f0d74176ac3c43d709c0",  "value":"1",   "rcvr":"0x064bd35c9064fc3e628a3be3310a1cf65488103d",  "rcvr_type":"0",   "custody_option":"0",     "redeemFromUnixTime":"1630000000",    "salt":"1234"}'  http://10.1.0.70:5000/sign  
    """
