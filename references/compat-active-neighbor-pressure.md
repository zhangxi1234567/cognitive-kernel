# Compat-Active Neighbor Pressure

This file defines the compatibility-active form of neighbor pressure.

Its purpose is:

- keep nearby lawful candidates exerting weak local pressure on the leading route
- prevent the local field from becoming decorative immediately

## Core Claim

Compat-only execution should already allow:

- one route to lead
- while nearby candidates still exert weak pressure on it

That pressure may come from:

- alternative readout style
- alternative seal economy
- alternative burden deletion

This is not:

- a requirement to switch
- a requirement to compare all routes explicitly

## What This Means In Compatibility Form

At the compatibility-active level, neighbor pressure means:

- the leading route is not isolated too early
- nearby lawful candidates can still test whether the lead route is truly smallest
- the field remains locally informative for a little longer

Interpretation rule:

- neighbor pressure is residual local tension
- not a requirement to manage side-routes explicitly

## Allowed Compatibility Pressure

The compatibility layer may already preserve:

- `neighbor_pressure`
- `candidate_field_liveness`
- `cluster_persistence`

These are enough to support:

- weak nearby pressure

without:

- route sprawl

## Final Rule

Compat-only execution should already let nearby candidates keep weak pressure on the leader while they are still informative.

It must not expose that pressure as workflow.
