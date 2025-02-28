import cv2
import numpy as np
import paddle
from deploy.python.utils import argsparser
from deploy.python.infer import Detector, visualize_box_mask, print_arguments
from deploy.python.my_utils import np_nms


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

        cv2.namedWindow('Pet Detection', cv2.WINDOW_FREERATIO)
        cv2.imshow('Pet Detection', im)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


if __name__ == '__main__':
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
    if FLAGS.video_file is not None or FLAGS.camera_id != -1:
        predict_video_or_stream(detector, FLAGS.video_file, FLAGS.camera_id)
