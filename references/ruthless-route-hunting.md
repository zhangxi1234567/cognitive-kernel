# Wu Boshi Ruthless Route Hunting

This file defines how the project should actively search for routes that are shorter than the first good route.

The system should not be satisfied with:

- one correct route

It should ask:

- is there a more ruthless route that is still honest?

This matters because many systems can already find:

- a correct route

But the project is aiming for:

- the shortest trustworthy route

Use:

- `single-route-elite-execution.md`

to remember that route hunting is mainly a training and fallback aid; the mature target is still one-route elite execution.

## 1. Core Rule

After one correct route appears, the solver should still ask:

- what object in this route is still unnecessary?
- what variable here is still decorative?
- what step is still proving more than the target asks for?
- can one boundary, guess, or direct readout replace half this route?

If yes, then the route hunt should continue.

## 2. What Ruthless Hunting Looks Like

Ruthless route hunting is not random cleverness.

It is a targeted search for opportunities such as:

- direct target readout
- boundary collapse
- answer-shape pressure
- special-value probe
- one-parameter compression
- removing one whole reconstructed object
- replacing a full derivation with one trusted determinant relation

The point is not:

- "be clever"

The point is:

- keep removing burden until only the real hinge remains

## 3. The Three Questions After A Good Route Appears

When a route is already correct, ask:

1. can one whole layer be deleted?
2. can one whole object be avoided?
3. can one whole proof block be replaced by one seam check or one direct readout?

If the answer is yes, the route hunt is not done yet.

## 4. Typical Ruthless Upgrades

Common upgrades include:

- coordinates -> one displacement parameter
- full point coordinates -> one vector form
- full vector form -> one determinant readout
- solving two points -> solving their difference only
- solving the whole object -> solving the target projection only
- ordinary derivation -> guess plus one seam check

These are the upgrades the project should keep testing for.

## 5. Why Systems Miss Ruthless Routes

Systems often stop too early because they think:

- "the route is already correct"

This creates:

- good but not best routes

Other systems stop because:

- they fear an aggressive route may fail

That fear is reasonable.

The answer is not to suppress aggressive search.

The answer is:

- hunt aggressive routes
- then kill weak ones fast with minimal verification

## 6. Final Rule

The route hunt ends only when:

- no whole burden block can still be removed without increasing fragility too much

That is the project's real notion of ruthless.
