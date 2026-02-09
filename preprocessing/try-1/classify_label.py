# classify_label.py

from phase1_classes import PHASE1_CLASSES

def get_phase1_category(label: str):
    for category, labels in PHASE1_CLASSES.items():
        if label in labels:
            return category
    return None
