# Compatibility Layer

This directory holds host-facing doctrine that is still alive, but should not be mistaken for the runtime cognition layer itself.

## Difference From `runtime/`

`runtime/` contains the smallest domain-agnostic cognitive surface.

`compat/` contains host-boundary and execution-boundary notes that help protect that surface from being expanded into:

- workflow
- menu logic
- visible method performance
- archive-driven route recall

## Difference From `references/`

`references/` is research/archive gravity.

`compat/` is still live package doctrine.

If a file exists mainly to shape host behavior or guard execution boundaries, it belongs here sooner than in archive.

If a file mainly studies tactics, seeds, registries, extraction, or explicit routing language, it belongs in archive.

## Tiny Checker

`check-host-contract.ps1` is a small consistency check for the allowed host-entry and compatibility surfaces only.
