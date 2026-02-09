# build_phase1_manifest.py
"""
Build Phase-1 manifest from Something-Something-v2 train.json + validation.json.

Outputs:
    preprocessing/manifests/phase1_train_manifest.csv (balanced train)
    preprocessing/manifests/phase1_val_manifest.csv (validation; untouched except classification)
    preprocessing/manifests/phase1_manifest.csv (combined)

Assumptions:
  - 20bn-something-something-download-package-labels/labels/train.json and 20bn-something-something-download-package-labels/labels/train.json exist (SSv2 split files)
  - video files are at research/20bn-something-something-v2/{id}.webm (we only record path; don't open videos)
"""

import os
import json
import random
from dotenv import load_dotenv
from collections import defaultdict
from typing import Optional, Dict, Tuple, List
import phase1_classes #same directory 
import pandas as pd

# ---------- CONFIG ----------
load_dotenv()
DATA_DIR = "preprocessing"
VIDEOS_DIR = os.getenv('VIDEOS_DIR')
TRAIN_JSON = os.getenv('TRAIN_JSON')
VAL_JSON = os.getenv('VAL_JSON')
MANIFEST_DIR = os.path.join(DATA_DIR, "manifests")
os.makedirs(MANIFEST_DIR, exist_ok=True)

#Asserting multiple variables to be not None, if not true, will raise an AssertionError
assert all(v is not None for v in [VIDEOS_DIR, TRAIN_JSON, VAL_JSON]), "One or more variables are None"

RANDOM_SEED = 42
random.seed(RANDOM_SEED)

# ---------- Pair definitions to balance (normalize these keys) ----------
# Map canonical normalized template => (pair_name, side)
# We'll define canonical normalized strings matching our normalization function below.
# For example: normalize("Pushing [something] from left to right") -> "pushing something from left to right"
PAIR_DEFINITIONS = [
    # directional L/R
    ("pushing something from left to right", "pushing something from right to left"),
    ("pulling something from left to right", "pulling something from right to left"),
    ("moving something up", "moving something down"),
    ("moving something towards the camera", "moving something away from the camera"),
    ("moving something closer to something", "moving something away from something"),
    # moving pair for objects approaching/away from each other
    ("moving something and something closer to each other", "moving something and something away from each other"),
    # 'pass each other' has no direct symmetric inverse, we skip balancing it
    # reversible state pairs
    ("opening something", "closing something"),
    ("folding something", "unfolding something"),
    ("covering something with something", "uncovering something"),
    ("putting something into something", "pulling something out of something"),  # approximate inverse
    # terminal completion pair:
    ("pretending to put something onto something", "putting something onto something"),
]

# ---------- Helper utilities ----------
def normalize_template(template: str) -> str:
    """
    Normalize SSv2 template strings to a canonical lowercase form for matching.

    Examples:
      "Pushing [something] from left to right" -> "pushing something from left to right"
      "Putting [something] into [something]" -> "putting something into something"
    """
    if template is None:
        return ""
    s = template.lower().strip()
    # remove square brackets, replace with nothing
    s = s.replace("[", "").replace("]", "")
    # replace repeated spaces
    s = " ".join(s.split())
    # ensure token "something" exists where placeholders were removed
    # SSv2 templates use [something], [number of], etc. We leave tokens as-is.
    return s

def build_lookup_from_phase1_classes(phase1_classes: Dict[str, set]) -> Dict[str, Tuple[str,str]]:
    """
    Build mapping: normalized_template -> (category, canonical_template)
    """
    lookup = {}
    for cat, templates in phase1_classes.items():
        for t in templates:
            norm = normalize_template(t)
            lookup[norm] = (cat, t)
    return lookup

LOOKUP = build_lookup_from_phase1_classes(phase1_classes.PHASE1_CLASSES)

def read_split_json(path: str) -> List[Dict]:
    with open(path, "r", encoding="utf8") as f:
        data = json.load(f)
    # SSv2 splits are lists of entries
    return data

# ---------- Core: build the raw manifest (no balancing yet) ----------
def build_raw_manifest(splits: Dict[str, str]) -> pd.DataFrame:
    """
    splits: dict mapping split_name -> path_to_json (e.g. {"train": TRAIN_JSON, "validation": VAL_JSON})
    Returns DataFrame with rows for all videos in those splits, columns:
      video_id, relative_path, split, template, template_norm, phase1_category, included, exclusion_reason, derived_from, is_derived
    """
    rows = []
    for split_name, json_path in splits.items():
        entries = read_split_json(json_path)
        for entry in entries:
            vid = str(entry.get("id"))
            template_raw = entry.get("template") or entry.get("label") or ""
            template_norm = normalize_template(template_raw)
            mapping = LOOKUP.get(template_norm)
            if mapping is None:
                category = "excluded"
                exclusion_reason = "label_not_phase1"
            else:
                category = mapping[0]
                exclusion_reason = ""

            video_relpath = os.path.join(VIDEOS_DIR, f"{vid}.webm") #type: ignore
            # existing files may be elsewhere; we still record relative path
            rows.append({
                "video_id": vid,
                "relative_path": video_relpath,
                "split": split_name,
                "template": template_raw,
                "template_norm": template_norm,
                "phase1_category": category,
                "included": "yes" if category != "excluded" else "no",
                "exclusion_reason": exclusion_reason,
                "derived_from": "",
                "is_derived": False,
            })
    df = pd.DataFrame(rows)
    return df

# ---------- Balancing logic ----------
def downsample_to_balance_pairs(df: pd.DataFrame, pairs: List[Tuple[str,str]], split: str = "train", seed: int = RANDOM_SEED) -> pd.DataFrame:
    """
    For each pair (side_a_norm, side_b_norm) in pairs:
      - consider only rows in df with split==split
      - if both sides exist, downsample the larger side to match the smaller side
    Returns a new DataFrame where the training split has been downsampled accordingly.
    Validation split is not touched.
    """
    df_out = df.copy()
    rng = random.Random(seed)

    # index rows by template_norm for quick selection
    for side_a, side_b in pairs:
        mask_a = (df_out["split"] == split) & (df_out["template_norm"] == side_a) & (df_out["included"] == "yes")
        mask_b = (df_out["split"] == split) & (df_out["template_norm"] == side_b) & (df_out["included"] == "yes")

        ids_a = df_out[mask_a]["video_id"].tolist()
        ids_b = df_out[mask_b]["video_id"].tolist()

        if len(ids_a) == 0 or len(ids_b) == 0:
            # nothing to balance for this pair
            continue

        # choose smaller size
        target = min(len(ids_a), len(ids_b))
        # downsample both sides to target (this ensures strict equality)
        if len(ids_a) > target:
            drop_a = set(rng.sample(ids_a, len(ids_a) - target))
        else:
            drop_a = set()
        if len(ids_b) > target:
            drop_b = set(rng.sample(ids_b, len(ids_b) - target))
        else:
            drop_b = set()

        # mark dropped rows as excluded (or set included=no with reason)
        if drop_a:
            df_out.loc[df_out["video_id"].isin(drop_a) & (df_out["template_norm"] == side_a), "included"] = "no"
            df_out.loc[df_out["video_id"].isin(drop_a) & (df_out["template_norm"] == side_a), "exclusion_reason"] = "downsampled_for_pair_balance"
        if drop_b:
            df_out.loc[df_out["video_id"].isin(drop_b) & (df_out["template_norm"] == side_b), "included"] = "no"
            df_out.loc[df_out["video_id"].isin(drop_b) & (df_out["template_norm"] == side_b), "exclusion_reason"] = "downsampled_for_pair_balance"

    return df_out

# ---------- Main pipeline ----------
def main():
    splits = {"train": TRAIN_JSON, "validation": VAL_JSON}
    print("Loading splits:", splits)
    df = build_raw_manifest(splits) #type: ignore
    print("Total entries found:", len(df))

    # Quick statistics before balancing
    print("Phase1 categories distribution (pre-balance):")
    print(df[df["included"]=="yes"]["phase1_category"].value_counts())

    # Show top directional templates counts pre-balance
    print("\nTop templates counts (pre-balance):")
    print(df[df["included"]=="yes"]["template_norm"].value_counts().head(30))

    # Apply pair balancing only to train split
    df_bal = downsample_to_balance_pairs(df, PAIR_DEFINITIONS, split="train", seed=RANDOM_SEED)

    # Post-balance stats
    print("\nPhase1 categories distribution (post-balance, train only modified):")
    print(df_bal[df_bal["included"]=="yes"]["phase1_category"].value_counts())

    # Save manifests
    train_out = os.path.join(MANIFEST_DIR, "phase1_train_manifest.csv")
    val_out = os.path.join(MANIFEST_DIR, "phase1_val_manifest.csv")
    combined_out = os.path.join(MANIFEST_DIR, "phase1_manifest.csv")

    df_bal[df_bal["split"] == "train"].to_csv(train_out, index=False)
    df_bal[df_bal["split"] == "validation"].to_csv(val_out, index=False)
    df_bal.to_csv(combined_out, index=False)

    print(f"\nManifests written to:\n  {train_out}\n  {val_out}\n  {combined_out}")

if __name__ == "__main__":
    main()
