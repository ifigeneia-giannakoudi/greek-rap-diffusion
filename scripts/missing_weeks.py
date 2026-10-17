"""List the weekly chart files that are still missing."""
from pathlib import Path

import pandas as pd

CHART_DIR = Path("data/raw/charts")

# Every Thursday from the first chart week of 2020 until today

START_WEEK = "2020-03-05"   # first chart week: the week before COVID was declared a pandemic

expected = pd.date_range(START_WEEK, pd.Timestamp.today(), freq="W-THU")

have = {p.stem.removeprefix("regional-gr-weekly-") for p in CHART_DIR.glob("*.csv")}

missing = [d.strftime("%Y-%m-%d") for d in expected if d.strftime("%Y-%m-%d") not in have]

print(f"expected {len(expected)}, have {len(have)}, missing {len(missing)}")
for d in missing[:20]:
    print("  missing:", d)

