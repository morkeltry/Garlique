#####################################################
# The Garlic server
# Simple web server that just serves up the static files
#####################################################

from flask import (
    Flask,
    Response,
    jsonify,
    make_response,
    redirect,
    request,
    render_template,
)
import json
from werkzeug.exceptions import HTTPException
import requests
import livereload

app = Flask(__name__, template_folder="./", static_folder="./", static_url_path="")


# before request redirect to https
@app.before_request
def before_request():
    if (
        request.url.startswith("http://")
        and not "127.0."
        and not "192.168." in request.url
    ):
        return redirect(request.url.replace("http://", "https://", 301))


@app.route("/")
def home():
    return render_template("home.html")


if __name__ == "__main__":

    app.config.update(
        DEBUG=True,
        TEMPLATES_AUTO_RELOAD=True,
    )
    app.run(debug=True, port=5001)

    # server = livereload.Server(app.wsgi_app)
    # server.serve()
