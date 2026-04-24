# Wu Boshi Mistake Mining

This file defines how to use likely wrong routes as information sources for finding faster lawful routes.

## Core Principle

A bad route is not just something to avoid.
It is a clue about what the problem is really testing.

## Main Questions

Ask:

1. What standard route would most students take first?
2. Why is that route expensive?
3. What hidden structure would make that route unnecessary?
4. What does the bait tell me about the intended shortcut?

## Common Wrong-Route Families

### 1. Formula matching too early

Signal:

- the problem looks like a chapter drill

Possible truth:

- it is really comparison, counting, or invariant

### 2. Solving every variable

Signal:

- students try to reconstruct the full object

Possible truth:

- the target needs only one quantity

### 3. Expanding too early

Signal:

- bulky algebra appears immediately

Possible truth:

- factor, ratio, symmetry, or one hidden parameter is controlling everything

### 4. Process simulation

Signal:

- probability / scheduling / story problems invite step-by-step tracking

Possible truth:

- the whole thing is just a permutation, matching, or partition

### 5. Over-respecting notation

Signal:

- advanced symbols make the problem feel advanced

Possible truth:

- the core is low-level and familiar once rewritten

## Mining Rule

Turn the wrong route into a question:

- if students want to simulate, is this really a static structure?
- if students want to compute values, is this really just an ordering question?
- if students want to solve all coordinates, is this really a target-only proof?
- if students want to expand, is there a hidden aggregate?

## Use In Solve Loop

Insert after first reduction:

- `What wrong route is being baited?`
- `What would that route overcompute?`
- `What single structural move would avoid that waste?`

## Success Condition

Mistake mining is working if a standard wrong route directly reveals:

- the bottleneck
- the hidden invariant
- the wasted variable
- the wrong representation

Then the shortcut is not random.
It is a response to the bait.
