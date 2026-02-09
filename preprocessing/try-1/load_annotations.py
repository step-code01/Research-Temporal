# load_annotations.py

import json

def load_ssv2_annotations(path):
    with open(path, "r") as f:
        data = json.load(f)
    return data
