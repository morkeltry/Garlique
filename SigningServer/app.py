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
from hexbytes import HexBytes
from eth_account.messages import encode_defunct
from config import *


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
    ):
        return redirect(request.url.replace("http://", "https://", 301))


@app.route("/sign", methods=["POST"])
def sign():
    """
    Signs a message if tx has been done on the blockchain
    json params:
        @txhash
        @value
        @recipient
        @salt
        @blocknumber
    returns:
        @signature
    """
    if request.method == "POST":
        data = request.get_json()
        txhash = data["txhash"]
        value = data["value"]
        recipient = data["recipient"]
        salt = data["salt"]
        blocknumber = data["blocknumber"]

        blockexplorer_url = f"https://api.etherscan.io/api?module=proxy&action=eth_getTransactionByHash&txhash={txhash}&apikey={ETHERSCAN_API_KEY}"
        r = requests.get(blockexplorer_url)
        if r.status_code != 200:
            return make_response(
                jsonify({"error": "Could not get transaction from blockexplorer"}), 400
            )

        if "result" not in r.json():
            return make_response(jsonify({"error": "tx not found"}), 400)

        result = r.json()["result"]
        print(result)
        # TODO: some validation logic that makes sense here
        if result["blockNumber"] != blocknumber:
            return make_response(jsonify({"error": "tx not confirmed"}), 400)

        # sign json object
        message = {
            "txhash": txhash,
            "value": value,
            "recipient": recipient,
            "salt": salt,
            "blocknumber": blocknumber,
        }
        signature = sign_message(message)
        return jsonify({"signature": signature})
    else:
        return jsonify({"error": "invalid request"})


def store_on_IPFS(cheque):
    """
    Encrypts and stores a cheque on IPFS
    """
    cid = w3.post_upload('helllo')
    w3_storage = w3storage.API(token=NFT_STORAGE_API_KEY)


    pass


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
    Deletes a cheque from storage
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
    address = w3.eth.account.recover_message(message,signature=HexBytes("0x0293cc0d4eb416ca95349b7e63dc9d1c9a7aab4865b5cd6d6f2c36fb1dce12d34a05039aedf0bc64931a439def451bcf313abbcc72e9172f7fd51ecca30b41dd1b"))
    print(address)
    # use 



if __name__ == "__main__":
    app.run(debug=True)

    # test with curl
    # curl -H "Content-Type: application/json" -X POST -d '{"txhash":"0xadb037f6d8d2f31c39d3ac14ab2590956b74ddb8fbf9f0d74176ac3c43d709c0","value":"1000000000000000000","recipient":"0x2a1cb5fd815b0ec7628c2f70276b552c12921fd2032d11ca1423a939e51682eb","salt":"271721t ","blocknumber":"0xf0b04f"}' http://127.0.0.1:5000/sign
