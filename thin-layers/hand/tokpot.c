/* tokpot.c -- token sets after a prefix and the least window sum one more layer can reach.
 * For each prefix: per-output |T(k)|, window sum S = sum_{k in W} |T(k)|, and the least window sum of
 * token images after any next layer (a DP over matchings, non-redundant comparators only).
 * input as tokcore.c; usage: tokpot WMASK(hex)   output: idx S minS1 |T(0)| ... |T(n-1)| */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define MAXN 16
typedef uint64_t word;
static int n, D, NW;
static uint32_t FULL, W;
typedef struct { int m; int a[MAXN / 2], b[MAXN / 2]; } Layer;
static uint32_t T[MAXN], s0[MAXN][MAXN], s1[MAXN][MAXN], nonred[MAXN];
static inline int has(const word *X, uint32_t s) { return (int)(X[s >> 6] >> (s & 63) & 1); }
static void apply_layer(const word *X, word *Y, const Layer *L) {
    memset(Y, 0, NW * sizeof(word));
    for (int w = 0; w < NW; w++) { word v = X[w]; while (v) { int b = __builtin_ctzll(v); v &= v - 1;
        uint32_t s = (uint32_t)(w * 64 + b);
        for (int c = 0; c < L->m; c++) { int i = L->a[c], j = L->b[c];
            if ((s >> i & 1) && !(s >> j & 1)) s ^= (1u << i) | (1u << j); }
        Y[s >> 6] |= 1ull << (s & 63); } }
}
static void tokens(const word *X) {
    memset(T, 0, sizeof T); memset(s0, 0, sizeof s0); memset(s1, 0, sizeof s1); memset(nonred, 0, sizeof nonred);
    for (int w = 0; w < NW; w++) { word v = X[w]; while (v) { int b = __builtin_ctzll(v); v &= v - 1;
        uint32_t s = (uint32_t)(w * 64 + b), zeros = ~s & FULL;
        for (uint32_t o = s; o; o &= o - 1) nonred[__builtin_ctz(o)] |= zeros;
        int k = n - 1 - __builtin_popcount(s);
        for (uint32_t z = zeros; z; z &= z - 1) { int j = __builtin_ctz(z);
            if (has(X, s | 1u << j)) { T[k] |= 1u << j; s0[k][j] |= zeros & ~(1u << j); s1[k][j] |= s; } } } }
}
static int cost_pair[MAXN][MAXN], cost_idle[MAXN];
static int *memo;
static int dp(uint32_t mask) {
    if (!mask) return 0;
    if (memo[mask] >= 0) return memo[mask];
    int c = __builtin_ctz(mask);
    uint32_t rest = mask & ~(1u << c);
    int best = cost_idle[c] + dp(rest);
    for (uint32_t r = rest; r; r &= r - 1) { int j = __builtin_ctz(r);
        if (!(nonred[c] >> j & 1)) continue;
        int v = cost_pair[c][j] + dp(rest & ~(1u << j));
        if (v < best) best = v; }
    return memo[mask] = best;
}
int main(int argc, char **argv) {
    W = (uint32_t)strtoul(argv[1], 0, 16);
    int P;
    if (scanf("%d %d %d", &n, &D, &P) != 3) return 1;
    NW = (1 << n) / 64; if (NW < 1) NW = 1;
    FULL = (1u << n) - 1;
    memo = malloc(sizeof(int) << n);
    static word X[1 << 11], Y[1 << 11];
    for (int idx = 0; idx < P; idx++) {
        int p; if (scanf("%d", &p) != 1) return 1;
        memset(X, 0, sizeof X);
        for (uint32_t s = 0; s < (1u << n); s++) X[s >> 6] |= 1ull << (s & 63);
        for (int l = 0; l < p; l++) { Layer L; if (scanf("%d", &L.m) != 1) return 1;
            for (int c = 0; c < L.m; c++) if (scanf("%d %d", &L.a[c], &L.b[c]) != 2) return 1;
            apply_layer(X, Y, &L); memcpy(X, Y, NW * sizeof(word)); }
        tokens(X);
        int S = 0;
        for (int k = 0; k < n; k++) if (W >> k & 1) S += __builtin_popcount(T[k]);
        for (int c = 0; c < n; c++) { cost_idle[c] = 0; for (int k = 0; k < n; k++) if (W >> k & 1) cost_idle[c] += (int)(T[k] >> c & 1); }
        for (int i = 0; i < n; i++) for (int j = i + 1; j < n; j++) { int v = 0;
            for (int k = 0; k < n; k++) if (W >> k & 1) {
                uint32_t r = 0;
                if (((s0[k][i] >> j) | (s0[k][j] >> i)) & 1) r |= 1u << j;
                if (((s1[k][i] >> j) | (s1[k][j] >> i)) & 1) r |= 1u << i;
                v += __builtin_popcount(r); }
            cost_pair[i][j] = v; }
        for (uint32_t m = 0; m < (1u << n); m++) memo[m] = -1;
        int m1 = dp(FULL);
        printf("%d %d %d", idx, S, m1);
        for (int k = 0; k < n; k++) printf(" %d", __builtin_popcount(T[k]));
        printf("\n"); fflush(stdout);
    }
    return 0;
}
