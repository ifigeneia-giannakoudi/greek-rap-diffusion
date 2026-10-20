"""Create labels/artists.csv: one row per chart artist, sorted by streams, ready to label.

Run once. It never overwrites an existing labels file.
"""

from pathlib import Path

import pandas as pd

CHARTS = Path("data/processed/charts.parquet")
OUT = Path("labels/artists.csv")

# One-time migration of decisions made during the feasibility check (Oct 18-19)
HIPHOP_NAMES = {
    "Bloody Hawk", "LEX", "Novel 729", "Logos Timis", "Anser", "Buzz", "Zoro", "Wang",
    "Sadam", "Mateos Nps", "Dani Gambino", "Jaul", "Stixoima", "Ethismos", "Tzamal",
    "Zinon", "Above The Hood", "Negros Tou Moria", "Mani", "Beats Pliz",
    "Sativa", "SativaMusic", "Eleuthero Pneuma", "Koraki", "Sadomas", "Tsaki",
    "12os Pithikos", "Melow", "TSE", "Immune", "HGEMONA$", "MK", "Mente Fuerte",
    "Iratus", "Mikros Kleftis", "Fi Vita Sigma", "Lobo", "Zoro&Buzz",
    "Goin' Through", "Stavento", "Giorgos Orfanidis",
}
IN_BETWEEN = {"RACK", "Hawk", "TOQUEL", "Saske", "Light", "Dof Twogee", "SNIK"}
ALIASES = {"SativaMusic": "Sativa"}   # name in the charts -> canonical artist

if OUT.exists():
    raise SystemExit(f"{OUT} already exists: not overwriting your labels.")

charts = pd.read_parquet(CHARTS)

# Streams per artist name (a song with 3 artists counts for each of them)
per_credit = charts.explode("artists")
stats = (per_credit.groupby("artists")
         .agg(streams_total=("streams", "sum"),
              first_week=("week", "min"),
              last_week=("week", "max"))
         .sort_values("streams_total", ascending=False))

# How many artists cover most of the chart? (decides how far down to label)
cum_share = 100 * stats["streams_total"].cumsum() / stats["streams_total"].sum()
for target in (80, 90, 95):
    n_artists = int((cum_share < target).sum()) + 1
    print(f"{n_artists:>5} artists cover {target}% of artist-credited streams")


def initial_style(name: str) -> str:
    if name in HIPHOP_NAMES:
        return "hip-hop"
    if name in IN_BETWEEN:
        return "in-between"
    return ""                      # not labelled yet


labels = pd.DataFrame({"name": stats.index})
labels["canonical"] = labels["name"].map(lambda n: ALIASES.get(n, n))
labels["style"] = labels["name"].map(initial_style)
labels["note"] = labels["style"].map(lambda s: "feasibility check, Oct 18-19" if s else "")
labels["note"] = labels["note"].where(~labels["name"].isin(ALIASES), "alias of Sativa")
labels["streams_total"] = stats["streams_total"].values
labels["first_week"] = stats["first_week"].dt.strftime("%Y-%m-%d").values
labels["last_week"] = stats["last_week"].dt.strftime("%Y-%m-%d").values

OUT.parent.mkdir(parents=True, exist_ok=True)
labels.to_csv(OUT, index=False, encoding="utf-8")
print(f"\nWrote {len(labels)} artists to {OUT}; "
      f"{(labels['style'] != '').sum()} already labelled")
