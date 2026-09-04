# Ten flagged sources opened, six of them fabricated

Recorded 2026-09-04. Table: `audit/flagged_source_reading.csv`.

The deposit's own `audit/extraction_integrity.csv` flags fifteen files that are
still in the analysis. Four had been read at source earlier in the session.
This pass opened the publisher PDF for ten more. One remains unread because its
PDF is not in the corpus.

A correction to an earlier statement in this session: three Springer papers were
described as having no PDF on hand. Two of them do, and one of those two is
`s10854-026-16566-9`, the single largest block of passing field-axis fits among
the flagged files.

## What each source showed

| paper | screen | verdict | the decisive observation |
|---|---|---|---|
| `phpro.2015.06.160` | CHECK | fabricated | the paper states 3.9e5 A/cm2 as its maximum at zero field at 4.2 K; the extraction reports 1.0e6 at 15 K and 1 T |
| `matchemphys.2023.128348` | CHECK | sound | X04's self-field value is exact at 155500 A/cm2; the other three drift 7 to 40 per cent |
| `matpr.2019.05.078` | CHECK | fabricated | the figure's maximum is about 2000 A/cm2; the extraction reports 1.0e6 |
| `cjph.2024.09.042` | CHECK | consistent | real tesla-axis data; contributes no anchors and no passing fits |
| `jpcs.2026.113652` | FAIL | fabricated | the current axis is A/m2, read as A/cm2; and twelve rows sit at 1.0 to 6.5 T for a figure whose field axis stops at 0.5 T |
| `jallcom.2013.04.183` | FAIL | fabricated | half the rows are a 25 K figure the paper never printed; Tc recorded 110 K where Table 1 reports 64 to 74 K |
| `ceramint.2024.10.058` | FAIL | fabricated | Nitrogen-1 is ranked highest; the figure has it lowest by an order of magnitude |
| `physc.2016.05.023` | FAIL | kOe axis | the printed field axis is kilo-oersted; the extraction CSV is not in the corpus |
| `s10854-026-16566-9` | FAIL | fabricated | the x=0% series reproduces the 3% panel; the fabricated series then run to nearly double the paper's stated maximum |
| `s41598-025-95932-9` | FAIL | fabricated | the paper's only critical-current figure is a self-field measurement; the extraction supplies six field-dependent series |

## What the screen's grades were worth

Four of the ten were graded FAIL and all four are bad. Six were graded CHECK
and two of those, `phpro.2015.06.160` and `matpr.2019.05.078`, are as bad as
any FAIL. The CHECK grade under-reports. Both of those papers were graded on a
high round fraction with no named signature, which is what a fabricated set
looks like when the fabricator varies the last digit.

Two papers passed: `matchemphys.2023.128348` is a real digitisation with real
imprecision, and its Tier 1 critical field of 3 T at 20 K is genuinely
supported by the paper's own criterion. `cjph.2024.09.042` is consistent and
contributes nothing to any headline number.

## What falls

| | papers | field-axis fits | of which passing | anchor rows |
|---|---:|---:|---:|---:|
| established earlier this session | 4 | 36 | 36 | 7 |
| established in this pass | 7 | 45 | 20 | 24 |
| **combined** | **11** | **81** | **56** | **31** |

That leaves **38 of the 94 passing field-axis fits** and **65 of the 96 anchor
rows** standing on sources not yet shown to be defective.

The three largest single losses are `mtphys.2022.100783` at 20 passing fits,
`s10854-026-16566-9` at 12, and `physc.2009.11.051` and `physc.2010.05.048` at
8 each.

## The pattern

Ten sources were opened in this pass and eight of the ten were exactly what the
screen's signature said, or worse. Nothing here was found by reading the
extracted numbers. Every finding came from putting the extracted numbers beside
the printed figure, and in four cases beside a sentence in the paper's own text
stating a maximum the extraction exceeds.
