# config.py
import json
import os
from dotenv import load_dotenv
from typing import Dict, Any

load_dotenv()
CONFIG_FILE = os.getenv("CONFIG_FILE", "config.json")
WORKFLOWS_DIR = os.getenv("WORKFLOWS_DIR", "workflows")
SAVE_IMAGE_NODE_ID = int(os.getenv("SAVE_IMAGE_NODE_ID", "81"))
COMFYUI_BASE_URL = os.getenv("COMFYUI_BASE_URL", "http://localhost:8188")
APIKEY = os.getenv("APIKEY", "DidYouKnowThatVaporeon")

if not os.path.exists(CONFIG_FILE):
    raise FileNotFoundError(f"{CONFIG_FILE} not found. Please create it as per the instructions.")
with open(CONFIG_FILE, "r") as f:
    config: Dict[str, Any] = json.load(f)
supported_models = [m["id"] for m in config["models"]]

def parse_size(size_str: str) -> tuple[int, int]:
    w, h = map(int, size_str.split('x'))
    w = (w // 8) * 8
    h = (h // 8) * 8
    return w, h

def load_workflow(model_config: dict) -> dict:
    """Load the base workflow JSON and return the dict."""
    wf_file = model_config["workflow"]
    wf_path = os.path.join(WORKFLOWS_DIR, wf_file)
    if not os.path.exists(wf_path):
        raise FileNotFoundError(f"Workflow file {wf_path} not found.")
    with open(wf_path, "r") as f:
        return json.load(f)