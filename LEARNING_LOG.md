# Learning log

Two or three lines a day: what I learned, where I got stuck, how I solved it.

## Day 1 · Sat Oct 17
- Set up a Python 3.11 venv on the cluster, a package layout (`src/greekrap`), pytest and GitHub Actions CI.
- Stuck: the cluster's Jupyter module set PYTHONPATH to its Python 3.9 packages, so pip skipped numpy/matplotlib in my venv. Fixed with `env.sh` (unload jupyter, `unset PYTHONPATH`) and verified with `pip check`.
- Created a restricted YouTube Data API key, stored in a git-ignored `.env`; first API call works.
