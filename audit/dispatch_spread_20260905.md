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

## Regenerated, 2026-09-05

The prediction file could not be regenerated in this checkout because three
inputs were absent. They are staged now: `3DSC_MP.csv`,
`literature_hc2_in_scope.csv` and `phase_3_makidegennes_per_paper_fits.csv`,
plus 32 extraction files the uploads copy of `data_agent2/v3_2_2B_extension`
was missing, which is why a first run produced 220 candidates against the
paper's 233. The generator runs. Script
`analysis/compare_regenerated_dispatch.py`, output in
`audit/p57_regen_20260905/`.

**The file as a whole does not reproduce, and the emitted set does.** Running
the generator on the pre-withdrawal snapshot and applying the two post-hoc
gate scripts gives 2151 rows against the deposit's 2097. Every one of the 54
extra rows is refused; the emitted set is 163 rows on identical
(compound, temperature, field) keys, at the same two grid points, with the same
15.5 T anchor on all 86 records at 4.2 K and the same 83 parent to 3 exact
split. So the comparison below is like-for-like on the quantity compared, and
is not a reproduction of the file. The residual difference is in how many
targets fall below the validated reduced field, 1120 against 1054.

**The spread at 4.2 K is twenty-three times larger on the corrected tables.**

| | deposit | regenerated |
|---|---:|---:|
| records at 4.2 K, 5 T | 86 | 86 |
| span of the prediction | 0.0098 dex | 0.2242 dex |
| on the substructure-aggregate predictor | 86 | 84 |
| on a sample-form-conditional predictor | 0 | 2 |

The whole of the widening is two records. Eighty-four still route to the
substructure-aggregate predictor and span 0.0085 dex among themselves, which is
slightly tighter than before. Two MgB2 records acquire a `wire` sample-form
commitment they did not have on the deposited tables, route to the Stage 2
conditional pool, and land at 5.199 and 5.198 against the aggregate's 4.980.

**This is a better answer to Referee A than the letter gives.** The narrow
spread is a property of the aggregate predictor evaluated at its own reference
point. The moment two records route to a conditioned cell instead, they sit
0.22 dex away. That demonstrates the conditioning claim rather than
embarrassing it.

The 0.0098 dex figure in the letter is therefore superseded and should be
0.2242 dex, with the split reported: the aggregate cell is still flat and the
flatness is structural.

**Still not settled.** The 54-row difference is unexplained. It is confined to
refused targets and does not touch any emitted prediction, but the reason it
exists has not been traced, and this comparison should not be described as a
reproduction. It has also not been through the adversarial review gate.
