import numpy as np
import paddle


def iou(box1, box2):
    N = box1.size(0)
    M = box2.size(0)

    lt = paddle.max(  # 左上角的点
        box1[:, :2].unsqueeze(1).expand(N, M, 2),  # [N,2]->[N,1,2]->[N,M,2]
        box2[:, :2].unsqueeze(0).expand(N, M, 2),  # [M,2]->[1,M,2]->[N,M,2]
    )

    rb = paddle.min(
        box1[:, 2:].unsqueeze(1).expand(N, M, 2),
        box2[:, 2:].unsqueeze(0).expand(N, M, 2),
    )

    wh = rb - lt  # [N,M,2]
    wh[wh < 0] = 0  # 两个box没有重叠区域
    inter = wh[:, :, 0] * wh[:, :, 1]  # [N,M]

    area1 = (box1[:, 2] - box1[:, 0]) * (box1[:, 3] - box1[:, 1])  # (N,)
    area2 = (box2[:, 2] - box2[:, 0]) * (box2[:, 3] - box2[:, 1])  # (M,)
    area1 = area1.unsqueeze(1).expand(N, M)  # (N,M)
    area2 = area2.unsqueeze(0).expand(N, M)  # (N,M)

    iou = inter / (area1 + area2 - inter)
    return iou


def np_nms(dets, thresh):
    """Pure Python NMS baseline."""
    # dets某个类的框，x1、y1、x2、y2、以及置信度score
    # eg:dets为[[x1,y1,x2,y2,score],[x1,y1,y2,score]……]]
    # thresh是IoU的阈值
    x1 = dets[:, 2]
    y1 = dets[:, 3]
    x2 = dets[:, 4]
    y2 = dets[:, 5]
    scores = dets[:, 1]
    # 每一个检测框的面积
    areas = (x2 - x1 + 1) * (y2 - y1 + 1)
    # 按照score置信度降序排序
    order = scores.argsort()[::-1]
    keep = []  # 保留的结果框集合
    while order.size > 0:
        i = order[0]
        keep.append(i)  # 保留该类剩余box中得分最高的一个
        # 得到相交区域,左上及右下
        xx1 = np.maximum(x1[i], x1[order[1:]])
        yy1 = np.maximum(y1[i], y1[order[1:]])
        xx2 = np.minimum(x2[i], x2[order[1:]])
        yy2 = np.minimum(y2[i], y2[order[1:]])
        # 计算相交的面积,不重叠时面积为0
        w = np.maximum(0.0, xx2 - xx1 + 1)
        h = np.maximum(0.0, yy2 - yy1 + 1)
        inter = w * h
        # 计算IoU：重叠面积 /（面积1+面积2-重叠面积）
        ovr = inter / (areas[i] + areas[order[1:]] - inter)
        # 保留IoU小于阈值的box
        inds = np.where(ovr <= thresh)[0]
        order = order[inds + 1]  # 因为ovr数组的长度比order数组少一个,所以这里要将所有下标后移一位
    return keep
