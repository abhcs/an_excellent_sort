/* leak_blinding.c -- three-layer blinding with a budget of leaks (h9.md section 9).
 *
 * Layer 1 is (0,1)(2,3)..., maximal (Tool B).  Put k infinities on the inputs; a "leak" is a comparator
 * that meets two reals.  For every second layer L2, up to permuting the pairs of L1, and every maximal
 * third layer L3, is there a placement with at most `budget` leaks in layers 1-3?  Maximal L3 suffice:
 * a sub-matching has no more leaks, and every matching extends to a maximal one.  Counts are over all
 * pairs (L2, maximal L3), each class of L2 weighted by its size.
 *
 * With n = 13 and k = 6 there are seven reals.  Budget 0 is what D(7) >= 6 needs (they never meet in
 * layers 1-3, so at most five layers remain); budget 1 is what (P7) needs (at most six nonempty layers,
 * the first with one comparator).
 *   leak_blinding 7 4 0     ->  24 prefixes without a good placement (as `blinding 7 3 4`)
 *   leak_blinding 11 6 0    ->  4 072 260 of 371 059 920 (as `blinding 11 3 6`, README section 6)
 *   leak_blinding 13 6 0    ->  80.0% of 76 824 788 040
 *   leak_blinding 13 6 1    ->  12.4% of 76 824 788 040
 * usage: leak_blinding n k budget   (5 <= n <= 13) */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#define MAXN 13
static int n, P;
typedef struct { int m; int8_t a[MAXN / 2], b[MAXN / 2]; } match_t;
static match_t *all, *maxm, cur; static int nall, nmax;
static void gen(int used, int start, int maxonly) {
    int first = -1;
    for (int i = start; i < n; i++) if (!(used >> i & 1)) { first = i; break; }
    if (first < 0) {
        if (maxonly) { if (cur.m == P) maxm[nmax++] = cur; } else all[nall++] = cur;
        return;
    }
    gen(used | 1 << first, first + 1, maxonly);
    for (int j = first + 1; j < n; j++) if (!(used >> j & 1)) {
        cur.a[cur.m] = first; cur.b[cur.m] = j; cur.m++;
        gen(used | 1 << first | 1 << j, first + 1, maxonly);
        cur.m--;
    }
}
typedef struct { uint16_t pos, plus; int8_t leak; } cfg_t;   /* infinities, which are +inf, leaks so far */
static int step(cfg_t *c, const match_t *M) {
    uint16_t pos = c->pos, plus = c->plus; int leak = c->leak;
    for (int e = 0; e < M->m; e++) {
        int a = M->a[e], b = M->b[e];
        int ia = pos >> a & 1, ib = pos >> b & 1;
        if (!ia && !ib) { leak++; continue; }
        int va = ia ? ((plus >> a & 1) ? 2 : 0) : 1, vb = ib ? ((plus >> b & 1) ? 2 : 0) : 1;   /* -inf < real < +inf */
        if (va > vb) {
            uint16_t sa = plus >> a & 1, sb = plus >> b & 1;
            pos = (pos & ~(1 << a | 1 << b)) | (ib << a) | (ia << b);
            plus = (plus & ~(1 << a | 1 << b)) | (sb << a) | (sa << b);
        }
    }
    c->pos = pos; c->plus = plus; c->leak = leak; return leak;
}
static int cmpcfg(const void *x, const void *y) {
    const cfg_t *p = x, *q = y;
    if (p->pos != q->pos) return p->pos - q->pos;
    if (p->plus != q->plus) return p->plus - q->plus;
    return p->leak - q->leak;
}
/* L2 up to permuting the pairs of L1 (the idle channel stays): a matching is a representative if its
 * key is the least in its orbit.  Comparators that a permutation reverses are untangled (Tool C's proof),
 * which keeps the pairs and relabels only later layers, so blinding does not change. */
static int perms[720][MAXN / 2], nperm;
static void genperm(int *p, int k, int used) {
    if (k == P) { memcpy(perms[nperm++], p, sizeof(int) * P); return; }
    for (int i = 0; i < P; i++) if (!(used >> i & 1)) { p[k] = i; genperm(p, k + 1, used | 1 << i); }
}
static uint64_t image_key(const match_t *M, int q) {
    int map[MAXN], partner[MAXN];
    for (int i = 0; i < P; i++) { map[2 * i] = 2 * perms[q][i]; map[2 * i + 1] = 2 * perms[q][i] + 1; }
    if (n & 1) map[n - 1] = n - 1;
    for (int c = 0; c < n; c++) partner[c] = c;
    for (int e = 0; e < M->m; e++) { int x = map[M->a[e]], y = map[M->b[e]]; partner[x] = y; partner[y] = x; }
    uint64_t k = 0;
    for (int c = 0; c < n; c++) k = k << 4 | (uint64_t)partner[c];
    return k;
}
int main(int argc, char **argv) {
    if (argc < 4) { fprintf(stderr, "usage: %s n k budget   (5 <= n <= 13)\n", argv[0]); return 1; }
    n = atoi(argv[1]); int K = atoi(argv[2]), budget = atoi(argv[3]); P = n / 2;
    if (n < 5 || n > MAXN || K < 1 || K >= n) { fprintf(stderr, "bad arguments\n"); return 1; }
    all = malloc(sizeof(match_t) * 600000); maxm = malloc(sizeof(match_t) * 200000);
    cur.m = 0; gen(0, 0, 0); cur.m = 0; gen(0, 0, 1);
    int p[MAXN / 2]; genperm(p, 0, 0);
    match_t L1; L1.m = P;
    for (int e = 0; e < P; e++) { L1.a[e] = 2 * e; L1.b[e] = 2 * e + 1; }
    /* placements of K infinities, after layer 1, with at most `budget` leaks */
    cfg_t *c1 = malloc(sizeof(cfg_t) * 2000000); int n1 = 0;
    for (int pos = 0; pos < (1 << n); pos++) if (__builtin_popcount(pos) == K)
        for (int sg = pos; ; sg = (sg - 1) & pos) {
            cfg_t c = { (uint16_t)pos, (uint16_t)sg, 0 };
            if (step(&c, &L1) <= budget) c1[n1++] = c;
            if (sg == 0) break;
        }
    qsort(c1, n1, sizeof(cfg_t), cmpcfg);
    int u = 0; for (int q = 0; q < n1; q++) if (!u || cmpcfg(&c1[q], &c1[u - 1])) c1[u++] = c1[q];
    n1 = u;
    long reps = 0, matched = 0, repfail = 0; double prefixes = 0, fails = 0;
    static int best[1 << MAXN]; static uint16_t rlist[1 << MAXN];   /* best[R] = 1 + leaks still allowed */
    for (int i = 0; i < nall; i++) {
        uint64_t k0 = image_key(&all[i], 0), kmin = UINT64_MAX; int stab = 0;
        for (int q = 0; q < nperm; q++) { uint64_t k = image_key(&all[i], q); if (k < kmin) kmin = k; if (k == k0) stab++; }
        if (k0 != kmin) continue;          /* perms[0] is the identity */
        long orbit = nperm / stab;
        reps++; matched += orbit;
        int nr = 0;
        for (int q = 0; q < n1; q++) {
            cfg_t c = c1[q];
            if (step(&c, &all[i]) > budget) continue;
            uint16_t R = (uint16_t)(~c.pos & ((1 << n) - 1));
            int b = budget - c.leak + 1;
            if (!best[R]) rlist[nr++] = R;
            if (b > best[R]) best[R] = b;
        }
        long f = 0;
        for (int j = 0; j < nmax; j++) {
            const match_t *M = &maxm[j]; int good = 0;
            for (int r = 0; r < nr && !good; r++) {
                uint16_t R = rlist[r]; int inside = 0;
                for (int e = 0; e < M->m; e++) inside += (R >> M->a[e] & 1) & (R >> M->b[e] & 1);
                good = inside < best[R];
            }
            f += !good;
        }
        for (int r = 0; r < nr; r++) best[rlist[r]] = 0;
        prefixes += (double)orbit * nmax; fails += (double)orbit * f; repfail += f > 0;
    }
    printf("n=%d, %d infinities (%d reals), at most %d leak%s in layers 1-3: %ld classes of L2 (%ld matchings), "
           "%.0f prefixes (L2, maximal L3), no good placement for %.0f (%.4f%%), in %ld classes\n",
           n, K, n - K, budget, budget == 1 ? "" : "s", reps, matched, prefixes, fails, 100.0 * fails / prefixes, repfail);
    return matched == nall ? 0 : 1;
}
