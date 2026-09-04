# Where the concessions already made collide with what the reading found

Recorded 2026-09-04. A check of the three artifacts in `out_v2` against the
defect classification. Nothing in the data changed.

## What the response letter conceded, and how it framed safety

The letter concedes the critical-field scale and then argues the central claim
is insulated from it:

> The conditioning claim now rests on the variance-decomposition diagnostic,
> which uses the critical-current anchor and involves neither a fitted exponent
> nor a critical field scale, rather than on the error ratio Referee A
> questioned.

That insulation is real against a *scale* error. It gives no protection when the
anchor's Jc **values** are wrong, and nineteen of the ninety-six anchor rows are
wrong in their values rather than their scale.

The letter also tells the referees the deposit is public and that critical-field
records carry the source-figure identifier, "which is what makes the provenance
problem described below independently checkable rather than something the reader
must take on trust." That is an invitation to open the source figures.

## The two showcase tables are drawn entirely from the compromised set

**Table S4**, the supplement's excerpt from the anchor file, prints twelve data
rows. Every one comes from a paper now classed defective, weak or unresolved:

| rows | paper | state |
|---:|---|---|
| 1 | `jallcom.2023.170146` | unresolved: DOI and filed PDF are different papers |
| 1 | `mtphys.2022.100783` polycrystal | defective: 13x to 69x above the traced Fig. 6(b) |
| 1 | `mtphys.2022.100783` single crystal | weak: 1.3x to 1.7x high, wrong tail |
| 5 | `ceramint.2024.10.058` | defective: ranking close to reversed against its Fig. 4 |
| 4 | `jallcom.2013.04.183` | defective: decade scale error, repair on file, unapplied |

The surrounding text singles out the worst of them as the illustration of the
paper's contribution:

> The five rows from `ceramint.2024.10.058` show what conditioning is for: five
> bulk specimens of the same compound from the same paper, differing only in
> processing atmosphere, span 0.26 dex.

That 0.26 dex is the spread between anchors of 2200 and 1200 A/cm2. The paper's
Fig. 4 reads about 125 and about 1100 at the same field, with the sample the
table ranks highest sitting lowest on the page.

The same table prints `Tc 110.0 K` for a Bi-2212 nickel-substituted sample whose
own Table 1 reports Tc onset between 64.11 and 74.38 K.

**Table S5**, the excerpt from the fit file, prints seven rows. All seven are
from the defective or unresolved set, and the three carrying the `ok` flag,
which are the ones that enter the analysis, are `physc.2009.11.051`,
`physc.2010.05.048` and `mtphys.2022.100783`: two kilo-oersted papers and the
weak record.

Nineteen printed rows across the two tables, none of them clean.

This is not bad luck. The supplement says it selected rows "to be useful rather
than favourable" and deliberately included the fits whose resolved scale sits
far below the literature value. Those are exactly the papers the integrity
screen was pointing at. The selection principle was sound; it found the right
rows for the wrong reason.

## Section 13 is staked on an audit with no deposit

The supplement calls the Tier 1 audit "the finding that qualifies every
field-axis result in this paper". That audit has no deposited list, rule or
script, its claim to have covered every critical-current-versus-field figure
cannot be true for six papers that have no readable figure in the corpus, and it
missed `physc.2016.05.023`, `jpcs.2026.113652` and `s41598-025-24806-x`.

## What is on the other side of the ledger

- Every defect was found by the authors, through the deposit's own integrity
  screen and by opening sources, not by a referee.
- Two thirds of the anchor damage is arithmetic and already understood.
- `iron_pnictide_1111` comes through untouched once the repairs are applied.
- The refusal gates, the provenance tiers and the integrity screen are the
  machinery that caught this. That is a real property of the method.
