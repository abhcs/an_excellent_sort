/* probe_condition.c -- the probe condition of d13.md section 2, on its own, for small n.
 *
 * After t layers of a sorting network of depth d, the channels that can hold the element of rank k
 * lie in the backward cone of output k, so there are at most 2^(d-t) of them (mode 1, per rank); and
 * the ranks a channel can hold lie in its forward cone, so there are at most 2^(d-t) of them (mode 2,
 * per channel).  Both are read off the probes, pairs of 0-1 inputs that differ in one bit (h9.md
 * Lemma 13): the images differ on one channel, which holds the element of rank n-1-w, where w is the
 * smaller weight.
 * Enumerates every network with L1 = (0,1)(2,3)..., L2 one matching per class up to permuting the
 * pairs of L1, and later layers any matchings (empty ones included) that repeat no comparator of the
 * layer before (the normal form of h9.md section 2), pruning a prefix as soon as the condition
 * fails.  If no network of depth d survives, then D(n) > d.
 * usage: probe_condition n d [mode [expect]]   (mode 1 = per rank, the default; 2 = per channel; 3 = both)
 * expect: the first layer that no prefix survives, or 0 if some network survives all d layers; the exit
 * status is 1 if the run disagrees. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#define MAXN 10
static int n, d, P, mode = 1;
typedef struct { int m; int8_t a[MAXN / 2], b[MAXN / 2]; } match_t;
static match_t *all, cur; static int nall;
static void gen(int used, int start) {
    int first = -1;
    for (int i = start; i < n; i++) if (!(used >> i & 1)) { first = i; break; }
    if (first < 0) { all[nall++] = cur; return; }
    gen(used | 1 << first, first + 1);
    for (int j = first + 1; j < n; j++) if (!(used >> j & 1)) {
        cur.a[cur.m] = first; cur.b[cur.m] = j; cur.m++; gen(used | 1 << first | 1 << j, first + 1); cur.m--;
    }
}
static inline uint32_t apply(uint32_t x, const match_t *M) {
    for (int e = 0; e < M->m; e++) { int a = M->a[e], b = M->b[e]; if ((x >> a & 1) && !(x >> b & 1)) x ^= 1u << a | 1u << b; }
    return x;
}
static int shares(const match_t *X, const match_t *Y) {
    for (int e = 0; e < X->m; e++) for (int f = 0; f < Y->m; f++) if (X->a[e] == Y->a[f] && X->b[e] == Y->b[f]) return 1;
    return 0;
}
/* the probes: pairs (s, t) of states, s < t differing in one bit; stored per layer depth */
typedef struct { uint32_t s, t; } pr_t;
static pr_t *buf[12]; static int nbuf[12];
static const match_t *layers[12];
static long passed, sorted_ok, killed_at[12], survived_at[12];
static int perms[120][5], nperm;
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
    uint64_t k = 0; for (int c = 0; c < n; c++) k = k << 4 | (uint64_t)partner[c];
    return k;
}
static int canonical(const match_t *M) {
    uint64_t k0 = image_key(M, 0);
    for (int q = 1; q < nperm; q++) if (image_key(M, q) < k0) return 0;
    return 1;
}
static int cmp(const void *x, const void *y) { const pr_t *p = x, *q = y; if (p->s != q->s) return p->s < q->s ? -1 : 1; return p->t < q->t ? -1 : p->t > q->t; }
static int check(int depth) {   /* condition after `depth` layers on buf[depth] */
    int cap = 1 << (d - depth); uint32_t reach[MAXN + 1] = {0}, wts[MAXN] = {0};
    for (int i = 0; i < nbuf[depth]; i++) {
        int w = __builtin_popcount(buf[depth][i].s);
        uint32_t diff = buf[depth][i].s ^ buf[depth][i].t;
        reach[w] |= diff;
        wts[__builtin_ctz(diff)] |= 1u << w;
    }
    if (mode & 1) for (int w = 0; w < n; w++) if (__builtin_popcount(reach[w]) > cap) return 0;
    if (mode & 2) for (int c = 0; c < n; c++) if (__builtin_popcount(wts[c]) > cap) return 0;
    return 1;
}
static void dfs(int depth) {          /* layers[0..depth-1] fixed; buf[depth] holds the probes after them */
    if (!check(depth)) { killed_at[depth]++; return; }
    survived_at[depth]++;
    if (depth == d) {
        passed++;
        int ok = 1;
        for (uint32_t x = 0; x < (1u << n) && ok; x++) {
            uint32_t y = x; for (int t = 0; t < d; t++) y = apply(y, layers[t]);
            int w = __builtin_popcount(x); if (y != ((1u << n) - 1) - ((1u << (n - w)) - 1)) ok = 0;
        }
        sorted_ok += ok;
        return;
    }
    for (int i = 0; i < nall; i++) {
        if (shares(layers[depth - 1], &all[i])) continue;
        if (depth == 1 && !canonical(&all[i])) continue;
        layers[depth] = &all[i];
        int c = 0;
        for (int q = 0; q < nbuf[depth]; q++) {
            pr_t p = { apply(buf[depth][q].s, &all[i]), apply(buf[depth][q].t, &all[i]) };
            buf[depth + 1][c++] = p;
        }
        qsort(buf[depth + 1], c, sizeof(pr_t), cmp);
        int u = 0; for (int q = 0; q < c; q++) if (!u || cmp(&buf[depth + 1][q], &buf[depth + 1][u - 1])) buf[depth + 1][u++] = buf[depth + 1][q];
        nbuf[depth + 1] = u;
        dfs(depth + 1);
    }
}
int main(int argc, char **argv) {
    if (argc < 3) { fprintf(stderr, "usage: probe_condition n d [mode [expect]]\n"); return 2; }
    int expect = argc > 4 ? atoi(argv[4]) : -1;
    n = atoi(argv[1]); d = atoi(argv[2]); P = n / 2; if (argc > 3) mode = atoi(argv[3]);
    if (n < 2 || n > MAXN || d < 1 || d > 11 || mode < 1 || mode > 3) { fprintf(stderr, "need 2 <= n <= %d, 1 <= d <= 11, mode 1-3\n", MAXN); return 2; }
    all = malloc(sizeof(match_t) * 100000); cur.m = 0; gen(0, 0);
    { int pp[5]; genperm(pp, 0, 0); }
    static match_t L1; L1.m = P; for (int e = 0; e < P; e++) { L1.a[e] = 2 * e; L1.b[e] = 2 * e + 1; }
    for (int t = 0; t <= d; t++) buf[t] = malloc(sizeof(pr_t) * (n << n));
    int c = 0;
    for (uint32_t x = 0; x < (1u << n); x++) for (int p = 0; p < n; p++) if (!(x >> p & 1)) {
        pr_t q = { apply(x, &L1), apply(x | 1u << p, &L1) }; buf[1][c++] = q;
    }
    qsort(buf[1], c, sizeof(pr_t), cmp);
    int u = 0; for (int q = 0; q < c; q++) if (!u || cmp(&buf[1][q], &buf[1][u - 1])) buf[1][u++] = buf[1][q];
    nbuf[1] = u; layers[0] = &L1;
    dfs(1);
    printf("n=%d, depth %d, %s: %ld networks pass at every layer, %ld of them sort", n, d,
           mode == 1 ? "per rank" : mode == 2 ? "per channel" : "per rank and per channel", passed, sorted_ok);
    printf("\n  prefixes killed after layer t:"); for (int t = 1; t <= d; t++) printf(" %d:%ld", t, killed_at[t]);
    printf("\n  prefixes surviving after layer t:"); for (int t = 1; t <= d; t++) printf(" %d:%ld", t, survived_at[t]); printf("\n");
    int first = 0; for (int t = d; t >= 1; t--) if (!survived_at[t]) first = t;
    if (first) printf("  nothing survives layer %d", first); else printf("  some network survives all %d layers", d);
    if (expect >= 0) printf(expect == first ? " (as expected)\n" : "   UNEXPECTED (expected %d)\n", expect); else printf("\n");
    return expect >= 0 && expect != first ? 1 : 0;
}
