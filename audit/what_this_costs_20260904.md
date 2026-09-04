# What the reading pass costs

Recorded 2026-09-04. Nothing in the data changed. This is a scope estimate, not
a repair.

## Two thirds of the damage is arithmetic

Of the 41 defective anchor rows, **22 are repairable by a correction that is
already understood**, and six papers carry them:

| paper | rows | rule |
|---|---:|---|
| `physc.2009.05.098` | 9 | H / 10, kilo-oersted read as tesla |
| `physc.2009.11.051` | 2 | H / 10 |
| `physc.2010.05.048` | 1 | H / 10 |
| `s41598-025-24806-x` | 2 | H / 10 |
| `jallcom.2013.04.183` | 4 | Jc x 10, repair already on file |
| `jpcs.2026.113652` | 4 | Jc x 0.01, repair already on file |

In each of these the Jc values track the printed curves; only a scale is wrong.
Nineteen rows are not repairable, because their values contradict the figure and
no rescaling reconciles them: `s10854-026-16566-9` (4), `ceramint` (5), `matpr`
(4), `phpro` (2), `physc.2011.05.018` (2), `s41598-025-95932-9` (1), and the
`mtphys` polycrystal (1).

**Anchor rows: 96 now, 76 after repairs, 19 withdrawn.**

## The conditioning result loses two material classes

Per-family inputs to the variance decomposition, as they stand, after repairs
are applied, and if the repairs were not applied:

| family | rows now | after repair | rows if unrepaired | sample forms after repair |
|---|---:|---:|---:|---:|
| conventional_AlB2 | 22 | 18 | 18 | 2 |
| cuprate_BSCCO | 9 | 8 | 0 | **1** |
| cuprate_LSCO | 5 | **0** | 0 | 0 |
| cuprate_RBCO | 3 | 3 | 3 | 1 (never evaluable) |
| iron_chalcogenide_11 | 23 | 17 | 14 | 2 |
| iron_pnictide_1111 | 23 | **23** | 14 | 3 |
| iron_pnictide_122 | 11 | 8 | 5 | 2 |

The decomposition needs at least two sample forms in a family to have anything
to decompose. On that test:

- **`cuprate_LSCO` disappears.** Its only paper, `ceramint.2024.10.058`, ranks
  the samples close to backwards against its own Fig. 4.
- **`cuprate_BSCCO` drops to one sample form** and stops being evaluable, so its
  deposited ratio of 0.096 can no longer be computed.
- `iron_pnictide_1111` is untouched once the repairs are applied, because every
  one of its defects is a unit error.
- Three families keep two or more sample forms: AlB2, chalcogenide 11, and
  pnictide 122.

So the conditioning claim narrows from seven families to four evaluable ones,
and loses the cuprates entirely.

A caveat on the numbers above: the deposited decomposition aggregates per paper
and my per-row recomputation does not reproduce its ratios, so no new band
values are asserted here. The row and sample-form counts are plain counting and
do stand.

## The field-axis result loses one family of four

| family | passing fits now | after withdrawal | papers |
|---|---:|---:|---:|
| conventional_AlB2 | 20 | 18 | 3 |
| iron_pnictide_122 | 36 | 14 | 3 |
| iron_pnictide_1111 | 17 | 9 | 3 |
| iron_chalcogenide_11 | 21 | **1** | **1** |
| total | 94 | 42 | 10 |

`iron_chalcogenide_11` falls to a single paper and fails `MIN_COMPOUNDS = 2`,
the method's own requirement.

The repairs do not help here. Correcting a kilo-oersted axis divides the
measured span by ten, which drops it below the 0.3 threshold of Eq. (1), so all
24 of those fits leave the passing cohort whether they are repaired or
withdrawn.

And the 42 survivors are not all equally solid: 20 rest on a figure that was
opened and agreed, 12 are the `mtphys` single-crystal record that sits 1.3 to
1.7 times high with a wrong tail, 6 are the record whose DOI and PDF are
different papers, and 4 are MAGLAB rows with no figure to check.

## The work

The mechanical part is small, because the pipeline is scripted and the four
checkers already exist: apply six arithmetic repairs, withdraw seven papers,
rerun the anchor table, the decomposition, Fig. 4, the tier assignment, the
predictions and the calibration, then rerun the field axis on what survives.

The expensive part is not labour. It is that the paper currently claims a
substructure-conditional result across seven families and can support four, and
claims a field-axis result across four families and can support three. Those
sections have to be rewritten to the narrower scope, along with Table I, the
supplement tables and the response letter.

## What is not affected

The reduced-variable scaling test takes its critical fields from the compiled
reference table rather than the per-paper resolved scale, and the manuscript
already records that it shares no source papers with the unit-affected set. That
should be confirmed against the wider defective set rather than assumed.
