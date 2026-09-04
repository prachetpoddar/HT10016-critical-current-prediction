# Rechecking the fabrication claims against the whole repository

Recorded 2026-09-04, after the ten-source reading pass. Nothing in the data
changed. What changed is what the reading pass is entitled to claim.

The reading pass graded ten extractions against their publisher figures and
called six of them fabricated. It did that without first searching the
repository for prior dispositions of the same papers. Three files it never
opened already carried findings on four of the six.

## What the repository already held

`audit/full_repo_sweep_20260903.md`, written the day before, lists five papers
with a recorded disposition and the note that none was applied:

| paper | disposition already recorded | state |
|---|---|---|
| `physc.2011.05.018` | withdrawn (re-extract) | still live |
| `physc.2009.11.051` | withdrawn (re-extract) | still live |
| `jallcom.2013.04.183` | **rescaled x10** | not applied |
| `jpcs.2026.113652` | **rescaled x0.01** | not applied |
| `mtphys.2022.100783` | dropped (duplicate) | still live |

`audit/repair_plan.csv` carries the same x10 for `jallcom.2013.04.183` in a
`repair` column, and its `log10_Jc_anchor` is already the post-repair value
while its `Jc_anchor_A_per_cm2` is not, which is how an unapplied repair looks.

`audit/reextraction_input_triage.csv` records, for
`s41598-025-95932-9`: *"opened and confirmed: p5 Fig. 4(b) Jc(H) linear y, 6
series, legend 45 to 70 K"*. And for `ceramint.2024.10.058`: *"no measurement
temperature appears anywhere on the figure"*.

`audit/dual_model_critical_field_agreement.csv` records
`matpr.2019.05.078` as AGREE_NO_DATA, *"both report no critical-field data"*,
which corroborates rather than refutes the finding on that paper.

## The corrections

**Retracted: `s41598-025-95932-9`.** The pass claimed the paper's only
critical-current figure is a self-field measurement and that six field-dependent
series had been invented. Fig. 4(b) is a Jc-versus-field figure, 0 to 1 T, six
series at 45 to 70 K, sample B. The extraction's axes and temperatures are
right. Its values are not: the 0.1 T points run 1.5x to 50x above the panel, the
45 K point of 3.0e6 exceeds the panel maximum of 2.2e6, a uniform -300000 ladder
replaces a 60-fold fan-out, and the record names sample A where the panel is
sample B. Bad digitisation, not fabrication. The pass read only the Fig. 4(a)
caption and never opened the page.

**Downgraded: `jallcom.2013.04.183`.** Not fabricated. Systematically about ten
times low, which is the repair already on file. With the x10 applied the values
land within 12 to 30 per cent of Fig. 8. What survives is that 28 of the 56 rows
are a 25 K figure the paper never printed, the H=0 anchor is outside a plotted
axis that starts at 0.25 T, and Tc is recorded 110 K against Table 1's 64 to 74.

**Not new: `jpcs.2026.113652`.** The hundredfold error was already on file as
"rescaled x0.01". New only in the reason, which the repository did not state:
the printed current axis is A/m2. The rows at 1.0 to 6.5 T for a figure ending
at 0.5 T, and the extracted Co0 panel that is not printed, do stand.

**Partly retracted: `phpro.2015.06.160`.** The claim that the Tier 1 critical
field of 9.0 T was harvested from a figure caption stating a measurement range
is wrong. The paper gives dHc2/dT of about -2.04 T/K near Tc, and 9.0 T at
17.7 K is a legitimate evaluation of the paper's own slope. The paper also
states Hc2(0) of about 26 T and 31 T. Separately, the pass said 1.0e6 was 25x
the paper's stated maximum; it is 2.6x the stated 3.9e5, and 77x the 15 K curve
it was assigned to. The series defects stand.

**Mechanism corrected: `s10854-026-16566-9`.** The series are not a copy of
panel (d). Each of the four exceeds its own panel, by 33x, 21x, 6x and 2.6x,
compressing a 27-fold spread across substitution into 2.1-fold. The verdict
stands; the explanation given for it did not.

**Unchanged:** `matpr.2019.05.078` (360x to 5000x above a figure whose maximum
is about 2200 A/cm2, with mono and multi reversed), `ceramint.2024.10.058`
(ranking close to reversed, the lowest curve recorded as the highest),
`matchemphys.2023.128348` (sound), `cjph.2024.09.042` (consistent),
`physc.2016.05.023` (kilo-oersted axis).

## What the headline numbers do and do not do

The 56 passing field-axis fits are unaffected. The four papers whose verdicts
moved carry no passing fits between them; they carry anchor rows. Of the 24
anchor rows in the newly read set, eight sit under a scale repair already
planned and one, `phpro`'s 7 K row, survives scrutiny.

## The rule this session earned

Every claim that extracted data is fabricated is rechecked against the entire
repository before it is reported. Search first for other records of the same
paper, alternate extractions, recorded repairs and prior dispositions. Four of
six verdicts here were affected by files that were one grep away.
