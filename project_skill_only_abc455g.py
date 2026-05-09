import sys


def solve_case(n, queries, arr):
    need_each = set(queries)
    need_distinct = set(queries)
    ans_each = {b: 0 for b in queries}
    ans_distinct = {b: 0 for b in queries}

    freq = [0] * (n + 1)

    for left in range(n):
        touched = []
        count_of_count = {}
        distinct = 0

        for right in range(left, n):
            x = arr[right]
            old = freq[x]
            if old == 0:
                touched.append(x)
                distinct += 1
            else:
                remaining = count_of_count[old] - 1
                if remaining:
                    count_of_count[old] = remaining
                else:
                    del count_of_count[old]

            new = old + 1
            freq[x] = new
            count_of_count[new] = count_of_count.get(new, 0) + 1

            if len(count_of_count) == 1:
                only_freq = next(iter(count_of_count))
                if only_freq in need_each:
                    ans_each[only_freq] += 1
                if distinct in need_distinct:
                    ans_distinct[distinct] += 1

        for x in touched:
            freq[x] = 0

    return ans_each, ans_distinct


def main():
    data = list(map(int, sys.stdin.buffer.read().split()))
    if not data:
        return
    t = data[0]
    idx = 1
    out = []

    for _ in range(t):
        n = data[idx]
        k = data[idx + 1]
        idx += 2
        arr = data[idx:idx + n]
        idx += n
        queries = data[idx:idx + k]
        idx += k

        ans_each, ans_distinct = solve_case(n, queries, arr)
        for b in queries:
            out.append(f"{ans_each[b]} {ans_distinct[b]}")

    sys.stdout.write("\n".join(out))


if __name__ == "__main__":
    main()
