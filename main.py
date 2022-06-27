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
    parser.add_argument("-pip", "--pulasripaddress", type=str, help="pulsar ip address")
    parser.add_argument("-pp", "--pulasrport", type=int, help="pulsar port")
    parser.add_argument("-dip", "--detectionipaddress", type=str, help="detection ip address")
    parser.add_argument("-dp", "--detectionport", type=int, help="detection port")
    parser.add_argument("-dm", "--detectionmodel", type=str, help="detection model")
    return parser

def config_init():
    """
    modify the config file to you own config file
    """
    config.set("Pulsar", "pulsar_host", args.pulasripaddress)
    config.set("Pulsar", "pulsar_port", args.pulasrport)

def algoritm_main(message_data, output_topic):
    fall_down_infer = GatheringInfer(message_data, output_topic)
    fall_down_infer.run()

if __name__ == "__main__":
    logger.info("GATHERING ALGORITHM START")
    parser = make_parser()
    args = parser.parse_args()
    threadPool = ThreadPoolExecutor(max_workers=10, thread_name_prefix="gathering_algorithm")
    # pulsar init
    pulsar_get_client = pulsar_client.Get_Results(args.inputtopic)
    while True:
        try:
            message = pulsar_get_client.get_results()
            if message is not None:
                message_data = eval(message.data())
                # TODO: process message_data
                threadPool.submit(lambda cxp: algoritm_main(*cxp), (message_data, args.outputtopic))
            else:
                logger.info("message is None")
        except Exception as e:
            logger.info("error: {}".format(e))
            continue
    pulsar_get_client.close()