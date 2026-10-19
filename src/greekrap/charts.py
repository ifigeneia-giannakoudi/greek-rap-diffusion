"""Load weekly Spotify chart files and parse artist credits."""
import re
from pathlib import Path

import pandas as pd

FILE_PREFIX = "regional-gr-weekly-"
REQUIRED_COLUMNS = {"rank", "uri", "artist_names", "track_name", "streams"}

# Artist names that contain ", " and must not be split. Add to this when you find more.
COMPOUND_NAMES = {"Tyler, The Creator"}


def parse_artists(credit: str) -> list[str]:
    """Split a chart credit like "HermesHermes, BLVD" into a list of artist names."""
    if not isinstance(credit, str) or not credit.strip():
        return []

    # Protect names that contain ", " by temporarily swapping in a placeholder
    protected = {}
    for i, name in enumerate(COMPOUND_NAMES):
        if name in credit:
            key = f"__NAME{i}__"
            protected[key] = name
            credit = credit.replace(name, key)

    artists = []
    for part in credit.split(", "):
        part = protected.get(part.strip(), part.strip())   # swap placeholders back
        if part and part not in artists:                  # skip empties and duplicates
            artists.append(part)
    return artists


WEEK_FILE_PATTERN = re.compile(rf"^{FILE_PREFIX}(\d{{4}}-\d{{2}}-\d{{2}})$")


def week_from_filename(path) -> pd.Timestamp:
    """'regional-gr-weekly-2020-03-05.csv' -> Timestamp('2020-03-05')."""
    match = WEEK_FILE_PATTERN.match(Path(path).stem)
    if not match:
        raise ValueError(f"Unexpected chart file name (a duplicate download?): {path}")
    return pd.Timestamp(match.group(1))

def read_chart(path) -> pd.DataFrame:
    """Read one weekly chart CSV and add clean, typed columns."""
    chart = pd.read_csv(path)
    missing = REQUIRED_COLUMNS - set(chart.columns)
    if missing:
        raise ValueError(f"{path}: missing columns {sorted(missing)}")

    chart["week"] = week_from_filename(path)
    chart["streams"] = pd.to_numeric(chart["streams"]).astype("int64")
    chart["track_id"] = chart["uri"].str.split(":").str[-1]   # spotify:track:XXX -> XXX
    chart["artists"] = chart["artist_names"].map(parse_artists)
    return chart


def load_charts(folder) -> pd.DataFrame:
    """Read every weekly chart in `folder` into one table, sorted by week and rank."""
    files = sorted(Path(folder).glob(f"{FILE_PREFIX}*.csv"))
    if not files:
        raise FileNotFoundError(f"No chart files found in {folder}")

    charts = pd.concat([read_chart(f) for f in files], ignore_index=True)

    dupes = charts.duplicated(subset=["week", "rank"]).sum()
    if dupes:
        raise ValueError(f"{dupes} duplicate (week, rank) rows: is a week downloaded twice?")
    return charts.sort_values(["week", "rank"]).reset_index(drop=True)
