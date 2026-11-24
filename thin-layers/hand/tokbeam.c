/* tokbeam.c -- heuristic (beam) search for continuations of a prefix that pass the token cone test
 * at layer D-2: |T(k)| <= 4 and T(k) within k +- 4 for every output k (tokcore.c's bounds).  Not a
 * proof of anything when it fails; when it succeeds, the token method at D-2 cannot refute that prefix.
 * Each step proposes next layers by a min-cost matching (DP over subsets) on noisy per-pair costs:
 * the summed image sizes of all outputs' tokens, plus a penalty for images outside the cones of the
 * layer being chosen.  Keeps the B best distinct reachable sets.
 * input as tokcore.c; usage: tokbeam B C TEMP SEED   output per prefix: best penalty and sum per layer */
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define MAXN 16
#define NWMAX 256
typedef uint64_t word;
static int n, D, NW;
static double PW = 1.0;
static uint32_t FULL;
static uint32_t allowed[32][MAXN];
static int bound[32];
typedef struct { int m; int a[MAXN / 2], b[MAXN / 2]; } Layer;
typedef struct { word X[NWMAX]; Layer hist[16]; int nl; double score; int pen, sum; uint64_t h; } St;
typedef struct { uint32_t T[MAXN], s0[MAXN][MAXN], s1[MAXN][MAXN], nonred[MAXN]; } Tok;
static inline int has(const word *X, uint32_t s) { return (int)(X[s >> 6] >> (s & 63) & 1); }
static void apply_layer(const word *X, word *Y, const Layer *L) {
    memset(Y, 0, NW * sizeof(word));
    for (int w = 0; w < NW; w++) { word v = X[w]; while (v) { int b = __builtin_ctzll(v); v &= v - 1;
        uint32_t s = (uint32_t)(w * 64 + b);
        for (int c = 0; c < L->m; c++) { int i = L->a[c], j = L->b[c];
            if ((s >> i & 1) && !(s >> j & 1)) s ^= (1u << i) | (1u << j); }
        Y[s >> 6] |= 1ull << (s & 63); } }
}
static void tokens(const word *X, Tok *t) {
    memset(t, 0, sizeof *t);
    for (int w = 0; w < NW; w++) { word v = X[w]; while (v) { int b = __builtin_ctzll(v); v &= v - 1;
        uint32_t s = (uint32_t)(w * 64 + b), zeros = ~s & FULL;
        for (uint32_t o = s; o; o &= o - 1) t->nonred[__builtin_ctz(o)] |= zeros;
        int k = n - 1 - __builtin_popcount(s);
        for (uint32_t z = zeros; z; z &= z - 1) { int j = __builtin_ctz(z);
            if (has(X, s | 1u << j)) { t->T[k] |= 1u << j; t->s0[k][j] |= zeros & ~(1u << j); t->s1[k][j] |= s; } } } }
}
static int penalty(const Tok *t, int lev, int *sum) {
    int p = 0, s = 0;
    for (int k = 0; k < n; k++) { int c = __builtin_popcount(t->T[k]); s += c * c;
        if (c > bound[lev]) p += c - bound[lev];
        p += __builtin_popcount(t->T[k] & ~allowed[lev][k]); }
    *sum = s; return p;
}
static double cpair[MAXN][MAXN], cidle[MAXN];
static double *memo; static int *choice;
static double dp(uint32_t mask) {
    if (!mask) return 0;
    if (memo[mask] > -1e17) return memo[mask];
    int c = __builtin_ctz(mask); uint32_t rest = mask & ~(1u << c);
    double best = cidle[c] + dp(rest); int bc = -1;
    for (uint32_t r = rest; r; r &= r - 1) { int j = __builtin_ctz(r);
        if (cpair[c][j] > 1e17) continue;
        double v = cpair[c][j] + dp(rest & ~(1u << j));
        if (v < best) { best = v; bc = j; } }
    choice[mask] = bc; return memo[mask] = best;
}
static double rnd(void) { return (rand() + 0.5) / ((double)RAND_MAX + 1); }
static double gauss(void) { return sqrt(-2 * log(rnd())) * cos(6.283185307 * rnd()); }
static int cmp(const void *a, const void *b) { const St *x = a, *y = b; return (x->score > y->score) - (x->score < y->score); }
static uint64_t hashX(const word *X) { uint64_t h = 1469598103934665603ull; for (int i = 0; i < NW; i++) { h ^= X[i]; h *= 1099511628211ull; h ^= h >> 29; } return h; }
int main(int argc, char **argv) {
    int B = atoi(argv[1]), C = atoi(argv[2]); double temp = atof(argv[3]); srand(atoi(argv[4])); if (argc > 5) PW = atof(argv[5]);
    int P;
    if (scanf("%d %d %d", &n, &D, &P) != 3) return 1;
    NW = (1 << n) / 64; if (NW < 1) NW = 1; FULL = (1u << n) - 1;
    for (int t = 0; t <= D; t++) { int r = D - t; bound[t] = r >= 5 ? n : (1 << r); if (bound[t] > n) bound[t] = n;
        for (int k = 0; k < n; k++) { int w = r == 0 ? 0 : r == 1 ? 1 : r == 2 ? 4 : n; uint32_t m = 0;
            for (int c = 0; c < n; c++) if (c >= k - w && c <= k + w) m |= 1u << c; allowed[t][k] = m; } }
    memo = malloc(sizeof(double) << n); choice = malloc(sizeof(int) << n);
    St *beam = malloc(sizeof(St) * B), *cand = malloc(sizeof(St) * B * C);
    for (int idx = 0; idx < P; idx++) {
        int p; if (scanf("%d", &p) != 1) return 1;
        St s0; memset(&s0, 0, sizeof s0);
        for (uint32_t s = 0; s < (1u << n); s++) s0.X[s >> 6] |= 1ull << (s & 63);
        for (int l = 0; l < p; l++) { Layer L; if (scanf("%d", &L.m) != 1) return 1;
            for (int c = 0; c < L.m; c++) if (scanf("%d %d", &L.a[c], &L.b[c]) != 2) return 1;
            word Y[NWMAX]; apply_layer(s0.X, Y, &L); memcpy(s0.X, Y, NW * sizeof(word)); }
        int nb = 1; beam[0] = s0;
        printf("%d", idx);
        int passed = 0;
        for (int lev = p + 1; lev <= D - 2; lev++) {
            int nc = 0;
            for (int bi = 0; bi < nb; bi++) {
                Tok tk; tokens(beam[bi].X, &tk);
                for (int ci = 0; ci < C; ci++) {
                    double noise = ci == 0 ? 0 : temp;
                    for (int c = 0; c < n; c++) { cidle[c] = 0;
                        for (int k = 0; k < n; k++) if (tk.T[k] >> c & 1) cidle[c] += pow(__builtin_popcount(tk.T[k]), PW) + 3.0 * !(allowed[lev][k] >> c & 1); }
                    for (int i = 0; i < n; i++) for (int j = i + 1; j < n; j++) {
                        if (!(tk.nonred[i] >> j & 1)) { cpair[i][j] = 1e18; continue; }
                        double v = 0;
                        for (int k = 0; k < n; k++) { uint32_t r = 0;
                            if (((tk.s0[k][i] >> j) | (tk.s0[k][j] >> i)) & 1) r |= 1u << j;
                            if (((tk.s1[k][i] >> j) | (tk.s1[k][j] >> i)) & 1) r |= 1u << i;
                            v += pow(__builtin_popcount(tk.T[k]), PW) * __builtin_popcount(r) + 3.0 * __builtin_popcount(r & ~allowed[lev][k]); }
                        cpair[i][j] = v * (1 + noise * 0.15 * gauss()); }
                    for (uint32_t m = 0; m < (1u << n); m++) memo[m] = -1e18;
                    dp(FULL);
                    Layer L; L.m = 0; uint32_t mask = FULL;
                    while (mask) { int c = __builtin_ctz(mask); int j = choice[mask];
                        if (j < 0) mask &= ~(1u << c); else { L.a[L.m] = c; L.b[L.m] = j; L.m++; mask &= ~(1u << c) & ~(1u << j); } }
                    St *ns = &cand[nc]; apply_layer(beam[bi].X, ns->X, &L);
                    memcpy(ns->hist, beam[bi].hist, sizeof ns->hist); ns->nl = beam[bi].nl; ns->hist[ns->nl++] = L;
                    Tok t2; tokens(ns->X, &t2); ns->pen = penalty(&t2, lev, &ns->sum);
                    ns->score = 100.0 * ns->pen + ns->sum; ns->h = hashX(ns->X); nc++;
                }
            }
            qsort(cand, nc, sizeof(St), cmp);
            nb = 0;
            for (int i = 0; i < nc && nb < B; i++) { int dup = 0; for (int j = 0; j < nb; j++) if (beam[j].h == cand[i].h) { dup = 1; break; }
                if (!dup) beam[nb++] = cand[i]; }
            printf(" L%d:pen%d/sum%d", lev, beam[0].pen, beam[0].sum);
            if (lev == D - 2 && beam[0].pen == 0) passed = 1;
        }
        printf(" %s\n", passed ? "PASSES" : "-");
        { printf("  layers:"); for (int l = 0; l < beam[0].nl; l++) { printf(" ["); for (int c = 0; c < beam[0].hist[l].m; c++) printf("(%d,%d)", beam[0].hist[l].a[c], beam[0].hist[l].b[c]); printf("]"); } printf("\n"); }
        fflush(stdout);
    }
    return 0;
}
