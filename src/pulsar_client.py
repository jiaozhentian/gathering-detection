import os
import time
import pulsar
from __init__ import logger, config

class Get_Results(object):
    def __init__(self, topic_name):
        self.logger = logger
        self.logger.info("Pulsar client init")
        self.pulsar_host = config.get('Pulsar', "pulsar_host")
        self.pulsar_port = config.get('Pulsar', "pulsar_port")
        self.pulsar_topic = topic_name
        pulsar_address = "pulsar://" + self.pulsar_host + ":" + self.pulsar_port
        self.pulsar_client = pulsar.Client(pulsar_address)
        self.consumer = self.pulsar_client.subscribe(self.pulsar_topic, "fall_down_algorithm")
    
    def get_results(self):
        self.logger.info("Getting results from topic: %s...", self.pulsar_topic)
        message = self.consumer.receive()
        self.consumer.acknowledge(message)
        self.logger.info("Got results from topic: %s", self.pulsar_topic)
        # self.logger.debug("Get_Results message: %s", message)
        return message

    def close(self):
        self.logger.info("Closing Get_Results...")
        self.pulsar_client.close()
        self.logger.info("Closed Get_Results")


class Send_Results(object):
    def __init__(self, topic_name):
        self.logger = logger
        self.logger.info("Pulsar client init")
        self.pulsar_host = config.get('Pulsar', "pulsar_host")
        self.pulsar_port = config.get('Pulsar', "pulsar_port")
        self.pulsar_topic = topic_name
        pulsar_address = "pulsar://" + self.pulsar_host + ":" + self.pulsar_port
        self.pulsar_client = pulsar.Client(pulsar_address)
        self.producer = self.pulsar_client.create_producer(self.pulsar_topic)
    
    def send_results(self, message_data):
        self.logger.info("Sending results to topic: %s...", self.pulsar_topic)
        message = pulsar.Message(data=str(message_data))
        self.producer.send(message)
        self.logger.info("Sent results to topic: %s", self.pulsar_topic)
    
    def close(self):
        self.logger.info("Closing Send_Results...")
        self.pulsar_client.close()
        self.logger.info("Closed Send_Results")