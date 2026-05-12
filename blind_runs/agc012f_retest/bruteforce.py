from itertools import permutations, product


def median_sequence(arr):
    n = (len(arr) + 1) // 2
    out = []
    for k in range(1, n + 1):
        pref = sorted(arr[: 2 * k - 1])
        out.append(pref[k - 1])
    return tuple(out)


def brute_sequences(arr):
    return {median_sequence(p) for p in set(permutations(arr))}


def killed_formula(arr):
    n = (len(arr) + 1) // 2
    s = sorted(arr)
    ans = 1
    for k in range(1, n + 1):
        ans *= len(set(s[k - 1 : 2 * n - k]))
    return ans


def show_counterexample():
    arr = [1, 1, 1, 1, 2, 3, 3]
    seqs = brute_sequences(arr)
    print("array:", arr)
    print("brute count:", len(seqs))
    print("killed formula:", killed_formula(arr))
    all_naive = {
        (x1, x2, x3, 1)
        for x1 in [1, 2, 3]
        for x2 in [1, 2, 3]
        for x3 in [1, 2]
    }
    print("missing from naive product model:", sorted(all_naive - seqs))


def exhaust_small(max_n=4, alphabet_max=4):
    for n in range(1, max_n + 1):
        m = 2 * n - 1
        for arr in product(range(1, alphabet_max + 1), repeat=m):
            brute = len(brute_sequences(list(arr)))
            naive = killed_formula(list(arr))
            if brute != naive:
                print("first mismatch")
                print("n =", n)
                print("arr =", arr)
                print("brute =", brute)
                print("naive =", naive)
                return
        print("no mismatch for n =", n, "alphabet <=", alphabet_max)


if __name__ == "__main__":
    show_counterexample()
