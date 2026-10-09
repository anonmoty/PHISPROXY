import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(ROOT, "templates")
LOG_DIR = os.path.join(ROOT, "logs")
CAPTURE_FILE = os.path.join(LOG_DIR, "captured.json")
HOST = "0.0.0.0"
PORT = 8080
