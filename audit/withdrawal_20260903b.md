# Two more records withdrawn, and what reading the papers changed

The Hc2 and Tc cross-table checks flagged two papers for a labelling
inconsistency. Reading them to settle the labels showed the labels were the
symptom.

## What survived adversarial review, and what did not

The first version of this case offered seven arguments. An independent review
broke three and corrected a fourth.

**Dropped.** That each fixed temperature equals 0.7 times the deposited Tc is
not a red flag: the figure's caption says all its loops are at t = 0.7 and the
panels print no absolute temperature, so computing T = 0.7 Tc is the only
correct way to label them. The right statement is that the temperatures inherit
the Tc error at 0.7 times its size.

**Dropped.** That the compound is recorded as BaFe2As2, the undoped parent, is
a one-field mislabel a correction could fix. It is corroboration that the record
was built without opening the paper, not grounds on its own.

**Dropped.** That one deposited point sits at 10 T past a 90 kOe axis. One point
of eleven, and a nine per cent extrapolation.

**Corrected.** Five of six transition temperatures are wrong, not six. The one
that is right, 22.8 K for x = 0.074, is the one printed as text in a caption.
Text-stated numbers were carried across and figure-read numbers were not.

## The case that stands

### 10.1016/j.physc.2009.03.028, Prozorov et al., Physica C 469 (2009) 667

The paper reports no critical current density and says so. Its figures are
magneto-optical images, M(T), Tc(x), magnetisation loops in emu, normalised
loops, Tc against ln Hp, relaxation and creep rate. No tables.

**The Bean route, the only defence, fails on the numbers.** Taking the loop
width from the paper's own Fig. 7 for x = 0.074 and normalising to 1 T, Bean
gives 1.08 at 5 K and 1.33 at 10 K, a critical current that **rises** with
field, which is the fishtail the paper exists to describe. The deposit gives
0.083 and 0.082, a monotonic fall. That is a factor of 13 to 16 in the wrong
direction.

**Nine curves are one curve.** Nine deposited series, from six crystals spanning
Tc 9 to 23 K, at four temperatures, out of two different figures, collapse onto
a single normalised shape: the coefficient of variation across all nine is 1.5
per cent at 1 T, 2.8 at 2 T and 6.6 at 3 T. The paper's central result is that
these shapes differ systematically with Tc. Independent digitisation does not
agree to 1.5 per cent; a template scaled per curve does.

**Points outside the figure.** For x = 0.038 the source panel shows the branches
merged above about 1.5 T, so the sample is reversible and the Bean current is
zero, and the panel holds no data past 3 T. The deposit asserts 700, 400 and
150 kA/cm2 at 3, 4 and 5 T, and gives that sample the same 5 T current as
x = 0.058, whose loop is still open there.

**Transition temperatures.** Against Fig. 3: 8.9, 15.2, 23.0, 21.8, 16.8 and
9.8 K for x = 0.038, 0.047, 0.058, 0.074, 0.10 and 0.118. The deposit holds
12.0, 17.0, 22.0, 22.8, 22.0 and 12.0, wrong by 5.2 K for x = 0.10.

### 10.1016/j.physc.2014.03.020, Inoue et al., Physica C 504 (2014) 73

Fig. 2(b) is the only critical-current-against-field object in the paper, holds
two curves at 4.2 K, and its y axis runs to 10^4 A/cm2.

**The deposited peak is off the chart.** 5e4 A/cm2, five times above the top
gridline of that axis and 5.4 times the largest current the paper reports
anywhere, the tape at 9.2 kA/cm2.

**The discrepancy is not a scale error.** Against the wire curve the deposit
runs about 100 times high at 1 T, 40 at 2 T, 15 at 4 T, 8 at 5 T and 3.8 at
9 T. The deposit falls by a factor of 250 across its range where the paper's
wire falls by about 25. No unit slip or rescale produces a varying factor with
the wrong curvature. All eleven values are round to one significant figure.

## What it moves

10 field-axis fits, 7 anchor rows, 2 provenance rows, 65 source points. Every
one of the 10 fits was already outside the applicability bound, so the passing
field-axis cohort stays at 94 fits over 16 papers and the leave-one-out results
do not move.

| | before | after |
|---|---|---|
| papers contributing fitted curves | 64 | **62** |
| distinct compounds | 39 | **38** |
| critical-current points | 4211 | **4146** |
| per-paper anchors | 103 | **96** |
| physical samples | 67 | **60** |
| aggregate eta^2 | 0.3473 | **0.3139** |
| iron pnictide 122 eta^2 | 0.5988 | **0.3452** |

**The 122 result is the one to look at.** The family loses 7 of its 16 physical
samples and its ratio falls from 0.60 to 0.35, which is still Regime B but close
to the 0.3 boundary. The aggregate falls to 0.314, also still Band B and also
close. No family changed regime, but two are now near an edge they were
comfortably inside.

## Consequences not yet handled

**Figure 3 needs regenerating.** Its middle panel is the 122 family, which now
has 9 markers rather than 16, and its printed ratio becomes 0.35. This container
has neither Helvetica nor Arial, and matplotlib substitutes silently, so
re-rendering here would change the deposited typeface without saying so. It has
to be regenerated where the fonts are.

**The Hc2 and Tc cross-table checks now pass.** Both flagged inconsistencies
were properties of records that should not have been in the deposit.
