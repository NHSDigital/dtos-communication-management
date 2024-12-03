import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Import order is important here as we need to load the message status function_app module first.
sys.path.insert(0, os.path.dirname(SCRIPT_DIR) + "/../src/functions/message_status/")
sys.path.insert(0, os.path.dirname(SCRIPT_DIR) + "/../src/functions/notify/")
sys.path.insert(0, os.path.dirname(SCRIPT_DIR) + "/../src/shared/")
