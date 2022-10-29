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
from werkzeug.exceptions import HTTPException
import requests
from ecdsa import SigningKey


app = Flask(__name__)
ETHERSCAN_API_KEY = "A5B6KPZ99R1DHF94EEAJMIUSW3DWJDQCM5"

# before request redirect to https
@app.before_request
def before_request():
    if request.url.startswith("http://") and not "127.0." and not "192.168." in request.url:
        return redirect(request.url.replace("http://", "https://", 301))



@app.route('/sign', methods=['POST'])
def sign():
    """
    Signs a message if tx has been done on the blockchain
    json params: 
        @txhash
        @value
        @recipient
        @salt
        @blockheight
    returns:
        @signature
    """
    if request.method == 'POST':
        data = request.get_json()
        txhash = data['txhash']
        value = data['value']
        recipient = data['recipient']
        salt = data['salt']
        blockheight = data['blockheight']

        blockexplorer_url = f"https://api.etherscan.io/api?module=proxy&action=eth_getTransactionByHash&txhash={txhash}&apikey={ETHERSCAN_API_KEY}"
        r = requests.get(blockexplorer_url)
        if r.status_code == 200:
            # tx exists on blockchain
            # TODO: further verification

            # sign json object
            message = {
                "txhash": txhash,
                "value": value,
                "recipient": recipient,
                "salt": salt,
                "blockheight": blockheight
            }
            signature = sign_message(message)
            return jsonify({"signature": signature})
        else:
            print(r.status_code)
            return jsonify({"error": "tx not found"})
    else:
        return jsonify({"error": "invalid request"})


def sign_message(message):
    """
    Signs a message with the server's private key
    """
    key = RSA.importKey(SERVER_PRIVATE_KEY)
    signature = key.sign(message, '')
    return signature
    

if __name__ == '__main__':
    app.run(debug=True)

    # test with curl
    # curl -H "Content-Type: application/json" -X POST -d '{"txhash":"0xadb037f6d8d2f31c39d3ac14ab2590956b74ddb8fbf9f0d74176ac3c43d709c0","value":"1000000000000000000","recipient":"0x2a1cb5fd815b0ec7628c2f70276b552c12921fd2032d11ca1423a939e51682eb","salt":"271721t ","blockheight":"111"}' http://127.0.0.1:5000/sign


