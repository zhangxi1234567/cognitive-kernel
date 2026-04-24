# Wu Boshi Target-Complete Main Carrier

This file defines a refinement of main-carrier choice:

- the main carrier should not only be small
- it should also be able to finish the target

A route often fails to become truly ruthless because it does something like this:

- first compress to a good small carrier
- then discover the target is not finished there
- then climb back to a heavier representation

The project should try to reduce this failure mode.

## 1. Core Preference

When choosing a main carrier, do not ask only:

- is this carrier smaller?

Also ask:

- can this carrier support the final target readout or final target proof?

If not, it may still be useful as an intermediate carrier.

But it is probably not yet the best main carrier.

## 2. What Target-Complete Means

A carrier is target-complete when:

- the target can be expressed on it
- the decisive verification can be expressed on it
- finishing the solve does not require rebuilding a heavier object without necessity

Examples:

- one parameter that already controls both the angle condition and the area
- one determinant form that already gives the final area
- one static counting carrier that already gives the target probability
- one relation carrier that already certifies the asked inequality

## 3. Common Failure

Bad pattern:

- first jump finds a small carrier
- but the route later says:
- "now let us recover full coordinates / full lengths / full cases"

This usually means:

- the chosen carrier was not yet target-complete

or:

- the route failed to notice that the target was already finishable on the smaller carrier

## 4. Selection Questions

When choosing among possible carriers, ask:

1. which carrier is smallest?
2. which carrier still holds the controller?
3. which carrier can already express the final target?
4. which carrier can already support the final seal?

The strongest carrier is often the one that answers all four well.

## 5. Final Preference

Prefer carriers that are not only small, but small enough to finish the problem.
