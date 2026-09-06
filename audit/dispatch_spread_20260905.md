# The narrow dispatch spread, and a count the paper gets wrong

Recorded 2026-09-05. Script `analysis/dispatch_spread_mechanism.py`.

Referee A: "The spread of Jc at H = 0 is also suspiciously small." The letter
concedes it and gives the figure: 0.0098 dex across the 86 MgB2-class records at
4.2 K and 5 T. This traces where that number comes from. Both of the things I
first concluded were broken by review before anything was reported, and the
corrections are the substance of the note.

## The paper says one grid point. There are two.

| grid point | records | compounds | span | median interval |
|---|---:|---:|---:|---:|
| 4.2 K, 5 T | 86 | 84 | 0.0098 dex | 0.6024 dex |
| 20 K, 5 T | 77 | 75 | 0.2592 dex | 0.8180 dex |

Both clear the gates this revision introduced: reduced temperature 0.48 to 0.70
against the 0.7 bound, reduced field 0.3226 against the 0.3 bound. Section III.E
and the response letter each call 4.2 K and 5 T "the one grid point that
survives the gate". That is wrong, and 77 emitted records say so.

The wording appears to come from misreading an assertion.
`analysis/apply_dispatch_scope_rewrite.py` checks that one *field* is emitted,
which is true, and that seems to have been carried into the text as one grid
point.

## At 20 K the letter's explanation is right

The letter says the compound-specific inputs are the critical-field anchor and
the transition temperature. At 20 K the prediction regresses on the temperature
term the generator forms with slope 1.216 and R squared 0.996, recovering the
family exponent of 1.14. The candidate's own Tc enters exactly as described, and
77 records take 77 distinct values.

**So the letter is not wrong.** It is incomplete at one of the two grid points.
A first version of this note said the explanation "is not what the deposited
predictions do", and that would have handed the referee an error.

## At 4.2 K the transition temperature cannot enter

`form3_predict_bootstrap` anchors every prediction at a reference point, and
`T_REF` is 4.2 K. The temperature term is
`log10(1 - T/Tc) - log10(1 - T_REF/Tc)`, which at the reference temperature is
identically zero for every candidate whatever its Tc. Across 59 distinct
transition-temperature anchors from 8.9 to 41.4 K, the largest value that term
takes is exactly 0.

Combined with a fact the manuscript already states, that every dispatched record
carries the same 15.5 T parent anchor so the field term is common, the
prediction at 4.2 K is one family-level constant.

**It is not the family anchor returned unchanged**, which is the second thing
review broke. The anchor is 5.3241 and the prediction is 4.9800; the shared
field term displaces it by 0.3441 dex.

## What the 0.0098 dex actually is

Bootstrap Monte Carlo on an 18-fit pool, and nothing else. With the temperature
term zero and the field term shared, the prediction reduces to a median over
5000 draws of one pool, drawn independently for each candidate. Simulating that
gives a span of 0.0092 with a standard deviation of 0.0016, of which the
observed 0.0098 is an ordinary draw.

The plus or minus 20 percent parent-anchor envelope contributes nothing to it.
The dispatch takes the median of three symmetric perturbations, which returns
the unperturbed value exactly. It does widen the interval: 0.3949 dex on the
three records with an exact anchor against 0.6025 on the 83 with a parent
anchor, so 0.21 dex of the quoted width is a deterministic anchor envelope
rather than sampling.

One consequence worth knowing: at the upper perturbation the envelope evaluates
the model at 18.6 T, a reduced field of 0.269, below the 0.3 bound the same
revision introduced. A third of the envelope sits outside the window.

## Two figures that are not the same figure

The letter says "1.6% of the 0.60 dex bootstrap interval at that point". The
manuscript separately says "0.61 dex across non-refused predictions". Those are
different quantities: 0.6024 at the reference point, 0.6117 over both grid
points. A first version of this script checked the letter's figure against the
manuscript's quantity and passed on the conflation; substituting the correct
definition made it fail. Both now reproduce, each against its own definition.

## A block on the 20 K half

`audit/beta_T_withdrawal_notes.md` records that
`data/phase_3_p57_de_novo_predictions.csv` was not regenerated after the beta_T
pool moved, and the generator cannot be run in this checkout because two of its
inputs are absent. The 4.2 K figures do not depend on beta_T at all, because the
temperature term is zero there, so they are safe. **The 20 K figures depend on
it directly and should not be quoted to a referee until the file is
regenerated.**

The deposited file also carries five columns and three refusal codes the
generator never writes; those come from `apply_field_window_gate.py` and
`apply_temperature_window_gate.py` applied afterwards. Nothing in the file pins
which version produced it.

## What this means for A6

The concession stands and gets stronger, but the thing to correct first is the
grid-point count, not the explanation. The honest version tells the referee that
the dispatch emits at two points rather than one; that at 20 K the transition
temperature enters as described; that at 4.2 K it cannot, because that is the
reference temperature, so the prediction there is a single family constant; and
that the residual 0.0098 dex is sampling noise on eighteen fits.

## Regenerated, 2026-09-05, and a claim retracted

The prediction file could not be regenerated in this checkout because three
inputs were absent. They are staged now: `3DSC_MP.csv`,
`literature_hc2_in_scope.csv` and `phase_3_makidegennes_per_paper_fits.csv`,
plus 32 extraction files the uploads copy of `data_agent2/v3_2_2B_extension`
was missing. The generator runs. Script
`analysis/compare_regenerated_dispatch.py`, outputs and a manifest in
`audit/p57_regen_20260905/`.

### The claim I was about to publish, and why it is wrong

I was going to tell Referee A that the 0.0098 dex spread becomes 0.2242 dex on
the corrected tables. An adversarial review refuted the attribution and I have
since confirmed it by running the generator on the tables as originally
released, before any withdrawal and before the anchor repair.

| arm | rows | span at 4.2 K, 5 T | on a conditional predictor |
|---|---:|---:|---:|
| deposited file | 2097 | 0.0098 dex | 0 |
| generator, release tables (git 8ad8d43) | 2151 | 0.2255 dex | 2 |
| generator, current tables | 2151 | 0.2242 dex | 2 |

**The withdrawals and the anchor repair move the spread by 0.0013 dex, which is
0.6 percent of it.** Everything else was there on the tables as released. There
is no corrections result here.

### What the run does show, and it is more serious

**The deposited prediction file does not reproduce from the deposited generator
run on the deposited tables.** On the release tables the generator routes two
MgB2 records from `matpr.2019.05.078` to the (conventional_AlB2, wire)
conditional cell, because that paper's fits carry sample form "wire" and wire
is in the generator's `ENGINEERED_FORMS`. Those two fits have been in
`phase_3_form3_fits_partial_cohortB_v2.csv`, unchanged, at every revision from
the release to now, and the lookup that reads them has been in the generator
since the release. The deposited file shows both records on the
substructure-aggregate predictor. Something between the generator and the
deposit removed the commitment and nothing in the repository records it.

The regenerated file also re-admits candidates that were withdrawn by hand.
Regenerating gives 239 candidates against the deposit's 233; the six extra are
one record from `physb.2025.417755` and five from `physc.2010.03.003`, the
paper this repository itself files as a withdrawn field-axis extraction. The
withdrawal was applied by editing the CSV, and the generator's candidate list
is built from the extraction directory, which no withdrawal touched. So the
generator cannot enforce the withdrawals, and any regeneration silently brings
them back. All six are refused, so no emitted prediction changes, but the
mechanism is the finding.

### A first regeneration was invalid, and the reason is worth recording

The generator sets `REPO` to the grandparent of the repository directory and
reads its extraction index from `REPO/data_agent2/v3_2_2B_extension`, while the
module it imports for candidate generation hardcodes a different `REPO`. In a
checkout where only the second resolves, `build_a2_tc_index` returns an empty
dict without raising, and every extraction-derived transition temperature falls
silently to a substructure default. My first run produced 612 rows on defaults
where the deposit has 558 on extraction values, moving 26 candidates' anchors
and flipping 30 refusal codes. The 4.2 K figure survived it, because the
temperature term is zero there, but nothing else in that file did. The run in
`audit/p57_regen_20260905/` is the corrected one and carries a manifest naming
the resolved path and hashing every input.

### The wire cell should not be shown to a referee

It holds 8 fits from 2 papers, 6 of them from one. The two records it predicts
come from `matpr.2019.05.078`, whose own 2 fits are in the pool, so a quarter
of the pool is the thing being predicted. That is exactly the case the A4
answer concedes: sample form being very nearly a relabelling of source paper.
Offering a 0.22 dex conditional shift as a demonstration of conditioning would
contradict the concession made four sections earlier in the same letter.

### What stands for A6

Not the widening. The letter's 0.0098 dex still describes the deposited file,
and what that figure measures is bootstrap Monte Carlo on an 18-fit pool: at
4.2 K the temperature term is zero for every candidate and all 86 share a
15.5 T anchor, so the 84 aggregate records have identical model inputs and
differ only in their draw. 0.0098 against 0.0085 is inside that noise. The
two-grid-point correction in the earlier section of this note also stands.

### Damage repaired

Running the two gate scripts rewrites `audit/field_window_gate.csv` and
`audit/temperature_window_gate.csv` in place. A first pass committed them in a
state describing the regenerated table while the shipped prediction table was
the deposited one. Both are restored.

## Where the regeneration diverges, assessed exhaustively

Recorded 2026-09-05. Script `analysis/where_regeneration_diverges.py`. Asked
before deciding what to disclose, and the answer narrows the disclosure a long
way.

### The released file against the generator that shipped with it

Same 2151 rows, aligned one to one, on the same tables, with the two gate
scripts left off because they postdate the release.

| what differs | rows | size |
|---|---:|---|
| `sample_form_commitment`, wire to blank | 18 | |
| `predictor_method_scope`, conditional to aggregate | 18 | |
| `predicted_log_Jc` on those 18 rows | 18 | median 0.266, max 0.328 dex |
| `predicted_log_Jc` on every other row | 337 | median 0.0007, max 0.0138 dex |

Nothing else. Every anchor, every provenance tier, every refusal code, the
candidate list, the row count: identical. The 337 are the bootstrap draw and
none exceeds 0.014 dex.

**So the released prediction file is the generator's own output with exactly the
wire commitments removed and those eighteen rows recomputed on the aggregate
predictor.** It is one paper wide. `matpr.2019.05.078` carries two fits whose
sample form is "wire", wire is in the generator's `ENGINEERED_FORMS`, and the
commitment path has been in the generator since the release commit and has never
been edited. Nothing else in the repository writes that column. The released
file also carries 1206 `single_crystal` commitments, exactly as the generator
produces them, so the mechanism was working and only this one form was removed.

### The deposit against a regeneration on the current tables

| rows moving more than 0.02 dex | n | max |
|---|---:|---:|
| emitted, on the wire records | 4 | 0.218 dex |
| emitted, anything else | 0 | |
| refused, temperature-axis only | 141 | 3.80 dex |

The 141 are all `iron_pnictide_122` and all carry `Hc2_unavailable`, so they are
temperature-axis-only predictions that the dispatch refuses. They move because
beta_T moved with the withdrawals and the anchor repair. That is the corrections
working, on rows the paper does not report.

**Among rows the paper does report, four predictions change and all four are the
wire records.** Everything else emitted is identical or differs by less than
0.02 dex.

Six candidates also come back, 54 rows from `physc.2010.03.003` and
`physb.2025.417755`, because the withdrawals were applied by editing the CSV
while the candidate list is rebuilt from the extraction directory. All 54 are
refused.

### What this means for the disclosure

The reproduction failure is not diffuse. It is one paper, one sample form,
eighteen rows, four of them emitted, and it was present in the released file
before any correction in this revision. The withdrawal-enforcement gap is
separate, affects no emitted prediction, and is a fixable defect in how a
withdrawal is applied rather than a defect in a reported number.

## Closed, 2026-09-06

Both open items are resolved and the deferral recorded above is lifted.

**The prediction file reproduces.** `analysis/rebuild_dispatch.py` runs the four
scripts that produce it, in order, in a scratch copy of the repository, and
compares the result with the deposited file cell by cell. It reports no
difference. The four are `phase_3_p57_de_novo_predictions.py`,
`withdraw_records.py`, `apply_field_window_gate.py` and
`apply_temperature_window_gate.py`. Only the first was named anywhere before,
which is why a reader who ran it alone got 2151 rows against the deposited 2097
and two of the five refusal codes.

**The wire cell is gone, by rule rather than by hand.** This note recommended
that it not be shown to a referee: it holds 8 fits from 2 papers, and the
records it predicts come from one of them. The generator now reads each family's
regime from the deposited variance decomposition and commits a family in the
minor-separation regime, Outcome C, to substructure-aggregate scope, which is
what Sec. II.D already said the model does and what the deposited file already
showed. That closes the finding this note recorded as the more serious one: the
rule had been applied to the file and never written into the code, and nothing
in the repository recorded who applied it.

**The withdrawals are enforced by the chain rather than by the generator.** This
note is right that the generator cannot enforce them, because its candidate list
is rebuilt from the extraction directory. `withdraw_records.py` is step 2 of the
chain for that reason, and the six candidate records of `physc.2010.03.003` and
`physb.2025.417755` are removed there. A regeneration that skips it brings them
back, which is what the reproduction check is for.

**What moved, and what did not.** Regenerating changed two printed numbers. The
spread at 4.2 K and 5 T falls from 0.0098 dex to 0.0085, and at 20 K and 5 T
from 0.2592 to 0.2543. The regression slope at 20 K moves from 1.216 to 1.209.
The median width on the three exact-anchor records moves from 0.3949 to 0.3982.
Unchanged: 163 emitted predictions, 84 compounds, 86 and 77 records at the two
grid points, all five refusal counts, the 321 of 540 split, the 4.980 family
constant, the 5.3241 anchor and its 0.344 dex displacement, the 18-fit pool, and
the median widths of 0.6124 and 0.6016 dex, which the documents print as 0.61
and 0.60.

The 0.0085 is the same kind of quantity the 0.0098 was, and this note's own
simulation covers both: 84 independent draws on the 18-fit pool give a span of
0.0092 with a standard deviation of 0.0016.

**The block on the 20 K half is lifted.** The file behind those figures is now
the one the chain reproduces.
