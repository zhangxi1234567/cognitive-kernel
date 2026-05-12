# Wu Boshi Single-Route Elite Execution

This file defines the project's real target state.

The project may use multi-route generation during training, debugging, or stress testing.

But the deeper goal is not:

- many routes every time

The deeper goal is:

- one strong route
- allowed to emerge early after cheap competition
- compressed continuously
- finished fast

Short version:

- the mature system should increasingly solve like a strong human in one route

## 1. Core Preference

The system should increasingly bias toward:

- catching the controller early
- activating the right skills quickly
- staying inside one strong route
- continuing compression inside that route
- reaching the answer without route sprawl

Multi-route search remains available.

It should be treated as support, not default identity.

## 2. What Single-Route Strength Means

Single-route strength does not mean:

- stubbornly following the first idea

It means:

- the first serious route is already close to the correct carrier
- later skill use happens inside that same route
- the route keeps becoming smaller without needing full restart
- nearby weak alternatives may remain provisionally alive until the lead route clears a cheap honest seam

This is closer to strong human solving:

- see the hinge
- take the right road early
- keep compressing on that road
- arrive fast

Use:

- `first-jump-main-carrier-selection.md`
- `stay-on-the-smallest-carrier.md`

when the missing issue is not whether one route exists, but whether the first route jumped onto the right carrier and stayed there.

## 3. The Desired Internal Pattern

The mature route will often feel like:

1. shell dies quickly
2. controller appears quickly
3. one main carrier is chosen
4. more skills fire inside that carrier
5. the target is read or sealed with minimal regrowth

This is different from:

- starting over with many unrelated full routes

## 4. When Multi-Route Still Matters

Multi-route generation is still useful when:

- the first route is unclear
- the route family is fragile
- the problem is unusually deceptive
- the system needs training contrast

But once one route clearly dominates, the system should usually stop spreading out and start compressing inward.

## 5. Final Preference

The project may use many routes to train stronger instinct.

But the mature behavior it wants is:

- early controller recognition
- fast skill linking
- one-route ruthless execution

Use:

- `meta-preferences-not-fixed-rules.md`

to keep this file from being misread as a solve script.
