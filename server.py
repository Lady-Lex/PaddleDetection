import base64
import random
import string
import time

import cv2
import numpy as np
from flask import Flask, jsonify, make_response, request, session
from flask_cors import CORS
from PIL import Image
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "sfdafsasfcas"
app.config["SESSION_COOKIE_SAMESITE"] = "None"  # 设置samesite 为None
app.config["SESSION_COOKIE_SECURE"] = True  # SECURE 为 true

CORS(app, supports_credentials=True)

host = "10.29.0.151"
port = 3200


def predict(image_np: np.ndarray):
    return


@app.route("/")
def clear():
    resp = make_response("success")
    id = "".join(random.sample(string.digits, 8))
    resp.set_cookie("id", id)
    return resp


@app.route("/upload", methods=["POST"])
def upload():
    id = request.cookies.get("id", None)
    data = request.get_json()["data"]
    data = data.split(",")[1]

    img_data = base64.b64decode(data)
    nparr = np.fromstring(img_data, np.uint8)
    img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # image_path = "./uploads/" + secure_filename(f"{id} {time.time()}.jpg")

    # im = Image.fromarray(img_np)
    # im.save(image_path)

    processed_image = predict(img_np)

    retval, buffer = cv2.imencode(".jpg", img_np)
    processed_image_base64 = base64.b64encode(buffer)
    processed_image_base64 = processed_image_base64.decode()

    return jsonify({"processed_image_base64": processed_image_base64})


if __name__ == "__main__":
    app.run(
        host=host,
        port=port,
        debug=True,
        ssl_context="adhoc",
    )
