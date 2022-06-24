from __init__ import *
import argparse
from concurrent.futures import ThreadPoolExecutor
from src.gathering_infer import GatheringInfer
import src.pulsar_client as pulsar_client

def make_parser():
    # TODO: delete "args = []"
    parser = argparse.ArgumentParser(args = [],description="fall_down_algorithm")
    parser.add_argument("-it", "--inputtopic", type=str, help="pulsar input topic")
    parser.add_argument("-ot", "--outputtopic", type=str, help="pulsar output topic")
    return parser

def algoritm_main(message_data, output_topic):
    fall_down_infer = GatheringInfer(message_data, output_topic)
    fall_down_infer.run()

if __name__ == "__main__":
    logger.info("GATHERING ALGORITHM START")
    parser = make_parser()
    args = parser.parse_args()
    # pulsar init
