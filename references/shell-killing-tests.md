# Wu Boshi Shell-Killing Tests

This file defines how to test whether an answer really killed the shell of a problem.

## Core Principle

The first job is not to solve.
The first job is to kill fake difficulty.

## Shell Types

Common shells:

- chapter prestige shell
- finance / probability / conic / statistics wording shell
- notation overload shell
- process-story shell
- too-many-objects shell
- advanced-language shell

## Tests

### 1. Rename Test

Can the problem be renamed in a smaller truthful way?

Examples:

- finance growth -> repeated multiplier
- probability story -> static matching count
- conic target -> one relation, not full object recovery

### 2. Burden Shift Test

Did the explanation move burden from:

- formula -> structure
- object -> relation
- process -> static state
- many variables -> one control knob
- full proof object -> target hinge

### 3. Wrapper Death Timing

Was the shell killed before the main solve started?

If not, the shell was not really killed.

### 4. Primitive Visibility

After the shell is killed, can the controlling primitive be named clearly?

### 5. Transfer Test

Would the shell-killing rename still help on a nearby problem?

If the rename only works for this exact wording, it is not a real shell-kill.

## Pass Rule

An answer passes shell-killing only if:

- it renames the problem smaller
- the rename changes the solve route
- the primitive becomes more visible after the rename

## Failure Rule

An answer fails even if correct when:

- it solves the problem before renaming it
- it names the shell but keeps solving inside the shell
- it says “本质上” but leaves the cognitive burden unchanged
