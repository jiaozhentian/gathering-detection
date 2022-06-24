from __init__ import *

import cv2
import base64
import numpy as np
from src.caculate_distance import CaculateDistance


class GatheringInfer(object):

    def __init__(self, pulsar_message, output_topic):
        self.pulsar_message = pulsar_message
        self.image = self._base64_to_image(pulsar_message['sourceFile'])
        self.distance_threshold = float(pulsar_message['algoParams']['distanceThreshold'])
        self.max_person = float(pulsar_message['algoParams']['maxPerson'])
        self.ouput_topic = output_topic
    
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
        