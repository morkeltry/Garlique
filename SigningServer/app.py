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
from ecdsa import SigningKey
import ecdsa

# # generate ecdsa key pair
# signing_key = SigningKey.generate(curve=ecdsa.SECP256k1)
# verify_key = signing_key.get_verifying_key()
# SERVER_PRIVATE_KEY = signing_key.to_string().hex()
# SERVER_PUBLIC_KEY = verify_key.to_string().hex()
SERVER_PRIVATE_KEY = "badea878ddd6f34cd2d061f3a095f3dba6be10357d5c5ef0b7e5a64ced930809"
SERVER_PUBLIC_KEY = "63439c944f4a2680cb9cd13a45341241fb6bb22c9df5a3028aae5766d589464ddd084ef3f8f873217c200b1a8d66e39f17eaeb7a9a0b02c27a6e181ee7a729e1"
signing_key = SigningKey.from_string(
    bytes.fromhex(SERVER_PRIVATE_KEY), curve=ecdsa.SECP256k1
)
verify_key = signing_key.get_verifying_key()
print(f"SERVER_PRIVATE_KEY: {SERVER_PRIVATE_KEY}")
print(f"SERVER_PUBLIC_KEY: {SERVER_PUBLIC_KEY}")

app = Flask(__name__)
ETHERSCAN_API_KEY = "A5B6KPZ99R1DHF94EEAJMIUSW3DWJDQCM5"


# before request redirect to https
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


def sign_message(message):
    """
    Signs a message with the server's private key
    """
    message = json.dumps(message, sort_keys=True)
    signature = signing_key.sign(message.encode())
    print(len(signature))
    return signature.hex()


if __name__ == "__main__":
    app.run(debug=True)

    # test with curl
    # curl -H "Content-Type: application/json" -X POST -d '{"txhash":"0xadb037f6d8d2f31c39d3ac14ab2590956b74ddb8fbf9f0d74176ac3c43d709c0","value":"1000000000000000000","recipient":"0x2a1cb5fd815b0ec7628c2f70276b552c12921fd2032d11ca1423a939e51682eb","salt":"271721t ","blocknumber":"0xf0b04f"}' http://127.0.0.1:5000/sign
