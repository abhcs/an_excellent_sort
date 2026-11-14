/* small_facts.c -- brute force over ALL comparator networks with given per-layer caps (any matching
 * of at most cap_t comparators in layer t; no maximality assumed), testing all 2^n binary inputs
 * bit-parallel.  Used for the hand-provable base facts:
 *   D(3) >= 3   : small_facts 3 1 1        -> 0 sorting networks
 *   D(5) >= 5   : small_facts 5 2 2 2 2    -> 0
 *   Lemma 3     : small_facts 5 1 1 2 2 2  -> 0
 * and for contrast small_facts 5 1 2 2 2 2 -> 360 (one thin layer is fine; two are not).
 * usage: small_facts n cap1 ... capd */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
static int n, d, cap[10], nm;
typedef struct { int m, a[4], b[4]; } match_t;
static match_t M[300], cur;
static long found;
static void gen(int used, int start) {
    int first = -1;
    for (int i = start; i < n; i++) if (!(used >> i & 1)) { first = i; break; }
    if (first < 0) { M[nm++] = cur; return; }
    gen(used | 1 << first, first + 1);
    for (int j = first + 1; j < n; j++) if (!(used >> j & 1)) {
        cur.a[cur.m] = first; cur.b[cur.m] = j; cur.m++;
        gen(used | 1 << first | 1 << j, first + 1); cur.m--;
    }
}
static void rec(int t, const uint64_t *w) {   /* w[i]: value of wire i on each of the 2^n inputs */
    if (t == d) {
        for (int i = 0; i + 1 < n; i++) if (w[i] & ~w[i + 1]) return;
        found++; return;
    }
    for (int k = 0; k < nm; k++) {
        if (M[k].m > cap[t]) continue;
        uint64_t v[8];
        for (int i = 0; i < n; i++) v[i] = w[i];
        for (int e = 0; e < M[k].m; e++) {
            int a = M[k].a[e], b = M[k].b[e];
            uint64_t x = v[a], y = v[b]; v[a] = x & y; v[b] = x | y;
        }
        rec(t + 1, v);
    }
}
int main(int argc, char **argv) {
    if (argc < 3) { fprintf(stderr, "usage: %s n cap1 ... capd (n <= 6)\n", argv[0]); return 1; }
    n = atoi(argv[1]); d = argc - 2;
    for (int t = 0; t < d; t++) cap[t] = atoi(argv[2 + t]);
    gen(0, 0);
    uint64_t w[8];
    for (int i = 0; i < n; i++) { w[i] = 0; for (int x = 0; x < (1 << n); x++) if (x >> i & 1) w[i] |= 1ULL << x; }
    rec(0, w);
    printf("n=%d, layer caps", n);
    for (int t = 0; t < d; t++) printf(" %d", cap[t]);
    printf(": %ld sorting networks among all networks with these caps\n", found);
    return 0;
}
