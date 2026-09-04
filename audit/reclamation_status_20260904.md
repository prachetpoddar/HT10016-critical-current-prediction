# Reclamation status

Recorded 2026-09-04. Every defective paper is on one of two routes: re-trace the
figure, or apply an arithmetic unit repair. Which route a paper takes was
decided by opening its figure, not by assuming.

## Traced, done

| paper | figure | series | points | check against the paper's own text |
|---|---|---:|---:|---|
| `ceramint.2024.10.058` | Fig. 4 | 5 | 189 | ranking restored; Nitrogen-1 lowest, not highest |
| `jallcom.2013.04.183` | Fig. 8 | 4 | 160 | matches a separate reading of the page to under 2% |
| `s10854-026-16566-9` | Fig. 9(a)-(d) | 12 | 236 | traced 3% zero-field 5 K value 1.18e6 against the paper's stated 1.1e6 |
| `matpr.2019.05.078` | Fig. 2(a) | 2 | 72 | mono/multi ordering restored |
| `phpro.2015.06.160` | Fig. 3 left | 6 | 231 | traced 4.2 K value 3.63e5 against the paper's stated 3.9e5 at zero field |

Three of the five carry an independent confirmation from a sentence in the paper
that was not used to build the extraction.

## Unit repair, verified value by value first

| paper | rule | why arithmetic is enough |
|---|---|---|
| `physc.2009.05.098` | H ÷ 10 | all nine low-field readings track the printed curves and each series ends where its curve does |
| `s41598-025-24806-x` | H ÷ 10 | the three Tc values match the caption exactly and the currents track the curves to about 30% |

## Checked for the unit route and rejected

Three papers were assumed to be unit-only defects and each turned out to have
wrong values as well. The assumption was made once and is recorded in
`analysis/apply_unit_repairs.py` so it is not made again.

- **`physc.2010.05.048`**: the recorded 2 K series runs 1e6 down to 2.6e5 in a
  smooth exponential where the printed curve starts near 5e5 and is flat around
  2e5 with a fishtail. The paper states 4e5 at 2 K under zero field against a
  recorded 1e6.
- **`physc.2011.05.018`**: the recorded 680 C series at 2 K falls only from 1e5
  to 8e4 where the printed curve falls from about 1e5 to about 1.4e4.
- **`jpcs.2026.113652`**: converting A/m2 to A/cm2 does not reconcile the
  numbers. The recorded 2.5e6 to 4e6 becomes 250 to 400 A/cm2 where the printed
  panels span 3e3 to 4e4 A/cm2. The `rescaled x0.01` repair on file is a guess.

## Still to trace

`physc.2010.05.048`, `physc.2011.05.018`, `jpcs.2026.113652`,
`physc.2009.11.051`, `s41598-025-95932-9`, `phpro.2015.06.160` right panel, and
`physc.2016.05.023` whose extraction CSV is not in the corpus at all.

## Six further tool fixes this pass

`open_frame` for L-shaped charts, `tick_side` for panels labelled on the right,
per-axis `tick_darkness`, `tick_min_len`, `tick_min_count` for three-decade log
axes, and per-series `exclude_boxes` for annotation drawn in the same colour as
a curve. `analysis/figure_probe.py` now reports the frame, the tick candidates
on all four sides in both directions, and the exact marker colours in one call,
so a spec is written once instead of guessed at five times.
