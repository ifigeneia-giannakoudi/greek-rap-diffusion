"""Load and validate the hand-made artist labels (labels/artists.csv)."""

import pandas as pd

STYLES = {"hip-hop", "in-between", "trap", "pop", "laiko", "international", "other"}
ROLES = {"artist", "producer"}
REQUIRED_COLUMNS = ["name", "canonical", "style", "role", "note"]


def load_labels(path) -> pd.DataFrame:
    """Read the labels file, clean whitespace, and fail loudly on invalid values."""
    # dtype=str + keep_default_na=False: empty cells stay "" and no name becomes NaN
    labels = pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8")

    missing = set(REQUIRED_COLUMNS) - set(labels.columns)
    if missing:
        raise ValueError(f"labels file is missing columns: {sorted(missing)}")

    for col in REQUIRED_COLUMNS:
        labels[col] = labels[col].str.strip()

    bad_styles = set(labels["style"]) - STYLES - {""}
    if bad_styles:
        raise ValueError(f"unknown style values: {sorted(bad_styles)} (allowed: {sorted(STYLES)})")

    bad_roles = set(labels["role"]) - ROLES
    if bad_roles:
        raise ValueError(f"unknown role values: {sorted(bad_roles)} (allowed: {sorted(ROLES)})")

    dupes = labels.loc[labels["name"].duplicated(), "name"]
    if not dupes.empty:
        raise ValueError(f"names listed more than once: {sorted(dupes)}")

    # An empty canonical means the name is its own canonical artist
    no_canonical = labels["canonical"] == ""
    labels.loc[no_canonical, "canonical"] = labels.loc[no_canonical, "name"]
    return labels
