# Wu Boshi Stay On The Smallest Carrier

This file defines a preference that becomes important after the main carrier is chosen.

Once the route has already found a smaller carrier, the route should try to stay on it.

The project should not casually:

- climb back to heavier objects
- rebuild full coordinates
- rebuild full lengths and heights
- expand into ordinary solve layers

unless correctness truly requires it.

## 1. Core Preference

When the route has already reached a smaller carrier, prefer finishing on that carrier whenever possible.

That means:

- keep the target on the small carrier
- keep verification on the small carrier
- keep later skills linked to that carrier

instead of regrowing into larger objects.

## 2. Why This Matters

Many routes compress well at first and then fail because they later say:

- now let us compute the whole thing normally

That is where real dimensional reduction is often lost.

The stronger route is often the one that asks:

- can the target be completed right here, without climbing back?

Use:

- `target-complete-main-carrier.md`

when the route is small but you still need to judge whether it is already target-complete.

## 3. Typical Failures

Common regrowth failures include:

- one parameter was found, then full point coordinates were rebuilt
- determinant form was visible, then length-height machinery was rebuilt
- relation carrier was found, then the full object was reconstructed
- local translated carrier was found, then the route expanded back into global clutter

## 4. Final Preference

Once the route becomes small, prefer staying small.
