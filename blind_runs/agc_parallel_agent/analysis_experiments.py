from itertools import combinations_with_replacement, permutations


def median_sequence(perm):
    seq = []
    for i in range(1, len(perm) + 1, 2):
        prefix = sorted(perm[:i])
        seq.append(prefix[i // 2])
    return tuple(seq)


def brute_sequences(values):
    return {median_sequence(p) for p in set(permutations(values))}


def threshold_feasible_subsets(n, c):
    out = []
    for mask in range(1 << n):
        chosen = {i + 1 for i in range(n) if (mask >> i) & 1}
        is_low = [False] + [i in chosen for i in range(1, n + 1)]
        cur = {1 if is_low[1] else 0}
        ok = True
        for t in range(1, n):
            nxt = set()
            for used in cur:
                for add in (0, 1, 2):
                    total = used + add
                    if is_low[t + 1]:
                        if t + 1 <= total <= c:
                            nxt.add(total)
                    else:
                        if total <= t and total <= c:
                            nxt.add(total)
            cur = nxt
            if not cur:
                ok = False
                break
        if ok and c in cur:
            out.append(tuple(i for i in range(1, n + 1) if i in chosen))
    return out


def naive_interval_count(values):
    values = sorted(values)
    n = (len(values) + 1) // 2
    uniq = sorted(set(values))
    index = {v: i for i, v in enumerate(uniq)}
    low = [0] * (n + 1)
    high = [0] * (n + 1)
    for i in range(1, n + 1):
        low[i] = index[values[i - 1]]
        high[i] = index[values[len(values) - i]]
    mid = index[values[n - 1]]
    size = len(uniq)
    dp = [[0] * size for _ in range(size)]
    dp[mid][mid] = 1
    for i in range(n, 1, -1):
        nxt = [[0] * size for _ in range(size)]
        for l in range(size):
            for r in range(l, size):
                cur = dp[l][r]
                if not cur:
                    continue
                for x in range(low[i - 1], high[i - 1] + 1):
                    if l < x < r:
                        continue
                    nl = min(l, x)
                    nr = max(r, x)
                    nxt[nl][nr] += cur
        dp = nxt
    return sum(dp[l][r] for l in range(size) for r in range(l, size))


def demo():
    values = [1, 1, 1, 1, 2, 3, 3]
    brute = brute_sequences(values)
    print("brute count", len(brute))
    print("naive interval count", naive_interval_count(values))
    print("threshold subsets for N=5, C=4", threshold_feasible_subsets(5, 4))
    distinct = list(range(1, 8))
    print("distinct count", len(brute_sequences(distinct)))


if __name__ == "__main__":
    demo()
