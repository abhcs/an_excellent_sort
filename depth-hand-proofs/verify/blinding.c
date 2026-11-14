/* blinding.c -- can k infinities be placed on the inputs so that no comparator in layers 1..s meets
 * two real values?
 * Layer 1 is (0,1),(2,3),... with m1 comparators (default floor(n/2), i.e. maximal).  Layers 2..s-1
 * range over every matching with at most `cap` comparators (default floor(n/2)); layer s ranges over
 * the maximal matchings only, which suffices: a placement that keeps the reals apart in a maximal
 * matching does so in every sub-matching, and every matching extends to a maximal one.
 * Prints how many prefixes (L2..Ls) admit no good placement.
 *   Lemma 1 (two layers, floor(n/2) infinities):  blinding n 2 n/2         -> 0 failures, n <= 11
 *   three layers on 7 channels, 4 infinities:      blinding 7 3 4           -> 24 failures
 *   three layers on 11 channels, 6 infinities:     blinding 11 3 6          -> ~4.07e6 failures
 *   the D(11) residual (two thin layers on 9):     blinding 9 3 4 3 3       -> 451008 failures
 *   four layers on 9 channels, 6 infinities:       blinding 9 4 6           -> 0 failures (2 min)
 * usage: blinding n s k [m1 [cap]] */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
static int n, s, k, m1, cap;
typedef struct { int m; int a[8], b[8]; } match_t;
static match_t *all, *maxm, curm; static int nall, nmax;
static void gen(int used, int start, int maxonly) {
    int first = -1;
    for (int i = start; i < n; i++) if (!(used >> i & 1)) { first = i; break; }
    if (first < 0) {
        if (maxonly) { if (curm.m == n / 2) maxm[nmax++] = curm; }
        else all[nall++] = curm;
        return;
    }
    gen(used | 1 << first, first + 1, maxonly);
    for (int j = first + 1; j < n; j++) if (!(used >> j & 1)) {
        curm.a[curm.m] = first; curm.b[curm.m] = j; curm.m++;
        gen(used | 1 << first | 1 << j, first + 1, maxonly);
        curm.m--;
    }
}
typedef struct { uint16_t pos, plus; } cfg_t;   /* channels holding an infinity; which are +inf */
static int step(cfg_t *c, const match_t *M) {   /* -1 if a comparator meets two reals */
    uint16_t pos = c->pos, plus = c->plus;
    for (int e = 0; e < M->m; e++) {
        int a = M->a[e], b = M->b[e];
        int ia = pos >> a & 1, ib = pos >> b & 1;
        if (!ia && !ib) return -1;
        int va = ia ? ((plus >> a & 1) ? 2 : 0) : 1;   /* -inf=0 < real=1 < +inf=2 */
        int vb = ib ? ((plus >> b & 1) ? 2 : 0) : 1;
        if (va > vb) {
            uint16_t sa = plus >> a & 1, sb = plus >> b & 1;
            pos = (pos & ~(1 << a | 1 << b)) | (ib << a) | (ia << b);
            plus = (plus & ~(1 << a | 1 << b)) | (sb << a) | (sa << b);
        }
    }
    c->pos = pos; c->plus = plus; return 0;
}
static int cmpcfg(const void *x, const void *y) {
    const cfg_t *p = x, *q = y;
    return p->pos != q->pos ? p->pos - q->pos : p->plus - q->plus;
}
static long fails, prefixes;
static cfg_t *buf[8]; static int nbuf[8];
static int dedup(cfg_t *b, int cnt) {
    qsort(b, cnt, sizeof(cfg_t), cmpcfg);
    int u = 0;
    for (int q = 0; q < cnt; q++) if (u == 0 || cmpcfg(&b[q], &b[u - 1])) b[u++] = b[q];
    return u;
}
static void dfs(int t) {          /* buf[t] = placements still good after layer t */
    int last = (t + 1 == s);
    int nm = last ? nmax : nall; match_t *ms = last ? maxm : all;
    for (int i = 0; i < nm; i++) {
        if (!last && ms[i].m > cap) continue;
        int cnt = 0;
        for (int q = 0; q < nbuf[t]; q++) {
            cfg_t c = buf[t][q];
            if (step(&c, &ms[i]) == 0) { buf[t + 1][cnt++] = c; if (last) break; }
        }
        if (last) { prefixes++; if (cnt == 0) fails++; continue; }
        nbuf[t + 1] = dedup(buf[t + 1], cnt);
        if (nbuf[t + 1] == 0) { fails++; prefixes++; continue; }   /* (counts this prefix once) */
        dfs(t + 1);
    }
}
int main(int argc, char **argv) {
    if (argc < 4) { fprintf(stderr, "usage: %s n s k [m1 [cap]]   (n <= 15, s >= 2)\n", argv[0]); return 1; }
    n = atoi(argv[1]); s = atoi(argv[2]); k = atoi(argv[3]);
    m1 = argc > 4 ? atoi(argv[4]) : n / 2; cap = argc > 5 ? atoi(argv[5]) : n / 2;
    all = malloc(sizeof(match_t) * 3000000); maxm = malloc(sizeof(match_t) * 3000000);
    curm.m = 0; gen(0, 0, 0); curm.m = 0; gen(0, 0, 1);
    match_t L1; L1.m = m1;
    for (int e = 0; e < m1; e++) { L1.a[e] = 2 * e; L1.b[e] = 2 * e + 1; }
    for (int t = 0; t <= s; t++) buf[t] = malloc(sizeof(cfg_t) * 4000000);
    int cnt = 0;
    for (int pos = 0; pos < (1 << n); pos++) if (__builtin_popcount(pos) == k)
        for (int sg = 0; sg < (1 << n); sg++) if ((sg & ~pos) == 0) {
            cfg_t c = { (uint16_t)pos, (uint16_t)sg };
            if (step(&c, &L1) == 0) buf[1][cnt++] = c;
        }
    nbuf[1] = dedup(buf[1], cnt);
    dfs(1);
    printf("n=%d, %d layers, %d infinities (%d reals), |L1|=%d, middle layers <=%d: "
           "%ld prefixes, no good placement for %ld\n", n, s, k, n - k, m1, cap, prefixes, fails);
    return 0;
}
