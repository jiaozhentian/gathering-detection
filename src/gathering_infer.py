from itertools import count
from __init__ import *

import cv2
import base64
import json
import requests
import numpy as np
from src.caculate_distance import CaculateDistance


class GatheringInfer(object):

    def __init__(self, pulsar_message, output_topic):
        self.pulsar_message = pulsar_message
        self.image = self._base64_to_image(pulsar_message['sourceFile'])
        self.distance_threshold = float(pulsar_message['algoParams']['distanceThreshold'])
        self.max_person = float(pulsar_message['algoParams']['maxPerson'])
        self.ouput_topic = output_topic
        self.detection_classes = ['bicycle', 'bus', 'car', 'motorcycle', 'person', 'truck']
        self.color_list = [[0, 0, 255], [0, 255, 0], [255, 0, 0], [0, 255, 255], [255, 0, 255], [255, 255, 0]]
        self.count_setting = 0
        self.distance_threshold = config.get("Algorithm", "distance_coefficient")
        self.people_count_setting = 0
        self.detection_confidence = config.get("Algorithm", "detection_confidence")
    
    def _base64_to_image(self, base64_code):
        """
        Turn base64 code to cv2 image
        :param base64_code: base64 code
        :param return: cv2 image, numpy.ndarray
        """
        # base64 decode
        img_data = base64.b64decode(base64_code)
        # 转换为np数组
        img_array = np.fromstring(img_data, np.uint8)
        # 转换成opencv可用格式
        img = cv2.imdecode(img_array, cv2.COLOR_RGB2BGR)
        return img
    
    def _image_to_base64(self, image):
        """
        Turn cv2 image to base64 code
        :param image: cv2 image, numpy.ndarray
        :param return: base64 code
        """
        # 转换为图像数据
        img_data = cv2.imencode('.jpg', image)[1]
        # 编码为base64
        base64_code = base64.b64encode(img_data)
        return base64_code
    
    def run(self):
        """
        Run the algorithm
        """
        if self.image is None:
            logger.error("The input image is None")
            return
        classes_result = []
        location_result = []
        score_result = []
        crowd_warning_status = False
        count_warning_status = False

        # 以下是我请求自己的接口，获取检测结果
        instance = [{"b64": self._image_to_base64(self.image)}]
        predict_request = json.dumps({"instances": instance})
        headers = {"Content-Type": "application/json"}
        response = requests.post("http://127.0.0.1:8501/v1/models/object_detection:predict", data=predict_request, headers=headers)
        response.raise_for_status()
        prediction = np.array(response.json()["predictions"])
        prediction = prediction[0]

        if prediction != []:
            boxes = prediction[:, 1:5]
            boxes[:, [0, 1, 2, 3]] = boxes[:, [1, 0, 3, 2]]
            boxes[:, 2:4] += boxes[:, 0:2] # 老模型要这一操作，新模型不需要
            classes = prediction[:, 6].astype(int)
            scores = prediction[:, 5]
            # 对检测结果数据进行循环分析
            count_num = 0
            people_count = 0
            centers = []
            close_pair = []
            s_close_pair = []
            status = []
            for score, _class in zip(scores, classes):
                if score > self.detection_confidence and _class == 5:
                    left = int(boxes[count_num][0])
                    top = int(boxes[count_num][1])
                    right = int(boxes[count_num][2])
                    bottom = int(boxes[count_num][3])
                    centers.append([right-left, bottom-top, [int((left+right)/2), int((top+bottom)/2)]])
                    status.append(0)

                    # render the bounding box of the object on the image
                    cv2.rectangle(self.image, (left, top), (right, bottom), self.color_list[count_num], 2)
                    cv2.putText(self.image, 
                                self.detection_classes[_class], 
                                (left, top), 
                                cv2.FONT_HERSHEY_SIMPLEX, 
                                0.5, 
                                self.color_list[count_num], 
                                2)
                    classes_result.append(classes[count_num]-1)
                    location_result.append(boxes[count_num])
                    score_result.append(score)
                count_num += 1
            # 如果画面中的人数超过一定人数，进行人数报警
            if people_count > self.people_count_setting:
                count_warning_status = True
            
            # 对检测结果数据进行循环分析
            for pointIndex in range(len(centers) - 1): # 因为最后一个值与自己计算距离是0, 如果centers是1或0，则会直接跳过
                for pointRest in range(pointIndex + 1, len(centers)):
                    # print(pointRest-pointIndex)
                    people_distance = CaculateDistance()
                    resultTemp = people_distance.isclose(centers[pointIndex], centers[pointRest])
                    if resultTemp == 1:
                        close_pair.append([centers[pointIndex][2], centers[pointRest][2]])
                        # 由于这是单相无重复遍历，所以在这里距离的起点坐标与重点坐标索引都需要进行加1
                        status[pointIndex] += 1
                        status[pointRest] += 1
                    elif resultTemp == 2:
                        s_close_pair.append([centers[pointIndex][2], centers[pointRest][2]])
                        status[pointIndex] += 0.5
                        status[pointRest] += 0.5
            if status != []:
                if max(status) >= self.count_setting:
                    # The warning is raised
                    crowd_warning_status = True
                    cv2.putText(self.image, text="WARING", org=(50, 50), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=(0, 0, 255), thickness=2)
                for h in close_pair:
                    cv2.line(self.image, tuple(h[0]), tuple(h[1]), (0, 0, 255), 2)
                for b in s_close_pair:
                    cv2.line(self.image, tuple(b[0]), tuple(b[1]), (0, 255, 255), 2)
