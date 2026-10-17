"""List every song that reached #1 on the Greek weekly chart, once each, in order."""

from pathlib import Path

import pandas as pd

CHART_DIR = Path("data/raw/charts")
OUT_DIR = Path("data/processed")

# 1. Collect the #1 song of every week
rows = []
for path in sorted(CHART_DIR.glob("regional-gr-weekly-*.csv")):   # sorted = chronological
    chart = pd.read_csv(path)
    top = chart.loc[chart["rank"] == 1].iloc[0]
    rows.append({
        "week": path.stem.removeprefix("regional-gr-weekly-"),
        "artists": top["artist_names"],
        "track": top["track_name"],
        "uri": top["uri"],
    })
number_ones = pd.DataFrame(rows)



# 2. Identify each song by title + artists (the same song can have several Spotify IDs)
def song_key(row):
    artists = sorted(a.strip().lower() for a in row["artists"].split(","))
    return row["track"].strip().lower() + " | " + ", ".join(artists)

number_ones["song"] = number_ones.apply(song_key, axis=1)

weeks_at_1 = number_ones.groupby("song").size().rename("weeks_at_1")
playlist = number_ones.drop_duplicates(subset="song", keep="first").join(weeks_at_1, on="song")

# 3. Save a table and a list of Spotify links
OUT_DIR.mkdir(parents=True, exist_ok=True)
playlist.to_csv(OUT_DIR / "number_ones.csv", index=False)
links = "https://open.spotify.com/track/" + playlist["uri"].str.split(":").str[-1]
(OUT_DIR / "number_ones_links.txt").write_text("\n".join(links) + "\n")

print(f"{len(number_ones)} weeks, {len(playlist)} different #1 songs\n")
print(playlist[["week", "artists", "track", "weeks_at_1"]].to_string(index=False))

assert playlist["weeks_at_1"].sum() == len(number_ones), "weeks at #1 don't add up!"


