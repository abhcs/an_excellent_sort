/* h9_blind.c -- which prefixes of an (H9) network defeat three-layer blinding?
 * Nine channels, L1 = (0,1)(2,3)(4,5) (channels 6,7,8 idle), L2 any matching with at most 3
 * comparators, L3 ANY matching (not only maximal ones).  For each prefix (L2, L3), can 4 infinities
 * be placed on the inputs so that no comparator of L1, L2, L3 meets two reals?  If so, the 5 reals
 * are sorted by layers 4..7, contradicting D(5) >= 5.
 * Prints the totals; with -l also lists every failing prefix, one per line: "L2 | L3", each a list
 * of comparators a-b.
 * usage: h9_blind [-l] */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#define N 9
typedef struct { int m; int a[4], b[4]; } match_t;
static match_t all[3000], cur; static int nall;
static void gen(int used, int start) {
    int first = -1;
    for (int i = start; i < N; i++) if (!(used >> i & 1)) { first = i; break; }
    if (first < 0) { all[nall++] = cur; return; }
    gen(used | 1 << first, first + 1);
    for (int j = first + 1; j < N; j++) if (!(used >> j & 1)) {
        cur.a[cur.m] = first; cur.b[cur.m] = j; cur.m++;
        gen(used | 1 << first | 1 << j, first + 1); cur.m--;
    }
}
typedef struct { uint16_t pos, plus; } cfg_t;
static int step(cfg_t *c, const match_t *M) {      /* -1 if a comparator meets two reals */
    uint16_t pos = c->pos, plus = c->plus;
    for (int e = 0; e < M->m; e++) {
        int a = M->a[e], b = M->b[e];
        int ia = pos >> a & 1, ib = pos >> b & 1;
        if (!ia && !ib) return -1;
        int va = ia ? ((plus >> a & 1) ? 2 : 0) : 1, vb = ib ? ((plus >> b & 1) ? 2 : 0) : 1;
        if (va > vb) {
            uint16_t sa = plus >> a & 1, sb = plus >> b & 1;
            pos = (pos & ~(1 << a | 1 << b)) | (ib << a) | (ia << b);
            plus = (plus & ~(1 << a | 1 << b)) | (sb << a) | (sa << b);
        }
    }
    c->pos = pos; c->plus = plus; return 0;
}
static int cmpcfg(const void *x, const void *y) {
    const cfg_t *p = x, *q = y; return p->pos != q->pos ? p->pos - q->pos : p->plus - q->plus;
}
static int dedup(cfg_t *b, int cnt) {
    qsort(b, cnt, sizeof(cfg_t), cmpcfg);
    int u = 0;
    for (int q = 0; q < cnt; q++) if (u == 0 || cmpcfg(&b[q], &b[u - 1])) b[u++] = b[q];
    return u;
}
static void pr(const match_t *M) {
    for (int e = 0; e < M->m; e++) printf("%s%d-%d", e ? " " : "", M->a[e], M->b[e]);
}
int main(int argc, char **argv) {
    int list = argc > 1 && !strcmp(argv[1], "-l");
    gen(0, 0);
    match_t L1 = { 3, {0, 2, 4}, {1, 3, 5} };
    static cfg_t c1[1 << 14], c2[1 << 14]; int n1 = 0;
    for (int pos = 0; pos < (1 << N); pos++) if (__builtin_popcount(pos) == 4)
        for (int sg = 0; sg < (1 << N); sg++) if ((sg & ~pos) == 0) {
            cfg_t c = { (uint16_t)pos, (uint16_t)sg };
            if (step(&c, &L1) == 0) c1[n1++] = c;
        }
    n1 = dedup(c1, n1);
    long pre = 0, fail = 0, premax = 0, failmax = 0, l2fail = 0;
    for (int i = 0; i < nall; i++) {
        if (all[i].m > 3) continue;
        int n2 = 0;
        for (int q = 0; q < n1; q++) { cfg_t c = c1[q]; if (step(&c, &all[i]) == 0) c2[n2++] = c; }
        n2 = dedup(c2, n2);
        if (n2 == 0) l2fail++;
        for (int j = 0; j < nall; j++) {
            int ok = 0;
            for (int q = 0; q < n2 && !ok; q++) { cfg_t c = c2[q]; if (step(&c, &all[j]) == 0) ok = 1; }
            pre++; if (all[j].m == 4) premax++;
            if (!ok) {
                fail++; if (all[j].m == 4) failmax++;
                if (list) { pr(&all[i]); printf(" | "); pr(&all[j]); printf("\n"); }
            }
        }
    }
    fprintf(stderr, "configurations after L1: %d; second layers with no good placement: %ld\n", n1, l2fail);
    fprintf(stderr, "L3 maximal: %ld prefixes, %ld fail; L3 any matching: %ld prefixes, %ld fail\n",
            premax, failmax, pre, fail);
    return 0;
}
