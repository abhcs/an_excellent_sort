/* subsetperm.c -- minimal reachable sets under "contains a relabelled copy" (also via complement).
 * Token sets only grow with the reachable set: if sigma(Y) is a subset of X for a channel permutation
 * sigma, every later layer gives X-tokens at least as large (after relabelling the layers), so
 * refuting Y refutes X.  Reads classes (n, count, then per class: size and the states), prints the
 * indices of classes that contain no relabelled (or complemented) copy of another class.
 * usage: subsetperm < classes.txt */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static int n, NC;
static int *sz; static uint32_t **st; static uint64_t (*bits)[8];   /* membership bitsets, n <= 9 */
static int cnt1[10000][9][10];   /* per class, channel, weight: number of states with a 1 there */
static int wcount[10000][10];
static inline int member(int c, uint32_t s) { return (int)(bits[c][s >> 6] >> (s & 63) & 1); }
static int perm[9], used[9];
static int Y, X, compY;  /* test sigma(Y') subset of X, Y' = Y or its complement */
static uint32_t mapstate(uint32_t s) { uint32_t t = 0; for (int i = 0; i < n; i++) if (s >> i & 1) t |= 1u << perm[i]; return t; }
static int rec(int i) {
    if (i == n) {
        uint32_t full = (1u << n) - 1;
        for (int k = 0; k < sz[Y]; k++) { uint32_t s = compY ? (st[Y][k] ^ full) : st[Y][k]; if (!member(X, mapstate(s))) return 0; }
        return 1;
    }
    for (int j = 0; j < n; j++) {
        if (used[j]) continue;
        int ok = 1;
        for (int w = 0; w <= n && ok; w++) {
            int wy = compY ? n - w : w;
            int cy = compY ? (wcount[Y][wy] - cnt1[Y][i][wy]) : cnt1[Y][i][w];   /* states of Y' at weight w with 1 on i */
            if (cy > cnt1[X][j][w]) ok = 0;
            int zy = (compY ? wcount[Y][wy] : wcount[Y][w]) - cy;
            if (zy > wcount[X][w] - cnt1[X][j][w]) ok = 0;
        }
        if (!ok) continue;
        used[j] = 1; perm[i] = j;
        if (rec(i + 1)) { used[j] = 0; return 1; }
        used[j] = 0;
    }
    return 0;
}
int main(void) {
    if (scanf("%d %d", &n, &NC) != 2) return 1;
    sz = malloc(sizeof(int) * NC); st = malloc(sizeof(uint32_t *) * NC); bits = calloc(NC, sizeof *bits);
    for (int c = 0; c < NC; c++) {
        if (scanf("%d", &sz[c]) != 1) return 1;
        st[c] = malloc(sizeof(uint32_t) * sz[c]);
        for (int k = 0; k < sz[c]; k++) { unsigned v; if (scanf("%u", &v) != 1) return 1; st[c][k] = v;
            bits[c][v >> 6] |= 1ull << (v & 63); int w = __builtin_popcount(v); wcount[c][w]++;
            for (int i = 0; i < n; i++) if (v >> i & 1) cnt1[c][i][w]++; }
    }
    int nmin = 0;
    for (X = 0; X < NC; X++) {
        int dominated = 0;
        for (Y = 0; Y < NC && !dominated; Y++) {
            if (Y == X || sz[Y] > sz[X]) continue;
            if (sz[Y] == sz[X] && Y > X) continue;     /* equal size: equal sets up to relabelling were merged */
            for (compY = 0; compY < 2 && !dominated; compY++) {
                int ok = 1;
                for (int w = 0; w <= n && ok; w++) if ((compY ? wcount[Y][n - w] : wcount[Y][w]) > wcount[X][w]) ok = 0;
                if (!ok) continue;
                memset(used, 0, sizeof used);
                if (rec(0)) dominated = 1;
            }
        }
        if (!dominated) { printf("%d\n", X); nmin++; fflush(stdout); }
    }
    fprintf(stderr, "%d minimal classes of %d\n", nmin, NC);
    return 0;
}
