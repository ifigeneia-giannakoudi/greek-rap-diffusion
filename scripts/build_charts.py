"""Build data/processed/charts.parquet from all weekly chart CSVs, with sanity checks."""

from pathlib import Path

import pandas as pd

from greekrap.charts import load_charts

RAW_DIR = Path("data/raw/charts")
OUT = Path("data/processed/charts.parquet")
START_WEEK = "2020-03-05"

charts = load_charts(RAW_DIR)

# Sanity checks on the real data
expected_weeks = pd.date_range(START_WEEK, charts["week"].max(), freq="W-THU")
assert charts["week"].nunique() == len(expected_weeks), "some weeks are missing"
# Spotify's published chart skips one rank in these weeks (file is complete, rank absent)
KNOWN_MISSING_RANKS = {"2024-05-30": 149, "2026-07-16": 154}

for week, ranks in charts.groupby("week")["rank"]:
    expected = set(range(1, 201))
    known_gap = KNOWN_MISSING_RANKS.get(week.strftime("%Y-%m-%d"))
    if known_gap:
        expected.discard(known_gap)
    assert set(ranks) == expected, f"{week.date()}: ranks differ from 1-200 (known gap: {known_gap})"
assert (charts["streams"] > 0).all(), "found zero or negative streams"
assert charts["artists"].map(len).min() >= 1, "found a song with no artists"

OUT.parent.mkdir(parents=True, exist_ok=True)
charts.to_parquet(OUT, index=False)

print(f"Saved {len(charts):,} rows, {charts['week'].nunique()} weeks, "
      f"{charts['track_id'].nunique():,} distinct tracks to {OUT}")
