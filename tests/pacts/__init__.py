import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(SCRIPT_DIR) + "/../src/functions/process_pilot_data/")
sys.path.insert(0, os.path.dirname(SCRIPT_DIR) + "/../src/functions/notify/")