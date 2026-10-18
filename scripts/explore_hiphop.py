"""Feasibility check: how often do hip-hop-style artists appear in the Greek charts?

Step 1: find how each artist is spelled in the data, and save all artist names.
"""

from pathlib import Path

import pandas as pd

CHART_DIR = Path("data/raw/charts")
OUT_FILE = Path("data/processed/all_artist_names.txt")

# Artists that are mostly hip-hop style (lower-case keywords)
HIPHOP = [
    "bloody hawk", "lex", "novel 729", "logos timis", "vevilos", "anser", "buzz", "zoro",
    "wang", "sadam", "mateos", "dani gambino", "jaul", "stixoima", "ethismos", "tzamal",
    "zinon", "above the hood", "negros tou moria", "dof twogee", "bong da city", "mani",
    "beats pliz", "sativa", "eleuthero pneuma", "koraki", "xplicit", "sadomas", "δπθ",
    "rationalistas", "taf lathos", "tsaki", "pithikos", "melow", "tse", "stolen mic",
    "immune", "hgemona$", "saske", "mk",
]
# Artists who switch between trap and hip-hop: to be labelled track by track later
MIXED = ["rack", "hawk", "toquel", "mente fuerte"]


def matches(keyword: str, name: str) -> bool:
    """Short keywords must equal the whole name; longer ones may appear inside it."""
    name = name.lower()
    return name == keyword or (len(keyword) >= 5 and keyword in name)


# 1. Read all weekly files into one table, adding the week from the file name
frames = []
for path in sorted(CHART_DIR.glob("regional-gr-weekly-*.csv")):
    week = pd.read_csv(path)
    week["week"] = pd.to_datetime(path.stem.removeprefix("regional-gr-weekly-"))
    frames.append(week)
charts = pd.concat(frames, ignore_index=True)

# 2. Split each credit into a list of names (a quick version; the tested parser comes later)
charts["artist_list"] = charts["artist_names"].str.split(", ")

# 3. Every distinct artist name in the charts
all_names = sorted(set(charts["artist_list"].explode().dropna()))
print(f"{len(charts)} chart rows, {len(all_names)} distinct artist names")

# 4. How is each keyword spelled in the data?
for group, keywords in [("HIPHOP", HIPHOP), ("MIXED", MIXED)]:
    print(f"\n=== {group} ===")
    for kw in keywords:
        found = [name for name in all_names if matches(kw, name)]
        print(f"{kw!r}: {found if found else '-- not found --'}")

# 5. Save every artist name, one per line, to scan for Greek spellings and missed names
OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
OUT_FILE.write_text("\n".join(all_names) + "\n", encoding="utf-8")
print(f"\nSaved {len(all_names)} names to {OUT_FILE}")




# ---------------------------------------------------------------
# Step 2: hip-hop's presence in the charts, year by year
# ---------------------------------------------------------------
HIPHOP_NAMES = {
    "Bloody Hawk", "LEX", "Novel 729", "Logos Timis", "Anser", "Buzz", "Zoro", "Wang",
    "Sadam", "Mateos Nps", "Dani Gambino", "Jaul", "Stixoima", "Ethismos", "Tzamal",
    "Zinon", "Above The Hood", "Negros Tou Moria", "Dof Twogee", "Mani", "Beats Pliz",
    "Sativa", "SativaMusic", "Eleuthero Pneuma", "Koraki", "Sadomas", "Tsaki",
    "12os Pithikos", "Melow", "TSE", "Immune", "HGEMONA$", "Saske", "MK",
}
MIXED_NAMES = {"RACK", "Hawk", "TOQUEL", "Mente Fuerte"}


def credits_any(names, group) -> bool:
    """True if any credited artist is in the group."""
    return isinstance(names, list) and any(n in group for n in names)


charts["streams"] = pd.to_numeric(charts["streams"], errors="coerce")
charts["year"] = charts["week"].dt.year
charts["hiphop"] = charts["artist_list"].apply(credits_any, group=HIPHOP_NAMES)
charts["hiphop_lead"] = charts["artist_list"].apply(
    lambda names: isinstance(names, list) and names[0] in HIPHOP_NAMES)
charts["mixed_only"] = (~charts["hiphop"]
                        & charts["artist_list"].apply(credits_any, group=MIXED_NAMES))
charts["hiphop_streams"] = charts["streams"].where(charts["hiphop"], 0)

yearly = charts.groupby("year").agg(
    weeks=("week", "nunique"),
    hiphop_entries=("hiphop", "sum"),
    lead_entries=("hiphop_lead", "sum"),
    mixed_entries=("mixed_only", "sum"),
    hiphop_streams=("hiphop_streams", "sum"),
    all_streams=("streams", "sum"),
)
# Normalise: partial years (2020 from March, 2026 until October) must not look smaller
yearly["hiphop_per_week"] = (yearly["hiphop_entries"] / yearly["weeks"]).round(1)
yearly["lead_per_week"] = (yearly["lead_entries"] / yearly["weeks"]).round(1)
yearly["mixed_per_week"] = (yearly["mixed_entries"] / yearly["weeks"]).round(1)
yearly["hiphop_stream_%"] = (100 * yearly["hiphop_streams"] / yearly["all_streams"]).round(1)

print("\n=== Hip-hop in the Top 200, per year ===")
print(yearly[["weeks", "hiphop_per_week", "lead_per_week", "mixed_per_week", "hiphop_stream_%"]])

# ---------------------------------------------------------------
# Step 3: who carries hip-hop's share? (release-cycle hypothesis)
# ---------------------------------------------------------------
total_by_year = charts.groupby("year")["streams"].sum()

# One row per (chart entry, credited artist)
per_credit = charts.explode("artist_list")
hh = per_credit[per_credit["artist_list"].isin(HIPHOP_NAMES)]

# Each hip-hop artist's share of all chart streams, per year (songs they are credited on)
per_artist = hh.groupby(["year", "artist_list"])["streams"].sum().unstack("year")
share = (100 * per_artist / total_by_year).round(1).fillna(0)
top10 = share.sum(axis=1).sort_values(ascending=False).head(10).index
print("\n=== Top 10 hip-hop artists: % of all chart streams, per year ===")
print(share.loc[top10])

# Hip-hop share with and without the four big names
BIG_FOUR = {"LEX", "Bloody Hawk", "Novel 729", "Logos Timis"}
charts["hiphop_rest"] = charts["artist_list"].apply(credits_any, group=HIPHOP_NAMES - BIG_FOUR)
rest_share = 100 * charts["streams"].where(charts["hiphop_rest"], 0).groupby(charts["year"]).sum()
print("\n=== Hip-hop stream share: all vs without the big four ===")
print(pd.DataFrame({
    "all_hiphop_%": yearly["hiphop_stream_%"],
    "without_big_four_%": (rest_share / total_by_year).round(1),
}))


# ---------------------------------------------------------------
# Step 4: pure hip-hop vs hip-hop collaborating with in-between / trap stars
# ---------------------------------------------------------------
IN_BETWEEN = {"RACK", "Light", "SNIK", "Hawk", "TOQUEL", "Mente Fuerte"}

charts["with_in_between"] = charts["artist_list"].apply(credits_any, group=IN_BETWEEN)
charts["with_big_four"] = charts["artist_list"].apply(credits_any, group=BIG_FOUR)
charts["pure_hiphop"] = charts["hiphop"] & ~charts["with_in_between"]
charts["hiphop_collab"] = charts["hiphop"] & charts["with_in_between"]


def stream_share(mask):
    """Percent of all chart streams per year from the rows where mask is True."""
    return (100 * charts["streams"].where(mask, 0).groupby(charts["year"]).sum()
            / total_by_year).round(1)


print("\n=== Hip-hop stream share (%), split by who is credited ===")
print(pd.DataFrame({
    "all_hiphop": stream_share(charts["hiphop"]),
    "pure_hiphop": stream_share(charts["pure_hiphop"]),
    "hiphop_x_in_between": stream_share(charts["hiphop_collab"]),
    "pure_without_big_four": stream_share(charts["pure_hiphop"] & ~charts["with_big_four"]),
}))

# Per-artist shares, pure hip-hop songs only
per_credit = charts.explode("artist_list")
pure = per_credit[per_credit["pure_hiphop"] & per_credit["artist_list"].isin(HIPHOP_NAMES)]
pure_share = (100 * pure.groupby(["year", "artist_list"])["streams"].sum().unstack("year")
              / total_by_year).round(1).fillna(0)
top10_pure = pure_share.sum(axis=1).sort_values(ascending=False).head(10).index
print("\n=== Top 10 artists, pure hip-hop songs only (% of all chart streams) ===")
print(pure_share.loc[top10_pure])
