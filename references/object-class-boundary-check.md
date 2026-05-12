# Wu Boshi Object-Class Boundary Check

This file defines a common cross-domain failure mode:

- the route finds a good carrier
- but silently applies one elegant rule to several incompatible object classes

Then a route that looks structurally correct can still fail on important edge cases.

## 1. Core Preference

After a main carrier is chosen, keep asking:

- are all objects on this carrier really of the same kind?

If not, split them early.

Examples:

- hostname versus IP address
- finite point versus degenerate point
- empty state versus non-empty state
- local item versus remote item
- symbolic branch versus numeric branch

## 2. Why This Matters

Many failures do not come from missing the controller.

They come from:

- applying the right controller to the wrong object class

That creates false positives, false negatives, or unstable edge behavior.

## 3. Orientation Questions

Once the carrier is chosen, ask:

1. what object classes live on this carrier?
2. which classes obey the same widening or reduction law?
3. which classes need exact handling?
4. what class split would kill the biggest hidden bug here?

These are orientation questions, not fixed visible steps.

## 4. Final Preference

Prefer routes that separate incompatible object classes early when later logic depends on the distinction.
