"""Feasibility check: how often do hip-hop-style artists appear in the Greek charts?

Step 1: find how each artist is spelled in the data, and save all artist names.
Step 2: hip-hop's presence in the Top 200, year by year.
Step 3: who carries hip-hop's share (release-cycle hypothesis).
Step 4: pure hip-hop vs hip-hop collaborating with in-between / trap artists.
Step 5: newcomers since 2025 not yet labelled (recall-bias check).
"""

import unicodedata
from pathlib import Path

import pandas as pd

CHART_DIR = Path("data/raw/charts")
OUT_FILE = Path("data/processed/all_artist_names.txt")

# ---------------------------------------------------------------
# Step 1: how are the artists spelled in the data?
# ---------------------------------------------------------------
# Lower-case search keywords (accents and case are ignored when matching)
HIPHOP = [
    "bloody hawk", "lex", "novel 729", "logos timis", "vevilos", "anser", "buzz", "zoro",
    "wang", "sadam", "mateos", "dani gambino", "jaul", "stixoima", "ethismos", "tzamal",
    "zinon", "above the hood", "negros tou moria", "bong da city", "mani",
    "beats pliz", "sativa", "eleuthero pneuma", "koraki", "xplicit", "sadomas", "δπθ",
    "rationalistas", "taf lathos", "tsaki", "pithikos", "melow", "tse", "stolen mic",
    "immune", "hgemona$", "mk", "mente fuerte",
]
# From the scene's history (Wikipedia, LiFO, Reader): Latin and Greek spellings
HIPHOP_90S = [
    "active member", "foxmoor", "ff.c", "terror x crew", "txc", "zontanoi nekroi",
    "ζωντανοί νεκροί", "zn", "paremvoles", "παρεμβολές", "nebma", "νεβμα", "o.p.a.",
]
HIPHOP_2000S = [
    "alfa gama", "άλφα γάμα", "vitapeis", "βήταπεις", "voreia asteria", "βόρεια αστέρια",
    "g.i.ant.s", "flowjob", "united crew", "rns", "yonka mayonka", "iratus", "tiny jackal",
    "mikros kleftis", "μικρός κλέφτης", "logos apeili", "λόγος απειλή", "rapsodos filologos",
    "ραψωδός φιλόλογος", "social waste", "fvs", "fi vita sigma",
]
HIPHOP_NEW_GEN = [
    "mr.yo", "skiahtro", "σκιάχτρο", "katholou crew", "rammenos assos", "ραμμένος άσσος",
    "zafko", "los hermanos", "expend flow", "lobo", "fer de lance", "obnoxious kas",
    "poetic", "tropeau roman", "zoro&buzz",
]
# Part of the history, but satirical or commercial: decide later if they count
SATIRICAL_COMMERCIAL = [
    "imiskoumbria", "ημισκούμπρια", "vavilona", "βαβυλώνα", "la klikaria",
    "goin' through", "goin through", "stavento", "paidi thavma", "παιδί θαύμα",
]
# In-between / trap-leaning artists (they only count together with a hip-hop artist)
MIXED = ["rack", "hawk", "toquel", "saske", "light", "dof twogee", "snik"]


def normalise(text: str) -> str:
    """Lower-case, remove accents and unify final sigma: 'Παρεμβολές' == 'ΠΑΡΕΜΒΟΛΕΣ'."""
    decomposed = unicodedata.normalize("NFD", text.lower())
    no_accents = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    return no_accents.replace("ς", "σ")


def matches(keyword: str, name: str) -> bool:
    """Short keywords must equal the whole name; longer ones may appear inside it."""
    keyword, name = normalise(keyword), normalise(name)
    return name == keyword or (len(keyword) >= 5 and keyword in name)


# Read all weekly files into one table, adding the week from the file name
frames = []
for path in sorted(CHART_DIR.glob("regional-gr-weekly-*.csv")):
    week = pd.read_csv(path)
    week["week"] = pd.to_datetime(path.stem.removeprefix("regional-gr-weekly-"))
    frames.append(week)
charts = pd.concat(frames, ignore_index=True)

# Split each credit into a list of names (a quick version; the tested parser comes later)
charts["artist_list"] = charts["artist_names"].str.split(", ")

all_names = sorted(set(charts["artist_list"].explode().dropna()))
print(f"{len(charts)} chart rows, {len(all_names)} distinct artist names")

for group, keywords in [("HIPHOP", HIPHOP), ("HIPHOP 90s", HIPHOP_90S),
                        ("HIPHOP 2000s", HIPHOP_2000S), ("HIPHOP new gen", HIPHOP_NEW_GEN),
                        ("SATIRICAL/COMMERCIAL", SATIRICAL_COMMERCIAL), ("MIXED", MIXED)]:
    print(f"\n=== {group} ===")
    for kw in keywords:
        found = [name for name in all_names if matches(kw, name)]
        print(f"{kw!r}: {found if found else '-- not found --'}")

OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
OUT_FILE.write_text("\n".join(all_names) + "\n", encoding="utf-8")
print(f"\nSaved {len(all_names)} names to {OUT_FILE}")

# ---------------------------------------------------------------
# Step 2: hip-hop's presence in the charts, year by year
# ---------------------------------------------------------------
# Exact spellings as they appear in the charts (add found historic names here)
HIPHOP_NAMES = {
    # Your original list (found in the charts)
    "Bloody Hawk", "LEX", "Novel 729", "Logos Timis", "Anser", "Buzz", "Zoro", "Wang",
    "Sadam", "Mateos Nps", "Dani Gambino", "Jaul", "Stixoima", "Ethismos", "Tzamal",
    "Zinon", "Above The Hood", "Negros Tou Moria", "Mani", "Beats Pliz",
    "Sativa", "SativaMusic", "Eleuthero Pneuma", "Koraki", "Sadomas", "Tsaki",
    "12os Pithikos", "Melow", "TSE", "Immune", "HGEMONA$", "MK", "Mente Fuerte",
    # From the scene's history (found in the charts)
    "Iratus", "Mikros Kleftis", "Fi Vita Sigma", "Lobo", "Zoro&Buzz",
    "Goin' Through", "Stavento",
    # Found through collaborations
    "Giorgos Orfanidis",
}
# Defined once, used everywhere below
IN_BETWEEN = {"RACK", "Hawk", "TOQUEL", "Saske", "Light", "Dof Twogee", "SNIK"}

overlap = HIPHOP_NAMES & IN_BETWEEN
assert not overlap, f"Names in both HIPHOP_NAMES and IN_BETWEEN: {overlap}"


def credits_any(names, group) -> bool:
    """True if any credited artist is in the group."""
    return isinstance(names, list) and any(n in group for n in names)


charts["streams"] = pd.to_numeric(charts["streams"], errors="coerce")
charts["year"] = charts["week"].dt.year
charts["hiphop"] = charts["artist_list"].apply(credits_any, group=HIPHOP_NAMES)
charts["hiphop_lead"] = charts["artist_list"].apply(
    lambda names: isinstance(names, list) and names[0] in HIPHOP_NAMES)
charts["in_between_only"] = (~charts["hiphop"]
                             & charts["artist_list"].apply(credits_any, group=IN_BETWEEN))
charts["hiphop_streams"] = charts["streams"].where(charts["hiphop"], 0)

yearly = charts.groupby("year").agg(
    weeks=("week", "nunique"),
    hiphop_entries=("hiphop", "sum"),
    lead_entries=("hiphop_lead", "sum"),
    in_between_entries=("in_between_only", "sum"),
    hiphop_streams=("hiphop_streams", "sum"),
    all_streams=("streams", "sum"),
)
# Normalise: partial years (2020 from March, 2026 until October) must not look smaller
yearly["hiphop_per_week"] = (yearly["hiphop_entries"] / yearly["weeks"]).round(1)
yearly["lead_per_week"] = (yearly["lead_entries"] / yearly["weeks"]).round(1)
yearly["in_between_only_per_week"] = (yearly["in_between_entries"] / yearly["weeks"]).round(1)
yearly["hiphop_stream_%"] = (100 * yearly["hiphop_streams"] / yearly["all_streams"]).round(1)

print("\n=== Hip-hop in the Top 200, per year ===")
print(yearly[["weeks", "hiphop_per_week", "lead_per_week",
              "in_between_only_per_week", "hiphop_stream_%"]])

# ---------------------------------------------------------------
# Step 3: who carries hip-hop's share? (release-cycle hypothesis)
# ---------------------------------------------------------------
total_by_year = charts.groupby("year")["streams"].sum()
BIG_FOUR = {"LEX", "Bloody Hawk", "Novel 729", "Logos Timis"}


def stream_share(mask):
    """Percent of all chart streams per year from the rows where mask is True."""
    return (100 * charts["streams"].where(mask, 0).groupby(charts["year"]).sum()
            / total_by_year).round(1)


# One row per (chart entry, credited artist)
per_credit = charts.explode("artist_list")
hh = per_credit[per_credit["artist_list"].isin(HIPHOP_NAMES)]
per_artist = hh.groupby(["year", "artist_list"])["streams"].sum().unstack("year")
share = (100 * per_artist / total_by_year).round(1).fillna(0)
top10 = share.sum(axis=1).sort_values(ascending=False).head(10).index
print("\n=== Top 10 hip-hop artists: % of all chart streams, per year ===")
print(share.loc[top10])

charts["hiphop_rest"] = charts["artist_list"].apply(credits_any, group=HIPHOP_NAMES - BIG_FOUR)
print("\n=== Hip-hop stream share: all vs without the big four ===")
print(pd.DataFrame({
    "all_hiphop_%": stream_share(charts["hiphop"]),
    "without_big_four_%": stream_share(charts["hiphop_rest"]),
}))

# ---------------------------------------------------------------
# Step 4: pure hip-hop vs hip-hop collaborating with in-between artists
# ---------------------------------------------------------------
charts["with_in_between"] = charts["artist_list"].apply(credits_any, group=IN_BETWEEN)
charts["with_big_four"] = charts["artist_list"].apply(credits_any, group=BIG_FOUR)
charts["pure_hiphop"] = charts["hiphop"] & ~charts["with_in_between"]
charts["hiphop_collab"] = charts["hiphop"] & charts["with_in_between"]

print("\n=== Hip-hop stream share (%), split by who is credited ===")
print(pd.DataFrame({
    "all_hiphop": stream_share(charts["hiphop"]),
    "pure_hiphop": stream_share(charts["pure_hiphop"]),
    "hiphop_x_in_between": stream_share(charts["hiphop_collab"]),
    "pure_without_big_four": stream_share(charts["pure_hiphop"] & ~charts["with_big_four"]),
}))

# Per-artist shares, pure hip-hop songs only (re-explode so the new columns are included)
per_credit = charts.explode("artist_list")
pure = per_credit[per_credit["pure_hiphop"] & per_credit["artist_list"].isin(HIPHOP_NAMES)]
pure_share = (100 * pure.groupby(["year", "artist_list"])["streams"].sum().unstack("year")
              / total_by_year).round(1).fillna(0)
top10_pure = pure_share.sum(axis=1).sort_values(ascending=False).head(10).index
print("\n=== Top 10 artists, pure hip-hop songs only (% of all chart streams) ===")
print(pure_share.loc[top10_pure])

# ---------------------------------------------------------------
# Step 5: newcomers since 2025 that are in neither list (recall-bias check)
# ---------------------------------------------------------------
artist_stats = per_credit.groupby("artist_list").agg(
    first_week=("week", "min"),          # first week the artist appears in the chart
    streams=("streams", "sum"),          # streams of all songs crediting them
    chart_weeks=("week", "nunique"),     # how many weeks they were in the chart
)
newcomers = artist_stats[(artist_stats["first_week"] >= "2025-01-01")
                         & ~artist_stats.index.isin(HIPHOP_NAMES | IN_BETWEEN)]
print(f"\n=== {len(newcomers)} artists first charting since 2025 (not yet labelled) ===")
print(newcomers.sort_values("streams", ascending=False).head(40).to_string())
