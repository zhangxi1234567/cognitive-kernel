#include <algorithm>
#include <cstdint>
#include <iostream>
#include <string>

using namespace std;

using int64 = long long;

namespace {

constexpr int NEED_OPERAND = 0;
constexpr int NEED_OPERATOR = 1;

struct ParseInfo {
    int end_phase;
    int64 delta_p;
    int64 need_p;
};

int64 next_with_parity(int64 x, int parity) {
    if ((x & 1LL) != parity) {
        ++x;
    }
    return x;
}

ParseInfo analyze_parser(const string& s, int start_phase) {
    int phase = start_phase;
    int64 delta_p = 0;
    int64 need_p = 0;

    for (char ch : s) {
        if (ch == '(') {
            if (phase == NEED_OPERAND) {
                ++delta_p;
            } else {
                need_p = max(need_p, 1 - delta_p);
                --delta_p;
            }
        } else {
            phase ^= 1;
        }
    }

    return {phase, delta_p, need_p};
}

int64 suffix_cost(int phase, int64 p, int64 b) {
    if (phase == NEED_OPERATOR) {
        return (b - 1) + 2 * p;
    }
    if (b == 0) {
        return 3 + 2 * p;
    }
    return (b - 1) + 2 * p;
}

int64 solve_one(const string& s) {
    int64 min_pref = 0;
    int64 balance = 0;
    for (char ch : s) {
        balance += (ch == '(' ? 1 : -1);
        min_pref = min(min_pref, balance);
    }
    const int64 min_b = -min_pref;

    int64 answer = (1LL << 60);

    for (int start_phase : {NEED_OPERAND, NEED_OPERATOR}) {
        const ParseInfo info = analyze_parser(s, start_phase);
        const int end_phase = info.end_phase;
        const int64 delta_p = info.delta_p;
        const int64 need_p = info.need_p;
        const int64 low_p = max(need_p, -delta_p);
        const int64 linear_const = balance - 1 + 2 * delta_p;

        // Prefix regime A:
        // build enough leading '(' first, then only use ')' if we still have p >= b.
        if (start_phase == NEED_OPERAND) {
            const int64 p = max(low_p, min_b);
            int64 extra = 0;
            if (end_phase == NEED_OPERAND && p + balance == 0 && p - 2 < min_b) {
                extra = 4;
            }
            answer = min(answer, 4 * p + linear_const + extra);
        } else {
            const int64 p = max(low_p, min_b + 1);
            int64 extra = 0;
            if (end_phase == NEED_OPERAND && p - 1 + balance == 0 && p - 3 < min_b) {
                extra = 4;
            }
            answer = min(answer, 4 * p + linear_const + extra);
        }

        // Prefix regime B:
        // only the two smallest parities can matter, because increasing p by 2
        // increases the objective by at least 8.
        for (int shift = 0; shift <= 1; ++shift) {
            const int64 p = low_p + shift;
            int64 b = 0;
            int64 prefix_cost = 0;

            if (start_phase == NEED_OPERAND) {
                b = next_with_parity(max(min_b, p + 1), static_cast<int>(p & 1LL));
                if (b == p) {
                    b += 2;
                }
                prefix_cost = b + 4;
            } else {
                b = next_with_parity(max(min_b, p), static_cast<int>((p ^ 1LL) & 1LL));
                prefix_cost = b + 2;
            }

            const int64 final_p = p + delta_p;
            const int64 final_b = b + balance;
            if (final_p < 0 || final_b < 0) {
                continue;
            }
            answer = min(answer, prefix_cost + suffix_cost(end_phase, final_p, final_b));
        }
    }

    return answer;
}

}  // namespace

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int t;
    cin >> t;
    while (t--) {
        int n;
        string s;
        cin >> n >> s;
        cout << solve_one(s) << '\n';
    }
    return 0;
}
