# Wu Boshi Consolidation Candidates

This file records likely first-pass merges or structural cleanups for the library.

Purpose:

- keep the system from expanding into an unstructured forest of names
- identify where multiple files are now expressing one deeper family

## Candidate A: Function-Bank Stack

Likely cluster:

- `function-bank-clusters`
- `public-function-bank-registry`
- parts of `function-archetype-matching`
- parts of `topic-routing-maps`

Why:

- all describe “many functions -> a few mother behaviors -> route by recognition”

Recommendation:

- first-pass consolidation now active:
  - `function-bank-superfamily` is now the top-level surface
  - `function-bank-clusters` provides the recurring bank logic
  - `function-archetype-matching` and `topic-routing-maps` are active subroutes
  - `public-function-bank-registry` remains the unresolved member registry

Next possible cleanup:

- update references to point at the superfamily first, and the historical subfiles second if needed

## Candidate B: Derivative Route Stack

Likely cluster:

- `derivative-series-route-taxonomy`
- `public-derivative-taxonomy-registry`
- `mean-value-models`
- `starting-line-patterns`
- `constructive-surrogates`
- `shape-behavior-microclusters`

Why:

- these are all route families around derivative, monotonicity, and graph behavior

Recommendation:

- first-pass consolidation now active:
  - `derivative-route-superfamily` is now the top-level surface
  - `derivative-series-route-taxonomy` provides the route-taxonomy logic
  - `mean-value-models`, `starting-line-patterns`, `constructive-surrogates`, `same-function-comparison`, `isomorphic-shape-families`, `math-physics-bridges`, and `shape-behavior-microclusters` are subroutes / bridge modules

Next possible cleanup:

- update references to point at the superfamily first, and the historical files second if needed

## Candidate C: Symmetry Stack

Likely cluster:

- `symmetry-clusters`
- `symmetry-to-periodicity`
- `symmetric-construction`

Why:

- all are symmetry-powered burden collapses

Recommendation:

- first-pass consolidation now complete:
  - `symmetry-clusters` is the superfamily
  - `symmetry-to-periodicity` and `symmetric-construction` are retained as submodes / subentries

Next possible cleanup:

- update references to point at the superfamily first, and the historical files second if needed

## Candidate D: Geometry-First Conic Stack

Likely cluster:

- `conic-eccentricity-clusters`
- `focus-completion`
- `focal-triangle-routes`
- `cosine-theorem-as-geometry-seal`
- `orientation-branching`
- `definition-first-triggers`
- `rectangle-midpoint-geometry`
- `special-ratio-direct-readouts`
- `graphic-shortcuts`
- `triangle-law-switch`

Why:

- these now form a genuine geometry-first subsystem

Recommendation:

- first-pass consolidation now active:
  - `geometry-first-conic-superfamily` is now the top-level surface
  - `conic-eccentricity-clusters` and `geometry-first-principle` provide the recurring geometry-first logic
  - `focus-completion`, `focal-triangle-routes`, `orientation-branching`, `definition-first-triggers`, `rectangle-midpoint-geometry`, `special-ratio-direct-readouts`, `graphic-shortcuts`, `triangle-law-switch`, `boundary-extreme-methods`, `option-backsolve`, and `special-triangle-banks` act as subroutes / seal modules

Next possible cleanup:

- update references to point at the superfamily first, and the historical subfiles second if needed

## Candidate E: Guess / Probe Stack

Likely cluster:

- `guess-policy`
- `witness-probing`
- `rapid-verification`
- `special-value-probing`
- `puzzle-assignment`
- `answer-shape-pressure`

Why:

- all are route search and cheap verification tools

Recommendation:

- first-pass consolidation now active:
  - `search-and-seal-superfamily` is now the top-level surface
  - `guess-policy` / `Guess Then Verify` provide the superfamily logic
  - `witness-probing`, `special-value-probing`, and `puzzle-assignment` act as probing subroutes
  - `answer-shape-pressure` acts as route-pressure support
  - `rapid-verification` acts as the sealing layer

Universal-age note:

- this stack should not be treated as exam-local cleverness
- it is the same move from early schooling through research:
  - guess smaller
  - probe cheaper
  - seal only the hinge

Next possible cleanup:

- introduce a single explicit `search-and-seal` superfamily surface if the current distributed references start feeling redundant

## Candidate F: System Governance Stack

Likely cluster:

- `acceptance-checklist`
- `output-protocol`
- `regression-tests`
- `test-cases`
- `shell-killing-tests`
- `low-floor-gate`
- `no-hidden-formal-imports`
- `anti-ordinary-solution-regrowth`

Why:

- these are governance and quality gates, not content primitives

Recommendation:

- first-pass consolidation now active:
  - the governance modules should be treated as one quality-system superfamily
  - `acceptance-checklist` owns acceptance
  - `output-protocol` owns answer shape and delivery
  - `regression-tests` / `test-cases` / `shell-killing-tests` own evaluation and drift detection
  - `low-floor-gate`, `no-hidden-formal-imports`, and `anti-ordinary-solution-regrowth` act as hard gates

Next possible cleanup:

- add one top-level `quality-system.md` surface that points to the existing specialized files without deleting them

## Hard Rule

Do not merge just to reduce file count.
Merge only when:

- the deeper family is clearer than the separate labels
- the lower-level distinctions are not lost
- the evidence / registry role remains explicit where needed
