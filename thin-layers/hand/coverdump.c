/* perrank.c -- per-rank capacities.  For each prefix and each non-redundant layer 4: for each window rank k,
 * u_k = channels removed from T(k) by layer 4 (= |T_3(k)| - |T_4(k)| + new ones), and nu_k = largest
 * matching of pairs inside T_4(k) separated for k (the most layer 5 can remove for rank k alone).
 * Reports the largest value over layers 4 of sum_k (|T_3(k)| - |T_4(k)| + nu_k) (separate matchings per
 * rank) and of the joint quantity (one matching for all ranks).  n = 9, window {3,4,5}.
 * input as tokcore.c */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define MAXN 12
typedef uint64_t word;
static int n, NW;
typedef struct { int m; int a[MAXN / 2], b[MAXN / 2]; } Layer;
static void apply(const word *X, word *Y, const Layer *L) {
    memset(Y, 0, NW * sizeof(word));
    for (uint32_t s = 0; s < (1u << n); s++) {
        if (!(X[s >> 6] >> (s & 63) & 1)) continue;
        uint32_t t = s;
        for (int c = 0; c < L->m; c++) { int i = L->a[c], j = L->b[c];
            if ((t >> i & 1) && !(t >> j & 1)) t ^= (1u << i) | (1u << j); }
        Y[t >> 6] |= 1ull << (t & 63);
    }
}
static uint32_t T[MAXN], both1[MAXN + 1][MAXN], both0[MAXN + 1][MAXN], nonred[MAXN];
static void stats(const word *X) {
    memset(T, 0, sizeof T); memset(both1, 0, sizeof both1); memset(both0, 0, sizeof both0); memset(nonred, 0, sizeof nonred);
    uint32_t full = (1u << n) - 1;
    for (uint32_t s = 0; s < (1u << n); s++) {
        if (!(X[s >> 6] >> (s & 63) & 1)) continue;
        int w = __builtin_popcount(s); uint32_t z = ~s & full;
        for (uint32_t o = s; o; o &= o - 1) { both1[w][__builtin_ctz(o)] |= s; nonred[__builtin_ctz(o)] |= z; }
        for (uint32_t o = z; o; o &= o - 1) both0[w][__builtin_ctz(o)] |= z;
        int k = n - 1 - w;
        for (uint32_t o = z; o; o &= o - 1) { int j = __builtin_ctz(o); uint32_t s2 = s | 1u << j; if (X[s2 >> 6] >> (s2 & 63) & 1) T[k] |= 1u << j; }
    }
}
/* pair (i,j) separated for rank k: never both rank >= k (no state of weight n-k with 1 on both), or
   never both rank <= k (no state of weight n-1-k with 0 on both) */
static int sep(int k, int i, int j) { return !(both1[n - k][i] >> j & 1) || !(both0[n - 1 - k][i] >> j & 1); }
static int Wk[3] = {3, 4, 5};
static int LIMIT = 14;
static int memo[1 << MAXN];
static int matchk(int k, uint32_t mask) {   /* largest matching of k-separated pairs inside mask */
    if (!mask) return 0;
    if (memo[mask] >= 0) return memo[mask];
    int i = __builtin_ctz(mask); uint32_t rest = mask & ~(1u << i);
    int best = matchk(k, rest);
    for (uint32_t r = rest; r; r &= r - 1) { int j = __builtin_ctz(r);
        if (sep(k, i, j)) { int v = 1 + matchk(k, rest & ~(1u << j)); if (v > best) best = v; } }
    return memo[mask] = best;
}
static int matchj(uint32_t mask) {          /* one matching, units summed over the window ranks */
    if (!mask) return 0;
    if (memo[mask] >= 0) return memo[mask];
    int i = __builtin_ctz(mask); uint32_t rest = mask & ~(1u << i);
    int best = matchj(rest);
    for (uint32_t r = rest; r; r &= r - 1) { int j = __builtin_ctz(r); int u = 0;
        for (int q = 0; q < 3; q++) { int k = Wk[q]; if ((T[k] >> i & 1) && (T[k] >> j & 1) && sep(k, i, j)) u++; }
        if (u) { int v = u + matchj(rest & ~(1u << j)); if (v > best) best = v; } }
    return memo[mask] = best;
}
static Layer *ALL; static int NALL;
static void gen(Layer *cur, uint32_t used, int c) {
    while (c < n && (used >> c & 1)) c++;
    if (c >= n) { ALL[NALL++] = *cur; return; }
    gen(cur, used | 1u << c, c + 1);
    for (int j = c + 1; j < n; j++) if (!(used >> j & 1)) { cur->a[cur->m] = c; cur->b[cur->m] = j; cur->m++; gen(cur, used | 1u << c | 1u << j, c + 1); cur->m--; }
}
int main(void) {
    int D, P;
    if (getenv("LIMIT")) LIMIT = atoi(getenv("LIMIT"));
    if (scanf("%d %d %d", &n, &D, &P) != 3) return 1;
    NW = (1 << n) / 64; if (NW < 1) NW = 1;
    ALL = malloc(sizeof(Layer) * 40000); Layer cur; cur.m = 0; gen(&cur, 0, 0);
    static word X[64], Y[64];
    long long hist_sep[40] = {0}, hist_joint[40] = {0};
    for (int idx = 0; idx < P; idx++) {
        int p; if (scanf("%d", &p) != 1) return 1;
        memset(X, 0, sizeof X);
        for (uint32_t s = 0; s < (1u << n); s++) X[s >> 6] |= 1ull << (s & 63);
        for (int l = 0; l < p; l++) { Layer L; if (scanf("%d", &L.m) != 1) return 1;
            for (int c = 0; c < L.m; c++) if (scanf("%d %d", &L.a[c], &L.b[c]) != 2) return 1;
            apply(X, Y, &L); memcpy(X, Y, sizeof X); }
        stats(X);
        int T3[3]; for (int q = 0; q < 3; q++) T3[q] = __builtin_popcount(T[Wk[q]]);
        uint32_t nr0[MAXN]; memcpy(nr0, nonred, sizeof nr0);
        int maxsep = 0, maxjoint = 0;
        for (int ai = 0; ai < NALL; ai++) {
            int ok = 1;
            for (int c = 0; c < ALL[ai].m && ok; c++) ok = nr0[ALL[ai].a[c]] >> ALL[ai].b[c] & 1;
            if (!ok) continue;
            apply(X, Y, &ALL[ai]); stats(Y);
            int s = 0;
            for (int q = 0; q < 3; q++) {
                for (int m = 0; m < (1 << n); m++) memo[m] = -1;
                s += T3[q] - __builtin_popcount(T[Wk[q]]) + matchk(Wk[q], T[Wk[q]]);
            }
            for (int m = 0; m < (1 << n); m++) memo[m] = -1;
            int jn = 0; for (int q = 0; q < 3; q++) jn += T3[q] - __builtin_popcount(T[Wk[q]]);
            int S4 = 0; for (int q = 0; q < 3; q++) S4 += __builtin_popcount(T[Wk[q]]);
            int nu = matchj((1u << n) - 1);
            jn += nu;
            if (S4 - nu <= LIMIT) {
                printf("C %d %d %d %d", idx, ai, S4, nu);
                for (int i = 0; i < n; i++) for (int j = i + 1; j < n; j++) {
                    int u = 0;
                    for (int q = 0; q < 3; q++) { int k = Wk[q]; if ((T[k] >> i & 1) && (T[k] >> j & 1) && sep(k, i, j)) u++; }
                    printf(" %d", u);
                }
                printf("\n");
            }
            if (s > maxsep) maxsep = s;
            if (jn > maxjoint) maxjoint = jn;
        }
        hist_sep[maxsep]++; hist_joint[maxjoint]++;
    }
    fprintf(stderr, "done\n"); return 0;
    printf("largest removal over layers 4, separate matchings per rank:"); for (int v = 0; v < 40; v++) if (hist_sep[v]) printf(" %d:%lld", v, hist_sep[v]); printf("\n");
    printf("largest removal over layers 4, one matching for all ranks:"); for (int v = 0; v < 40; v++) if (hist_joint[v]) printf(" %d:%lld", v, hist_joint[v]); printf("\n");
    return 0;
}
