# Cognitive Kernel

Mechanism-first cognitive runtime for LLMs, aimed at an early metacognitive layer.

This project is not a prompt cookbook, a math trick shelf, or a visible workflow script.

It is a thin cross-domain cognition layer that biases a model toward:

- smaller truthful carriers
- honest latent quantities
- final owner / final closure
- anti-regrowth of fake complexity
- exact cash-back to the asked interface

In plain words:

this repository tries to make a model less likely to stay trapped in surface narration,
and more likely to notice when it is still holding the wrong carrier, the wrong owner,
or only a beautiful middle object instead of the final closure.

The target is not "solve more benchmark questions by memorizing tactics."

The target is to make a model more likely to:

- peel surface costume early
- compress to the real controller
- keep primitive competition alive layer by layer
- refuse beautiful but wrong middle objects
- finish at an exact executable closure object

## Early Metacognition, Not Full AGI

This project should not be described as "already AGI."

That would be loose and unserious.

What it is trying to build is smaller and more specific:

- an early self-checking layer
- an early route-competition layer
- an early false-essence rejection layer
- an early "do not stop at the first elegant object" layer

That is why "metacognitive" is the right word here, even if the present form is still primitive.

The package is not just trying to help a model produce better answers.

It is trying to make the model more likely to monitor the shape of its own reasoning while the reasoning is happening:

- is this only surface symmetry?
- is this a local mechanism or the final owner?
- did I compress the real burden or only rename it?
- am I stopping at a strong middle carrier without exact interface closure?

That is a weak form of metacognition, but it is real.

And if systems are ever going to reason robustly in unfamiliar domains, some version of this layer is hard to avoid.

## Why This Exists

Most model improvement work helps with one or more of:

- more recall
- broader coverage
- better search
- more fluent explanation

That still does not automatically produce mechanism-first thinking.

This repository explores a different layer:

> can a reusable runtime bias make a model more likely to find the controlling structure of a problem, compress false burden, and close on the right final-answer family across domains?

Math is only one extraction field here, not the boundary of the project.

The same layer is intended to transfer across:

- algorithms
- coding / debugging
- translational research

## Why This Matters For AGI

Scaling helps models remember more, cover more, and search faster.

But those gains do not automatically force a system to:

- distrust surface costume
- search for the smallest truthful carrier
- generate rival explanations
- eliminate bad routes cheaply
- keep asking where the final authority actually lives
- cash a deep mechanism back into an exact operational answer

Those abilities sit closer to a cognition-structure problem than to a pure parameter-count problem.

This repository is an attempt to prototype that missing layer in a reusable runtime form.

So the claim is not:

> this repository is AGI

The claim is:

> if we want systems that can approach unknown hard problems more like researchers and less like giant statistical autocomplete engines, then an explicit metacognitive compression layer is probably part of the road.

## Blind-Test Snapshot

Blind parallel comparisons were run between:

- `with-skill`: this package's current local runtime surface
- `no-skill`: same model, no access to this package

Protocol:

- solve independently first
- compare only after both lanes finish
- judge against official/editorial/verified answer families when available

Current consolidated result:

- `with-skill` wins: `15`
- ties: `1`
- `no-skill` wins: `1`
- average score: `90.0` vs `83.1`

### Headline Table

| Task | With skill | No skill | Result |
| --- | ---: | ---: | --- |
| `AGC012F - Prefix Median` | 82 | 58 | with-skill |
| `AGC034F - RNG and XOR` | 97 | 94 | with-skill |
| `2026 ICPC APC M - Deformed Balance` | 84 | 49 | with-skill |
| `IOI 2018 - Werewolf` | 97 | 96 | with-skill |
| `IOI 2018 - Meetings` | 83 | 68 | with-skill |
| `IOI 2020 - Supertrees` | 96 | 94 | with-skill |
| `IOI 2020 - Biscuits` | 99 | 97 | with-skill |
| `IOI 2015 - towns` | 91 | 84 | with-skill |
| `2026 ICPC APC L - Onion` | 93 | 76 | with-skill |
| `ABC455 G - Balanced Subarrays` | 74 | 71 | with-skill |
| `Min Max Subarrays II` | 90 | 72 | with-skill |
| `JOIG Practice - Transmission` | 100 | 100 | tie |
| Django sliced `Prefetch` bug | 96 | 94 | with-skill |
| xarray MultiIndex reset bug | 71 | 93 | no-skill |
| `cGAS-STING` translational research | 94 | 88 | with-skill |
| `2026 EHEC` translational research | 91 | 88 | with-skill |
| `2026` oncolytic-virus translational research | 92 | 90 | with-skill |

The main pattern so far:

- strongest gains appear when a task rewards finding a thinner true carrier and pushing all the way to a final settlement object
- the clearest failure mode is stopping at a real local mechanism before the final authorizing boundary is fully pinned

This fits the intended identity of the package:

- not a topic skill
- not a benchmark wrapper
- not a tactic shelf
- but a small cognition bias that changes where the model settles

## Package Layout

- [SKILL.md](./SKILL.md): thin host-side entry
- [runtime/](./runtime): active cognition layer
- [benchmarks/](./benchmarks): evaluation and drift checks
- [compat/](./compat): host / runtime compatibility notes
- [references/](./references): archive and research layer, not the solve-time menu

## What The Live Runtime Actually Uses

The benchmarked active surface is intentionally small.

Core entry:

- [SKILL.md](./SKILL.md)

Core runtime bias:

- [runtime/COGNITIVE_CONSTITUTION.md](./runtime/COGNITIVE_CONSTITUTION.md)
- [runtime/CONFLICT_RESOLUTION.md](./runtime/CONFLICT_RESOLUTION.md)

These files are meant to act more like attention-shaping than like explicit route instructions.

If the package starts to feel like choosing from a shelf, it has drifted.

## Install

### Codex

Place this directory under your local Codex skills root, for example:

```text
~/.codex/skills/cognitive-kernel
```

or:

```text
~/.codex/skills/wu-boshi-perspective
```

The host entry is `SKILL.md`.

### Claude Code / compatible hosts

This repository also includes:

- [AGENTS.md](./AGENTS.md)
- [CLAUDE.md](./CLAUDE.md)
- [COMPATIBILITY.md](./COMPATIBILITY.md)

so the same package can be adapted across host runtimes without changing the core cognition layer.

## Design Stance

This repository does not want to become:

- a tactic tree
- a visible workflow
- a decomposition ritual
- a benchmark-gaming wrapper

It wants to remain:

- thin
- cross-domain
- mechanism-first
- closure-demanding
- hostile to fake essence

## Status

This is an active research runtime, not a finished universal reasoning system.

What current evidence supports:

- it can improve hard-task closure quality in blind comparison
- it transfers beyond one problem family
- it behaves more like a cognition bias layer than a topic skill shelf

What current evidence does not yet support:

- universal dominance
- stable superiority on every bug family
- full autonomous scientific discovery

## See Also

- [benchmarks/2026-05-02_SKILL_ALIGNMENT_BENCHMARK.md](./benchmarks/2026-05-02_SKILL_ALIGNMENT_BENCHMARK.md)
- [benchmarks/MULTI_AGENT_BLIND_ELIMINATION_PROTOCOL.md](./benchmarks/MULTI_AGENT_BLIND_ELIMINATION_PROTOCOL.md)
- [PACKAGE_MAP.md](./PACKAGE_MAP.md)

## Contact

If you want to discuss the project, benchmarks, transfer behavior, or the metacognitive-runtime direction, you can reach out here:

<img src="./assets/wechat-qr.jpg" alt="WeChat QR Code" width="280" />
