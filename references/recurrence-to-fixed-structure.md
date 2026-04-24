# Wu Boshi Recurrence To Fixed Structure

This file defines how to reduce recurrence problems to a fixed structure.

Its purpose is:

- stop treating recurrence as endless step-by-step updating
- search for the invariant, model, or stable pattern underneath the update
- compress many time steps into one fixed law

## Core Rule

When a recurrence appears, ask:

- what does one step preserve?
- what stable pattern would make the recurrence trivial?
- is this really recurrence, or a disguised arithmetic/geometric/invariant model?

Then compress:

- recurrence process -> fixed structure or model class

## Trigger Signals

- explicit step relation
- repeated update law
- sequence defined recursively
- complicated recurrence but suspiciously simple answer form

## Compression Moves

- recurrence -> arithmetic progression
- recurrence -> geometric progression
- recurrence -> fixed point
- recurrence -> invariant quantity
- recurrence -> low-period cycle

## Why It Works

- many recurrences are shells around a known model
- the update law is often cheaper to read through stability, invariance, or model calling than through raw iteration

## Good Uses

- arithmetic / geometric disguise
- constant or periodic solutions
- invariant-preserving updates
- quick multiple-choice elimination on sequences

## Failure Boundary

Do not overfire this move when:

- no stable structure actually exists
- local pattern extrapolation is misleading
- the recurrence is genuinely nonlinear and unstable

## Transfer

- school math: sequence problems
- university math: dynamical systems toy models
- cross-domain: repeated process -> stable pattern / bottleneck / invariant
