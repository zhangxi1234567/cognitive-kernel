# Wu Boshi Mechanism-First Learning

This file defines the standard for teaching a model to **truly acquire** a reduction move.

The goal is not:

- "remember this trick for this kind of problem"
- "store a few elegant examples"
- "sound like a reduction-style solver"

The goal is:

- recognize the same control mechanism in a new disguise
- regenerate the reduction route without being handed the old example
- know what is preserved, what is compressed, and what would break the move

## The Core Distinction

There are two very different states:

### 1. Surface Trick Recall

The model remembers:

- one title
- one solved example
- one familiar diagram
- one chapter label

This is weak.

When the surface changes, the model:

- falls back to ordinary derivation
- forgets to call the primitive
- or forces the primitive where it does not belong

### 2. Mechanism Acquisition

The model has internalized:

- the trigger signal
- the control mechanism
- the preserved structure
- the lawful compression move
- the failure boundary
- the transfer promise

This is the target.

When the surface changes, the model can still say:

- "this is the same mechanism in different clothes"
- "the object changed, but the control variable did not"
- "the route is still legal because the preserved quantity is the same"

## The Six-Part Primitive Learning Contract

Every serious primitive should be learned through these six parts.

### 1. Trigger Signal

What visible cues should activate the primitive?

Examples:

- a 2D or 3D quantity may actually be controlled by one gap, height, projection, or section
- the surface object looks complicated but a mother object is visibly nearby
- a boundary or degenerate case makes the control relation clearer than the full object
- many visible quantities seem to hang on one hidden parameter

### 2. Control Mechanism

What actually makes the fast move true?

Examples:

- projection preserves the target-relevant readout
- degeneration exposes the hinge without changing the decision structure
- symmetry removes fake distinctions
- one aggregate controls many local quantities
- one seam is where a global claim would fail first

### 3. Preserved Structure

What remains trustworthy after the reduction?

Typical preserved items:

- order
- incidence
- partition completeness
- target-relevant ratio
- monotone orientation
- invariant quantity
- map-back relation

Without this layer, the model only has a vibe, not a lawful shortcut.

### 4. Compression Move

What burden is being deleted?

Possible answers:

- object -> relation
- 2D -> 1D
- 3D -> cross-section
- many variables -> one control axis
- many cases -> one partition law
- full derivation -> cheap comparison / count / verification

### 5. Failure Boundary

When does this move stop being safe?

Examples:

- the reduction does not preserve the asked quantity
- the degenerate case destroys the mechanism instead of exposing it
- the projection is suggestive but not controlling
- the symmetry is fake
- the guessed route separates some cases but not all

### 6. Transfer Promise

Where else should this primitive reappear?

Examples:

- school geometry -> analytic geometry -> optimization -> physics
- counting regions -> counting states -> exact cover -> combinatorial matching
- boundary probing -> parameter threshold -> instability onset -> bug divergence point

## The Learning Loop

When adding or refining a primitive, train it in this order:

1. show one seed
2. extract the mechanism
3. name what is preserved
4. state what is being compressed
5. show one failure mode
6. show one very different transfer example
7. ask the model to recognize the primitive in a new disguise

If step 7 fails, the primitive has not really been learned.

## Canonical Test Questions

To see whether the model has learned the mechanism, ask:

- what visible signal should make you try this move?
- what is the real reason it works?
- what quantity or structure is preserved?
- what burden got deleted?
- when would this move become unsafe?
- what other topic could wear the same skeleton?

If the model cannot answer these, it has learned a story, not a primitive.

## Example: "Area Can Collapse To A Line"

Weak version:

- "triangle area problems can use this trick"

Strong version:

- trigger: the area is controlled by one gap, height, projection, or boundary quantity
- mechanism: the target is linear in a lower-dimensional control variable
- preserved structure: the reduced readout still determines the asked quantity
- compression: area problem -> line / height / projection problem
- failure: the map-back from the line quantity to the target is not actually preserved
- transfer: triangle area, trapezoid area, chord-area, section-volume, flux-like readout

That is the difference between storing an example and learning a mechanism.

## Anti-Regrowth Rule

After a primitive is called, do not quietly regrow into:

- chapter-specific routine
- answer-key derivation
- local example worship

The mechanism should stay visible throughout the route.

If the explanation ends up being:

- "here is the ordinary solution, but I opened with a simpler sentence"

then the mechanism was not actually in control.

## Success Condition

Mechanism-first learning succeeds when a new problem can trigger:

- the same primitive
- for the same reason
- with the same preserved structure
- even though the object, notation, and chapter label all changed
