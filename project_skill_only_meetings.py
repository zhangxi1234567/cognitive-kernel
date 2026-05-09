#!/usr/bin/env python3
"""
IOI 2018 Meetings blind benchmark submission.

Input:
    N Q
    H_0 H_1 ... H_{N-1}
    L R      (Q lines, 0-indexed inclusive)

Output:
    One minimum total meeting cost per line.
"""

from __future__ import annotations

import sys


def query_cost(heights: list[int], left: int, right: int) -> int:
    best = None
    for meet in range(left, right + 1):
        total = heights[meet]

        current_max = heights[meet]
        for idx in range(meet - 1, left - 1, -1):
            if heights[idx] > current_max:
                current_max = heights[idx]
            total += current_max

        current_max = heights[meet]
        for idx in range(meet + 1, right + 1):
            if heights[idx] > current_max:
                current_max = heights[idx]
            total += current_max

        if best is None or total < best:
            best = total
    return 0 if best is None else best


def solve(data: list[int]) -> str:
    if not data:
        return ""
    it = iter(data)
    n = next(it)
    q = next(it)
    heights = [next(it) for _ in range(n)]
    answers = []
    for _ in range(q):
        left = next(it)
        right = next(it)
        answers.append(str(query_cost(heights, left, right)))
    return "\n".join(answers)


def main() -> None:
    data = list(map(int, sys.stdin.buffer.read().split()))
    sys.stdout.write(solve(data))


if __name__ == "__main__":
    main()
