# build_phase1_manifest.py

import os
import csv
from typing import Optional
from dotenv import load_dotenv
from load_annotations import load_ssv2_annotations
from classify_label import get_phase1_category

load_dotenv()

ANNOTATIONS_PATH = os.getenv('ANNOTATIONS_PATH')
VIDEOS_DIR = os.getenv('VIDEOS_DIR')
OUTPUT_MANIFEST = os.getenv('OUTPUT_MANIFEST') 
assert ANNOTATIONS_PATH is not None
assert VIDEOS_DIR is not None
assert OUTPUT_MANIFEST is not None

def build_manifest():
    annotations = load_ssv2_annotations(ANNOTATIONS_PATH)
    rows = []

    for meta,video_id in annotations.items():
        label = meta["label"]
        phase1_category = get_phase1_category(label) 

        video_path = os.path.join(VIDEOS_DIR, f"{video_id}.webm") #type: ignore

        if not os.path.exists(video_path):
            continue  # skip missing files safely

        if phase1_category is None:
            rows.append({
                "video_id": video_id,
                "relative_path": video_path,
                "original_label": label,
                "phase1_category": "excluded",
                "included": "no",
                "exclusion_reason": "label_not_phase1"
            })
        else:
            rows.append({
                "video_id": video_id,
                "relative_path": video_path,
                "original_label": label,
                "phase1_category": phase1_category,
                "included": "yes",
                "exclusion_reason": ""
            })

    write_csv(rows)

def write_csv(rows):
    fieldnames = [
        "video_id",
        "relative_path",
        "original_label",
        "phase1_category",
        "included",
        "exclusion_reason"
    ]

    os.makedirs(os.path.dirname(OUTPUT_MANIFEST), exist_ok=True) #type: ignore

    with open(OUTPUT_MANIFEST, "w", newline="") as f: #type: ignore
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

if __name__ == "__main__":
    build_manifest()
