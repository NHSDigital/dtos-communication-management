import os
import sys

if "function_app" in sys.modules:
    del sys.modules["function_app"]

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(SCRIPT_DIR) + "/../src/functions/notify/")
sys.path.insert(0, os.path.dirname(SCRIPT_DIR) + "/../src/shared/")
