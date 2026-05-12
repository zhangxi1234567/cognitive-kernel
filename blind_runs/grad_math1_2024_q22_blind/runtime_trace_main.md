# Runtime Trace

## Event 1: `init`
- Time: `2026-05-11T16:13:56.153081+00:00`
- Kind: `bootstrap`
- Note: state bootstrap
- Object: `order-statistic moments of X(n)`
- Debt: materialize E[X(n)] and E[X(n)^2] cleanly enough to cash back into c
- Next bite: derive the cdf/pdf of X(n) and read out first two moments
- Winning skill: `exact_closure`
- Promoted skill: `exact_closure`
- Active primitives: `definition_as_direct_readout`, `readout`

## Event 2: `primitive:set`
- Time: `2026-05-11T16:14:10.350285+00:00`
- Kind: `mutation`
- Object: `order-statistic moments of X(n)`
- Debt: materialize E[X(n)] and E[X(n)^2] cleanly enough to cash back into c
- Next bite: derive the cdf/pdf of X(n) and read out first two moments
- Winning skill: `exact_closure`
- Promoted skill: `exact_closure`
- Active primitives: `readout`, `projection`

## Event 3: `competition:set`
- Time: `2026-05-11T16:14:10.408878+00:00`
- Kind: `mutation`
- Object: `order-statistic moments of X(n)`
- Debt: materialize E[X(n)] and E[X(n)^2] cleanly enough to cash back into c
- Next bite: derive the cdf/pdf of X(n) and read out first two moments
- Winning skill: `exact_closure`
- Promoted skill: `exact_closure`
- Active primitives: `projection`, `witness`

## Event 4: `primitive:clear`
- Time: `2026-05-11T16:14:26.706021+00:00`
- Kind: `mutation`
- Object: `order-statistic moments of X(n)`
- Debt: materialize E[X(n)] and E[X(n)^2] cleanly enough to cash back into c
- Next bite: derive the cdf/pdf of X(n) and read out first two moments
- Winning skill: `exact_closure`
- Promoted skill: `exact_closure`
- Active primitives: `definition_as_direct_readout`, `readout`

## Event 5: `competition:clear`
- Time: `2026-05-11T16:14:27.059542+00:00`
- Kind: `mutation`
- Object: `order-statistic moments of X(n)`
- Debt: materialize E[X(n)] and E[X(n)^2] cleanly enough to cash back into c
- Next bite: derive the cdf/pdf of X(n) and read out first two moments
- Winning skill: `exact_closure`
- Promoted skill: `exact_closure`
- Active primitives: `projection`, `witness`

## Event 6: `primitive:set`
- Time: `2026-05-11T16:15:03.119431+00:00`
- Kind: `mutation`
- Object: `order-statistic moments of X(n)`
- Debt: materialize E[X(n)] and E[X(n)^2] cleanly enough to cash back into c
- Next bite: derive the cdf/pdf of X(n) and read out first two moments
- Winning skill: `exact_closure`
- Promoted skill: `exact_closure`
- Active primitives: `readout`, `definition_as_direct_readout`

## Event 7: `handoff:set`
- Time: `2026-05-11T16:15:23.303684+00:00`
- Kind: `mutation`
- Object: `order-statistic moments of X(n)`
- Debt: materialize E[X(n)] and E[X(n)^2] cleanly enough to cash back into c
- Next bite: derive the cdf/pdf of X(n) and read out first two moments
- Winning skill: `exact_closure`
- Promoted skill: `exact_closure`
- Active primitives: `readout`, `definition_as_direct_readout`
- Handoff target: `asked-medium closure for the two constants c`

## Event 8: `set-output`
- Time: `2026-05-11T16:18:19.486394+00:00`
- Kind: `mutation`
- Object: `order-statistic moments of X(n)`
- Debt: materialize E[X(n)] and E[X(n)^2] cleanly enough to cash back into c
- Next bite: derive the cdf/pdf of X(n) and read out first two moments
- Winning skill: `readout`
- Active primitives: `readout`, `definition_as_direct_readout`
- Handoff target: `asked-medium closure for the two constants c`

## Event 9: `evidence:set`
- Time: `2026-05-11T16:18:20.295629+00:00`
- Kind: `mutation`
- Object: `order-statistic moments of X(n)`
- Debt: materialize E[X(n)] and E[X(n)^2] cleanly enough to cash back into c
- Next bite: derive the cdf/pdf of X(n) and read out first two moments
- Winning skill: `readout`
- Active primitives: `readout`, `definition_as_direct_readout`
- Handoff target: `asked-medium closure for the two constants c`
