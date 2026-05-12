AGC012F blind retest artifact

Status: unresolved

Read boundary honored:
- problem statement only
- allowed local live surface only
- no editorial / answer / discussion / blog / historical blind artifacts
- no internet search beyond directly reading the statement page

What was established

1. Small-case brute force is easy for validation.
2. A tempting formula
   - answer = product over k of distinct values in sorted_a[k..2N-k]
   - is false.
3. Counterexample to that formula:
   - N = 4
   - a = [1, 1, 1, 1, 2, 3, 3]
   - formula gives 18
   - brute force gives 17
   - the missing sequence is (2, 3, 1, 1)
4. Another useful observation from brute force:
   - for several small instances, future continuations of a median-prefix appear to depend on more than just the current median and the naive allowed interval.
   - repeated median values can reuse the same physical element, so a model that treats every median occurrence as consuming a new copy is wrong.

False leads that were explicitly killed

1. Position-only independence:
   - conjecture: any choice of median rank p_k in [k, 2N-k] is feasible
   - killed by duplicated-value cases
2. Layer independence:
   - conjecture: each stage k can choose any value appearing in sorted_a[k..2N-k], independently
   - killed by the same counterexample above
3. “Each median occurrence consumes one copy” model:
   - wrong because the same element can stay median for multiple stages

Files

- bruteforce.py
  - brute enumerator for small N
  - includes the killed formula and a validator harness

Most useful next step

- derive a correct state compression that keeps enough information about:
  - which current median element/value can persist,
  - what low/high support has already been forced,
  - and how duplicates change future flexibility.
