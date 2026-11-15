/* witness_game.c -- the witness game of d13.md section 3: a relaxation of the probe condition that
 * sees some of the shared history of the channels.
 *
 * Channel c computes a monotone Boolean function f_c of the 0-1 inputs, and the ranks it can hold form
 * the interval [a_c, n-1-b_c] (d13.md Lemma 15).  Here a_c + 1 = tau0(c), the least size of a set Z of
 * inputs with f_c = 0 when Z is 0 and the rest 1, and b_c + 1 = tau1(c), the least size of a set M with
 * f_c = 1 when M is 1 and the rest 0.  The game tracks one such Z_c and one M_c per channel (initially
 * {c}); a comparator (lo, hi) gives
 *     min: Z = the smaller of Z_lo, Z_hi      M = M_lo | M_hi
 *     max: Z = Z_lo | Z_hi                    M = the smaller of M_lo, M_hi
 * since f_min = f_lo AND f_hi and f_max = f_lo OR f_hi.  These are genuine forcing sets, so
 * |Z_c| >= tau0(c) and |M_c| >= tau1(c): the game's intervals lie inside the true ones, and at each rank
 * the game counts at most as many channels as the network has.  If no prefix passes the game's
 * per-rank condition (as in probe_condition.c, mode 1), no prefix passes the real one, and D(n) > d.
 * Same enumeration as probe_condition.c (normal form of h9.md section 2).
 * usage: witness_game n d [check] [expect]
 *   check: also compare |Z_c|, |M_c| with tau0, tau1 on every prefix (exit status 1 if any is smaller);
 *   expect: the first layer that no prefix survives, or 0 if some network survives all d layers (exit
 *   status 1 if the run disagrees). */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#define MAXN 11
static int n, d, P, check;
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
static int shares(const match_t *X, const match_t *Y) {
    for (int e = 0; e < X->m; e++) for (int f = 0; f < Y->m; f++) if (X->a[e] == Y->a[f] && X->b[e] == Y->b[f]) return 1;
    return 0;
}
static int perms[120][MAXN / 2], nperm;
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
typedef struct { uint16_t Z[MAXN], M[MAXN]; } st_t;
static void step(st_t *s, const match_t *L) {
    for (int e = 0; e < L->m; e++) {
        int lo = L->a[e], hi = L->b[e];
        uint16_t zl = s->Z[lo], zh = s->Z[hi], ml = s->M[lo], mh = s->M[hi];
        s->Z[lo] = __builtin_popcount(zl) <= __builtin_popcount(zh) ? zl : zh;
        s->Z[hi] = zl | zh;
        s->M[lo] = ml | mh;
        s->M[hi] = __builtin_popcount(ml) <= __builtin_popcount(mh) ? ml : mh;
    }
}
static int ok_depth(const st_t *s, int cap) {
    if (cap >= n) return 1;
    for (int k = 0; k < n; k++) {
        int cnt = 0;
        for (int c = 0; c < n; c++) {
            int a = __builtin_popcount(s->Z[c]) - 1, b = __builtin_popcount(s->M[c]) - 1;
            if (a <= k && k <= n - 1 - b) cnt++;
        }
        if (cnt > cap) return 0;
    }
    return 1;
}
/* exact a_c, b_c for checking */
static const match_t *layers[12];
static long bad_bounds;
static void exact_check(int depth, const st_t *s) {
    int a[MAXN], b[MAXN];
    for (int c = 0; c < n; c++) { a[c] = n; b[c] = n; }
    for (uint32_t x = 0; x < (1u << n); x++) {
        uint32_t y = x;
        for (int t = 0; t < depth; t++) {
            const match_t *L = layers[t];
            for (int e = 0; e < L->m; e++) { int p = L->a[e], q = L->b[e]; if ((y >> p & 1) && !(y >> q & 1)) y ^= 1u << p | 1u << q; }
        }
        int w = __builtin_popcount(x);
        for (int c = 0; c < n; c++) {
            if (!(y >> c & 1)) { if (n - w < a[c] + 1) a[c] = n - w - 1; }   /* zeros = n-w: a+1 <= n-w */
            else { if (w < b[c] + 1) b[c] = w - 1; }
        }
    }
    for (int c = 0; c < n; c++)
        if (__builtin_popcount(s->Z[c]) - 1 < a[c] || __builtin_popcount(s->M[c]) - 1 < b[c]) bad_bounds++;
}
static long killed[12], survived[12];
static void dfs(int depth, const st_t *s) {     /* layers[0..depth-1] applied, giving s */
    if (check) exact_check(depth, s);
    if (!ok_depth(s, 1 << (d - depth))) { killed[depth]++; return; }
    survived[depth]++;
    if (depth == d) return;
    for (int i = 0; i < nall; i++) {
        if (shares(layers[depth - 1], &all[i])) continue;
        if (depth == 1 && !canonical(&all[i])) continue;
        layers[depth] = &all[i];
        st_t t = *s; step(&t, &all[i]);
        dfs(depth + 1, &t);
    }
}
int main(int argc, char **argv) {
    if (argc < 3) { fprintf(stderr, "usage: witness_game n d [check] [expect]\n"); return 2; }
    n = atoi(argv[1]); d = atoi(argv[2]); P = n / 2; int expect = -1;
    for (int i = 3; i < argc; i++) { if (!strcmp(argv[i], "check")) check = 1; else expect = atoi(argv[i]); }
    if (n < 2 || n > MAXN || d < 1 || d > 11) { fprintf(stderr, "need 2 <= n <= %d, 1 <= d <= 11\n", MAXN); return 2; }
    all = malloc(sizeof(match_t) * 100000); cur.m = 0; gen(0, 0);
    { int pp[MAXN / 2]; genperm(pp, 0, 0); }
    static match_t L1; L1.m = P; for (int e = 0; e < P; e++) { L1.a[e] = 2 * e; L1.b[e] = 2 * e + 1; }
    st_t s; for (int c = 0; c < n; c++) { s.Z[c] = s.M[c] = (uint16_t)(1u << c); }
    layers[0] = &L1; step(&s, &L1);
    dfs(1, &s);
    printf("n=%d, depth %d, witness game:", n, d);
    printf("\n  prefixes killed after layer t:"); for (int t = 1; t <= d; t++) printf(" %d:%ld", t, killed[t]);
    printf("\n  prefixes surviving after layer t:"); for (int t = 1; t <= d; t++) printf(" %d:%ld", t, survived[t]);
    if (check) printf("\n  bounds below the exact value: %ld (must be 0)", bad_bounds);
    printf("\n");
    int first = 0; for (int t = d; t >= 1; t--) if (!survived[t]) first = t;
    if (first) printf("  nothing survives layer %d", first); else printf("  some network survives all %d layers", d);
    if (expect >= 0) printf(expect == first ? " (as expected)\n" : "   UNEXPECTED (expected %d)\n", expect); else printf("\n");
    return (expect >= 0 && expect != first) || bad_bounds ? 1 : 0;
}
