# 2026-05-02 Skill Alignment Benchmark

This note records the benchmark pass used before committing the current
scheme-alignment update.

The purpose of this run was not to celebrate middle-carrier elegance.

It was to check whether the current `baseline-current` package is now
landing in the correct final-answer families on the hard set that had
previously drifted.

## Evaluation Standard

Use final-answer-family agreement as the promotion gate.

Do not score by:

- elegance
- closure quality alone
- "sounds like the editorial"
- self-reported confidence

## Core Hard-Set Check

The current package was re-run against the following hard problems and
judged by whether the produced closure landed in the official family.

| Problem | Result | Notes |
| --- | --- | --- |
| `AGC012F - Prefix Median` | partial pass | reverse family recovered, but state still thicker than the tightest final DP form |
| `2026 APC L - Onion` | pass | small-vector + ordered collinear groups + endpoint peel recovered |
| `IOI 2015 - towns` | pass | `B` multiset + candidate fiber + same-component + majority certification recovered |

Indicative alignment scores from this check:

- `AGC012F`: `68/100`
- `Onion`: `90/100`
- `towns`: `88/100`

Average across this strict hard set: `80/100`.

## Previously Recovered Families

The current package had also already been driven back into the correct
families on:

- `ABC455 G - Balanced Subarrays`
- `Min Max Subarrays II`
- `IOI 2020 - Supertrees`
- `JOIG Practice - Transmission`

## Commit Meaning

This update should be understood as:

- the stable unified scheme has been written into the package
- layerwise primitive reselection is now explicit
- final settlement remains inside the same cognition layer
- beautiful wrong families are now explicitly demoted
- the package has been tested against the current hard-set alignment suite

It should not be understood as:

- full universal closure
- all hard problems now 90+
- no further benchmark drift risk
