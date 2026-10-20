# Artist labelling guide

One row per artist name in `labels/artists.csv`. Label in order of streams (top 220 = 90% of streams).

## style
| Style | Definition | Examples |
|---|---|---|
| hip-hop | Boom bap / low bap / lyrical, conscious or underground rap; not trap production | LEX, Bloody Hawk, Logos Timis |
| in-between | Moves between trap and hip-hop; counts as hip-hop only in collaborations with hip-hop artists | RACK, TOQUEL, SNIK |
| trap | Trap production (808s, hi-hats, autotune), Greek trap / drill | |
| pop | Greek pop, urban pop, reggaeton-leaning pop | |
| laiko | Greek laiko / entertainment music | |
| international | Non-Greek artists | |
| other | Anything else | |

Leave `style` empty if unsure, and write why in `note`.

## role
- `artist`: performs on the track (default)
- `producer`: credited mainly as producer (e.g. Beyond, BeTaf Beats); style can stay empty

## canonical
Same real person or group under different names -> same `canonical` (e.g. SativaMusic -> Sativa).
Duos credited as one name (Zoro&Buzz) are their own canonical artist.

## Decisions log
- Saske, Light, Dof Twogee: in-between (trap-leaning), Oct 18-19
- Mente Fuerte: hip-hop, Oct 18-19
- Goin' Through, Stavento: hip-hop (historic; commercial era), Oct 19
