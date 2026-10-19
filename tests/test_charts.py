from greekrap.charts import parse_artists


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
