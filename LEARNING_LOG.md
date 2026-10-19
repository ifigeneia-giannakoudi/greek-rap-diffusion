# Learning log

Two or three lines a day: what I learned, where I got stuck, how I solved it.

## Day 1 · Sat Oct 17
- Set up a Python 3.11 venv on the cluster, a package layout (`src/greekrap`), pytest and GitHub Actions CI.
- Stuck: the cluster's Jupyter module set PYTHONPATH to its Python 3.9 packages, so pip skipped numpy/matplotlib in my venv. Fixed with `env.sh` (unload jupyter, `unset PYTHONPATH`) and verified with `pip check`.
- Created a restricted YouTube Data API key, stored in a git-ignored `.env`; first API call works.
- Downloaded first charts. Format: one CSV per week, date in file name, artists comma-separated, streams as text, previous_rank = -1 for new entries.
- Note: total streams grew a lot since 2020 (Spotify adoption in Greece), so compare shares, not raw streams.
- Built a playlist of all 167 unique #1 songs. Found 7 songs with two Spotify IDs (single vs album release); fixed by matching on title + artists (entity resolution). Added an assert that weeks at #1 sum to 346.
- Insight: rap already dominates #1 from 2020, so the diffusion story must be measured across the whole Top 200, not at #1.

## Day 2 (cont.) · Sun Oct 18 · Reframing the research question
- Trap already dominated in 2020, so the question became: did hip-hop-style rap rise inside a trap market?
- Feasibility: 33 of 40 named hip-hop artists reach the Top 200 (7 never chart: the Top 200 only sees the mainstream).
- Pure hip-hop (no trap-star collaborators) stream share: 6.1% (2020) -> ~15% (2023-25) -> 7.4% (2026 so far).
- Collaborations with trap stars peaked in 2021 (4.9%), then pure hip-hop took over.
- Without LEX, Bloody Hawk, Novel 729, Logos Timis: peak 10.2% in 2023, falling since; the big four's part of pure hip-hop rose from ~32% to ~61% (concentration).
- 2026 dip = big names between albums (release cycles) + shrinking wider scene; possible recall bias in my artist list still to check.
- Relabelled: Saske and Light -> in-between (trap-leaning); Mente Fuerte -> hip-hop.
- New numbers: pure hip-hop 3.6% (2020) -> 12.4% (2023) -> 11.4% (2025) -> 4.4% (2026).
  In 2020 ~half of hip-hop's streams came via trap-star collaborations, ~20% by 2023.
  Big four's part of pure hip-hop: ~40% (2023) -> ~80% (2025).
- Sensitivity: same four phases with and without Saske -> the story is robust to this label.
- Recall-bias check: listed all artists first charting since 2025 and not yet labelled; no hip-hop names among them, so the 2026 dip is not an artefact of my artist list.

## Day 2 (cont.) · Mon Oct 19 · Final labels for the exploration
- Fixed a real bug: IN_BETWEEN was defined twice and the copies drifted (Mente Fuerte in both sets). Now one set + an assert.
- Added historic artists found in the charts (Iratus, Mikros Kleftis, Fi Vita Sigma, Lobo, Zoro&Buzz, Goin' Through, Stavento, Giorgos Orfanidis). No 90s founders chart since 2020.
- Final: hip-hop 7.4% (2020) -> 15.7% (2023) -> 6.9% (2026); pure 3.4% -> 12.7% -> 3.8%.
- Collaborations' part of hip-hop: >50% (2020) -> ~20% (2023) -> ~42% (2025). LEX's 2025 peak was mostly collaborations.
