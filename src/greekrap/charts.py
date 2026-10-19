"""Load weekly Spotify chart files and parse artist credits."""

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

