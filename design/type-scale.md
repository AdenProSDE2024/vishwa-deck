# Type scale — Vishwa deck (1440 × 810)

Six steps. Every page uses only these. Sizes are the ones already dominant in
`deck.css`; the change is that the in-between values (16, 18, 20, 22, 11.5, 13,
13.5, 14, 10.5) collapse into the nearest step.

| Step | Size / weight | Use | Existing class |
|---|---|---|---|
| Display | 62 / 700 | cover headline only | `h1.big` |
| Head | 47 / 700 | page headline | `h1` |
| Kicker | 25 / 700 | one-line takeaway at the bottom of a page | `.kicker` |
| Lead | 21 / 700 | card titles, node labels, statements inside a card | — |
| Body | 17 / 400 | all running copy | — |
| Caption | 14.5 / 400 | secondary line under a Lead | — |
| Label | 12.5 / 600 mono | eyebrows, status labels, axis and table headers | `.lbl`, `.eyebrow` (15 stays) |
| Chip | 11 / 400 mono | the bordered disclaimer chips | — |

Numbers keep their own scale: `.num` 64, `.num.xl` 92, stat-strip figures 33.

## Mapping applied so far

| Was | Now | Where |
|---|---|---|
| 16, 18 | 17 | body copy on 05, 06, 07, 08, 09 |
| 20, 22 | 21 | card titles on 06, 07, 09 |
| 10.5, 11.5, 12, 13 | 12.5 | mono labels everywhere except the 11px chips |
| 13.5, 14, 15 | 14.5 | secondary lines under a Lead |

`.eyebrow` stays 15 and the 11px chips stay 11 — both are deliberate outliers
already used consistently across all pages.

## Not changed

- `h1` 47 and `h1.big` 62
- `.foot` 12.5 (already on the Label step)
- Table type in `table.cmp` (appendix only)
