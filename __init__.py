import os
import configparser
from utils import logs

logger = logs.Log("fall_down_algorithm").logs_setup()
path = os.path.abspath(".")
config_path = os.path.join(path, 'configs', 'config.ini')
config = configparser.ConfigParser()
config.read(config_path,encoding='utf-8')