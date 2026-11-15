/* h9_p7.c -- data on (P7) (h9.md section 7.5).
 *
 * (P7): no sorting network on 7 channels with at most 6 layers has at most one comparator in its first
 * layer.  Take L1 = (0,1) and forbid a comparator in two consecutive layers.
 *
 * Part 1 (why infinities are not enough).  Two infinities on the inputs, finishing with D(5) >= 5 or
 * Lemma 3, settle every pair (L2, L3) except the 300 of the two forms (alpha) and (beta) of Lemma 12, and
 * not all (L2,L3,L4) below those.
 * Part 2 (the probe argument, directly).  For every one of those 300 pairs and every L4, some output's
 * probes reach at least five channels after layer 4.  A probe is an input x of weight w and a channel p
 * with x_p = 0; inputs x and x+e_p differ after any layers in exactly one channel, and need different
 * values at output 6-w; two more layers let an output depend on at most four channels.
 * The proof as written (the reduction to six cases and the tables of appendix B) is checked by
 * h9_p7_proof.py.  Exit status 0 iff everything holds.  usage: h9_p7 */
#include <stdio.h>
#include <string.h>
#define N 7
typedef struct { int m; int a[3], b[3]; } match_t;
static match_t all[300], cur; static int nall;
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
static int layer(int *v, const match_t *M) {
    int rr = 0;
    for (int e = 0; e < M->m; e++) {
        int a = M->a[e], b = M->b[e];
        if (!v[a] && !v[b]) { rr++; continue; }
        if (v[a] > v[b]) { int t = v[a]; v[a] = v[b]; v[b] = t; }
    }
    return rr;
}
static int apply(int x, const match_t *M) {
    for (int e = 0; e < M->m; e++) { int a = M->a[e], b = M->b[e]; if ((x >> a & 1) && !(x >> b & 1)) x ^= 1 << a | 1 << b; }
    return x;
}
static int has(const match_t *M, int a, int b) { for (int e = 0; e < M->m; e++) if (M->a[e] == a && M->b[e] == b) return 1; return 0; }
static int shares(const match_t *X, const match_t *Y) { for (int e = 0; e < Y->m; e++) if (has(X, Y->a[e], Y->b[e])) return 1; return 0; }
static int pairs_up(const match_t *M, int R) {
    int cov = 0;
    for (int e = 0; e < M->m; e++) if ((R >> M->a[e] & 1) && (R >> M->b[e] & 1)) cov |= 1 << M->a[e] | 1 << M->b[e];
    return cov == R;
}

/* two infinities: reals meet in at most one of layers 1..d, or (d layers + the 6-d after) give five layers
 * whose first two have one comparator each */
static int certified(const match_t *const *L, int d) {
    for (int x = 0; x < N; x++) for (int y = x + 1; y < N; y++) for (int s = 0; s < 4; s++) {
        int v[N] = {0}; v[x] = (s & 1) ? 1 : -1; v[y] = (s & 2) ? 1 : -1;
        int q[4], m = 0;
        for (int t = 0; t < d; t++) { int c = layer(v, L[t]); if (c) q[m++] = c; }
        int total = m + (6 - d);
        if (total <= 4 || (total == 5 && m >= 2 && q[0] == 1 && q[1] == 1)) return 1;
    }
    return 0;
}
/* channels reached after the given layers by probes for output k */
static int reach(const match_t *const *L, int d, int k) {
    int w = N - 1 - k, R = 0;
    for (int x = 0; x < (1 << N); x++) if (__builtin_popcount(x) == w) for (int p = 0; p < N; p++) if (!(x >> p & 1)) {
        int y = x, z = x | 1 << p;
        for (int t = 0; t < d; t++) { y = apply(y, L[t]); z = apply(z, L[t]); }
        R |= y ^ z;
    }
    return R;
}
int main(void) {
    gen(0, 0);
    int ok = 1;
    match_t L1 = { 1, {0}, {1} };

    /* ---- Part 1 ---- */
    long pairs = 0, hard = 0, alpha = 0, beta = 0, other = 0, formA = 0, formB = 0, triples = 0, hard4 = 0;
    for (int i = 0; i < nall; i++) for (int j = 0; j < nall; j++) {
        if (shares(&L1, &all[i]) || shares(&all[i], &all[j])) continue;
        pairs++;
        int c = -1; for (int e = 0; e < all[i].m; e++) if (all[i].a[e] == 1) c = all[i].b[e];
        int isA = pairs_up(&all[i], 0x7E) && c >= 0 && pairs_up(&all[j], 0x7F & ~(1 << c));
        int isB = !isA && pairs_up(&all[i], 0x7D) && pairs_up(&all[j], 0x7E);
        formA += isA; formB += isB;
        const match_t *L[4] = { &L1, &all[i], &all[j], 0 };
        if (certified(L, 3)) continue;
        hard++;
        if (isA) alpha++; else if (isB) beta++; else other++;
        for (int k = 0; k < nall; k++) {
            if (shares(&all[j], &all[k])) continue;
            triples++; L[3] = &all[k];
            if (!certified(L, 4)) hard4++;
        }
    }
    printf("Part 1. (P7) with L1 = (0,1): %ld pairs (L2,L3); %ld without a two-infinity certificate in layers 1-3\n", pairs, hard);
    printf("  of these, %ld are of form (alpha) and %ld of form (beta) (of %ld and %ld in all), %ld of neither\n", alpha, beta, formA, formB, other);
    printf("  below them: %ld triples (L2,L3,L4), %ld without a two-infinity certificate in layers 1-4\n", triples, hard4);
    if (other || formA != alpha || formB != beta) ok = 0;

    /* ---- Part 2 ---- */
    long hp = 0, left = 0;
    for (int i = 0; i < nall; i++) for (int j = 0; j < nall; j++) {
        if (shares(&L1, &all[i]) || shares(&all[i], &all[j])) continue;
        int c = -1; for (int e = 0; e < all[i].m; e++) if (all[i].a[e] == 1) c = all[i].b[e];
        int isA = pairs_up(&all[i], 0x7E) && c >= 0 && pairs_up(&all[j], 0x7F & ~(1 << c));
        int isB = !isA && pairs_up(&all[i], 0x7D) && pairs_up(&all[j], 0x7E);
        if (!isA && !isB) continue;
        hp++;
        for (int k = 0; k < nall; k++) {
            if (shares(&all[j], &all[k])) continue;
            const match_t *L[4] = { &L1, &all[i], &all[j], &all[k] };
            int best = 0;
            for (int out = 0; out < N; out++) { int n = __builtin_popcount(reach(L, 4, out)); if (n > best) best = n; }
            if (best < 5) left++;
        }
    }
    printf("Part 2. over all %ld pairs of the two forms and every L4: %ld cases where no output's probes reach five channels\n", hp, left);
    if (left) ok = 0;

    printf(ok ? "all (P7) checks hold\n" : "SOME (P7) CHECK FAILS\n");
    return ok ? 0 : 1;
}
