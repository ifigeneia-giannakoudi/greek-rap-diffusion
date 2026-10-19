import pandas as pd
import pytest

from greekrap.charts import load_charts, parse_artists, week_from_filename

def test_single_artist():
    assert parse_artists("SNIK") == ["SNIK"]


def test_two_artists():
    assert parse_artists("HermesHermes, BLVD") == ["HermesHermes", "BLVD"]


def test_order_is_kept():
    assert parse_artists("Sicario, Konstantinos Argiros, SNIK") == [
        "Sicario", "Konstantinos Argiros", "SNIK"]


def test_greek_characters():
    assert parse_artists("Ρία Ελληνίδου, Φοίβος") == ["Ρία Ελληνίδου", "Φοίβος"]


def test_compound_name_not_split():
    assert parse_artists("Tyler, The Creator, Fy") == ["Tyler, The Creator", "Fy"]


def test_duplicates_removed():
    assert parse_artists("SNIK, SNIK") == ["SNIK"]


def test_ampersand_name_kept_whole():
    assert parse_artists("Zoro&Buzz, Lobo") == ["Zoro&Buzz", "Lobo"]


def test_empty_and_missing():
    assert parse_artists("") == []
    assert parse_artists(None) == []

# ---------- loading chart files ----------

def write_chart(path, rows):
    """Write a tiny fake chart CSV in the same format as Spotify's."""
    pd.DataFrame(rows, columns=["rank", "uri", "artist_names", "track_name", "streams"]
                 ).to_csv(path, index=False)


def test_week_from_filename():
    assert week_from_filename("regional-gr-weekly-2020-03-05.csv") == pd.Timestamp("2020-03-05")
    with pytest.raises(ValueError):
        week_from_filename("something-else.csv")


def test_load_charts(tmp_path):
    write_chart(tmp_path / "regional-gr-weekly-2026-10-15.csv", [
        [2, "spotify:track:bbb", "DIFF, Spize", "BACK", "500929"],
        [1, "spotify:track:aaa", "HermesHermes, BLVD", "VGAINO RIXNO", "519139"],
    ])
    write_chart(tmp_path / "regional-gr-weekly-2020-03-05.csv", [
        [1, "spotify:track:ccc", "Roddy Ricch", "The Box", "128791"],
    ])

    charts = load_charts(tmp_path)

    assert len(charts) == 3
    assert charts["week"].iloc[0] == pd.Timestamp("2020-03-05")        # sorted by week
    assert list(charts["rank"].iloc[1:]) == [1, 2]                     # then by rank
    assert charts["streams"].dtype == "int64"                          # numbers, not text
    assert charts.loc[1, "artists"] == ["HermesHermes", "BLVD"]        # parsed into a list
    assert charts.loc[1, "track_id"] == "aaa"


def test_browser_duplicate_file_is_rejected(tmp_path):
    row = [[1, "spotify:track:aaa", "SNIK", "Song", "100"]]
    write_chart(tmp_path / "regional-gr-weekly-2020-03-05.csv", row)
    write_chart(tmp_path / "regional-gr-weekly-2020-03-05 (1).csv", row)   # browser duplicate
    with pytest.raises(ValueError, match="Unexpected chart file name"):
        load_charts(tmp_path)


def test_duplicate_rank_is_rejected(tmp_path):
    write_chart(tmp_path / "regional-gr-weekly-2020-03-05.csv", [
        [1, "spotify:track:aaa", "SNIK", "Song A", "100"],
        [1, "spotify:track:bbb", "LEX", "Song B", "90"],      # two songs at rank 1
    ])
    with pytest.raises(ValueError, match="duplicate"):
        load_charts(tmp_path)

def test_empty_folder_is_rejected(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_charts(tmp_path)
