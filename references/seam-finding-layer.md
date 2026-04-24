# Seam-Finding Layer

This file defines the project's positive account of seam finding.

Its purpose is:

- describe how a model may become locally sensitive to thin shells, dangerous values, branch seams, and collapse points
- preserve seam awareness without turning it into a probing script
- distinguish structurally informative seams from merely easy test points

## Core Claim

Seam finding is not random trying.

Seam finding is:

- local sensitivity to where a structure is most likely to crack open
- local sensitivity to where two branches may collapse into one carrier
- local sensitivity to where one probe can expose the controller faster than full solving

It is not:

- a list of mandatory substitutions
- a fixed order of probes
- a recipe such as “always try 0, then 1, then equality”

## What Counts As A Seam

A seam may be:

- a boundary
- a singular or nearly singular point
- an equality seam
- a branch-switch location
- a midpoint or symmetry point
- a smallest failing witness
- a special value that sharply reduces the shell
- a location where two forms become the same object

The point is not that all such seams must be tested.

The point is that some of them may become locally visible when the shell is thin.

## Informative Seam

A seam is informative when:

- testing it deletes real uncertainty
- it distinguishes neighboring candidate structures
- it reveals a lower carrier or controller directly
- it causes two apparently different branches to collapse into one object

Short version:

- an informative seam changes the route

## Decorative Seam

A seam is decorative when:

- it is easy but not dangerous
- it does not reduce the shell meaningfully
- it produces a nice-looking local simplification without exposing the controller

Short version:

- decorative seams should not be overfired

## Thin-Shell Sensitivity

Thin-shell sensitivity means:

- the model notices when the current expression or structure looks thicker than the real burden
- the model notices where that thickness seems easiest to puncture

This is not:

- a requirement to probe immediately
- a requirement to enumerate all possible seams

## Seam-To-Carrier Collapse

Healthy seam use often ends when:

- one special value, equality seam, or witness location makes a smaller carrier visible
- that carrier absorbs the useful burden deletion of the probe
- the route no longer needs the probe as an explicit move

This is not:

- a host deciding the next probe

It is:

- the shell cracking into a thinner truthful carrier

## Host Constraint

The host may preserve:

- that a local seam still seems informative
- that a current shell still appears thin and puncturable
- that a probe collapsed two branches into one carrier

The host must not preserve:

- a fixed probe order
- a canonical danger-point checklist
- a reusable seam recipe by topic

## Final Rule

The project should allow seam awareness to appear, sharpen, cool, or disappear.

It must not convert seam finding into a reusable probing workflow.
