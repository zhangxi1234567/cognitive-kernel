# Wu Boshi Exception-First Seam Check

This file defines a high-value verification preference:

- once an elegant route appears, immediately ask what exception class could still break it

This is especially valuable in:

- programming
- debugging
- protocol logic
- configuration logic

## 1. Core Preference

If a route looks clean, ask:

- what exception seam would most likely break this route first?

Examples:

- whitelist override
- null or missing state
- empty collection
- IP versus hostname
- expired key versus live key
- local versus remote object

If such a seam is obvious, test it early.

## 2. Why This Matters

This is often the difference between:

- a conceptually right route

and:

- a production-ready route

## 3. Final Preference

After elegance appears, test the most dangerous exception seam before trusting the route fully.
