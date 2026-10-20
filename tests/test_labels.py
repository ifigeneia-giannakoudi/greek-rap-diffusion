import pytest

from greekrap.labels import load_labels

HEADER = "name,canonical,style,role,note\n"


def write(tmp_path, body):
    path = tmp_path / "artists.csv"
    path.write_text(HEADER + body, encoding="utf-8")
    return path


def test_valid_file_loads(tmp_path):
    labels = load_labels(write(tmp_path, "LEX,LEX,hip-hop,artist,\nBeyond,,,producer,\n"))
    assert list(labels["style"]) == ["hip-hop", ""]
    assert labels.loc[1, "canonical"] == "Beyond"      # empty canonical -> the name itself


def test_spaces_are_stripped(tmp_path):
    labels = load_labels(write(tmp_path, "LEX,LEX, hip-hop ,artist,\n"))
    assert labels.loc[0, "style"] == "hip-hop"


def test_style_typo_is_rejected(tmp_path):
    with pytest.raises(ValueError, match="unknown style"):
        load_labels(write(tmp_path, "LEX,LEX,hiphop,artist,\n"))


def test_duplicate_name_is_rejected(tmp_path):
    with pytest.raises(ValueError, match="more than once"):
        load_labels(write(tmp_path, "LEX,LEX,hip-hop,artist,\nLEX,LEX,trap,artist,\n"))


def test_greek_name_survives(tmp_path):
    labels = load_labels(write(tmp_path, "Ρία Ελληνίδου,Ρία Ελληνίδου,pop,artist,\n"))
    assert labels.loc[0, "name"] == "Ρία Ελληνίδου"
