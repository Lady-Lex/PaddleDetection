import base64
import random
import string

import cv2
import numpy as np
from flask import Flask, jsonify, make_response, request, session
from flask_cors import CORS
from PIL import Image
from werkzeug.utils import secure_filename
import cv2
import numpy as np
import paddle
from deploy.python.utils import argsparser
from deploy.python.infer import Detector, visualize_box_mask, print_arguments
from deploy.python.my_utils import np_nms

app = Flask(__name__)
app.secret_key = "sfdafsasfcas"
app.config["SESSION_COOKIE_SAMESITE"] = "None" 
app.config["SESSION_COOKIE_SECURE"] = True  

CORS(app, supports_credentials=True)

host = "10.29.157.26"
port = 3200




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

    retval, buffer = cv2.imencode(".jpg", processed_image)
    processed_image_base64 = base64.b64encode(buffer)
    processed_image_base64 = processed_image_base64.decode()

    return jsonify({"processed_image_base64": processed_image_base64})


paddle.enable_static()
parser = argsparser()
FLAGS = parser.parse_args()
print_arguments(FLAGS)
FLAGS.device = FLAGS.device.upper()
assert FLAGS.device in ['CPU', 'GPU', 'XPU', 'NPU'
                        ], "device should be CPU, GPU, XPU or NPU"
assert not FLAGS.use_gpu, "use_gpu has been deprecated, please use --device"

assert not (
    FLAGS.enable_mkldnn == False and FLAGS.enable_mkldnn_bfloat16 == True
), 'To enable mkldnn bfloat, please turn on both enable_mkldnn and enable_mkldnn_bfloat16'

detector = Detector(
    FLAGS.model_dir,
    device=FLAGS.device,
    run_mode=FLAGS.run_mode,
    batch_size=FLAGS.batch_size,
    trt_min_shape=FLAGS.trt_min_shape,
    trt_max_shape=FLAGS.trt_max_shape,
    trt_opt_shape=FLAGS.trt_opt_shape,
    trt_calib_mode=FLAGS.trt_calib_mode,
    cpu_threads=FLAGS.cpu_threads,
    enable_mkldnn=FLAGS.enable_mkldnn,
    enable_mkldnn_bfloat16=FLAGS.enable_mkldnn_bfloat16,
    threshold=FLAGS.threshold,
        output_dir=FLAGS.output_dir)

def predict(image_np: np.ndarray)-> np.ndarray:
    results = detector.predict_image([image_np[:, :, ::-1]], visual=False, run_benchmark=False)

    # 非极大化抑制
    keep = np_nms(results['boxes'], 0.5)
    results['boxes'] = results['boxes'][keep]

    im = visualize_box_mask(
        image_np,
        results,
        detector.pred_config.labels,
        threshold=detector.threshold)
    im = np.array(im)
    return im


def predict_video_or_stream(detector, video_file, camera_id):
    if camera_id != -1:
        capture = cv2.VideoCapture(camera_id)
    else:
        capture = cv2.VideoCapture(video_file)

    # Get Video info : resolution, fps, frame count
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(capture.get(cv2.CAP_PROP_FPS))
    frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    print("fps: %d, frame_count: %d" % (fps, frame_count))

    index = 1
    while 1:
        ret, frame = capture.read()
        if not ret:
            break
        print('detect frame: %d' % (index))
        index += 1
        results = detector.predict_image([frame[:, :, ::-1]], visual=False, run_benchmark=False)

        # 非极大化抑制
        keep = np_nms(results['boxes'], 0.5)
        results['boxes'] = results['boxes'][keep]

        im = visualize_box_mask(
            frame,
            results,
            detector.pred_config.labels,
            threshold=detector.threshold)
        im = np.array(im)

        cv2.namedWindow('Mask Detection', cv2.WINDOW_FREERATIO)
        cv2.imshow('Mask Detection', im)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


"""
python server2.py --model_dir=output_inference_old/config/ --video_file=try_cat2.mp4 --device=gpu  --thresh=0.5
"""


if __name__ == "__main__":
    # if FLAGS.video_file is not None or FLAGS.camera_id != -1:
    #     predict_video_or_stream(detector, FLAGS.video_file, FLAGS.camera_id)

    app.run(
        host=host,
        port=port,
        debug=True,
        ssl_context="adhoc",
    )
