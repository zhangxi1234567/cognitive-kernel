# False Essence Drift Tests

This file defines benchmark intentions for adversarial near-miss cases.

It is not a solve protocol.

It exists to catch regression into fake essence.

## Core Question

When several candidates look smart, can the runtime kill the impostors before settling?

## Failure Classes To Test

### 1. Local Pattern Trap

A neat family, alias, residue class, or visual pattern explains the presented case but not the real control law.

Pass condition:

- runtime rejects the local pattern unless it survives one broader-law check

### 2. False Deepening Trap

A more upstream story sounds more universal but does not improve present-task closure.

Pass condition:

- runtime prefers the nearer sufficient boundary

### 3. False Symmetry Trap

A symmetric or balanced story compresses the problem but deletes a real asymmetric witness.

Pass condition:

- runtime pressures the symmetry with one hostile asymmetric seam

### 4. Retention-Not-Validity Trap

Metadata is reattached or carried forward, but the real failure owner is the later legality test.

Pass condition:

- runtime does not stop at the retention layer if a later validity owner still governs legality

Winning refinement:

- if both a broad validator and a narrower final pinning owner exist, runtime should prefer the narrower final owner

### 5. One-Site Completion Trap

A small local patch works at one entry point but leaves the same law open nearby on the same boundary.

Pass condition:

- runtime expands only enough to close the same witnessed law across sibling entry points

## Drift Signals

The package is regressing if it:

- names elegant controllers without touching a falsifiable seam
- repeatedly chooses deeper stories that do not improve closure
- repeatedly chooses producer/translator layers over validator/legality owners
- repeatedly stops at one visible crack when the same law still leaks nearby
- explains the problem beautifully but does not change the actual repair surface or answer path

## Minimal Evidence

For each benchmarked miss, capture:

- chosen candidate boundary
- nearest rival candidate
- separating witness or kill seam
- whether closure improved at the asked interface

If the rival was never named, confidence should stay lower.

See also:

- `QUARTERLY_FREQ_WIN_NOTE.md`
