/* tokwin.c -- (window sums; derived from tokstats.c) why the median's tokens cannot shrink fast enough (efficient-prefixes.md §3).
 * For each prefix (p layers) and each non-redundant next layer A (layer p+1), for output K:
 *   t1   = |T_{p+1}(K)|,
 *   nu   = largest matching of one-sided pairs inside T_{p+1}(K)  (merge bound: |T_{p+2}| >= t1 - nu),
 *   img  = least |image of T_{p+1}(K)| over all non-redundant layers B (layer p+2),
 *   dir  = least |T_{p+2}(K)| over all such B, with T read directly from the reachable set.
 * Prints per prefix: idx, number of layers A, min t1, min (t1 - nu), min img, min dir; and a
 * histogram over all (prefix, A) of (t1 - nu, img, dir) capped at 9.
 * input as tokcore.c; usage: tokstats K */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAXN 16
typedef uint64_t word;
static int n, D, NW, K;
static uint32_t W;
static uint32_t FULL;
typedef struct { int m; int a[MAXN / 2], b[MAXN / 2]; } Layer;
typedef struct {
    uint32_t T[MAXN];
    uint32_t s0[MAXN][MAXN], s1[MAXN][MAXN];
    uint32_t nonred[MAXN];
} Tok;

static inline int has(const word *X, uint32_t s) { return (int)(X[s >> 6] >> (s & 63) & 1); }

static void apply_layer(const word *X, word *Y, const Layer *L) {
    memset(Y, 0, NW * sizeof(word));
    for (int w = 0; w < NW; w++) {
        word v = X[w];
        while (v) {
            int b = __builtin_ctzll(v);
            v &= v - 1;
            uint32_t s = (uint32_t)(w * 64 + b);
            for (int c = 0; c < L->m; c++) {
                int i = L->a[c], j = L->b[c];
                if ((s >> i & 1) && !(s >> j & 1)) s ^= (1u << i) | (1u << j);
            }
            Y[s >> 6] |= 1ull << (s & 63);
        }
    }
}

static void tokens(const word *X, Tok *t) {
    memset(t, 0, sizeof *t);
    for (int w = 0; w < NW; w++) {
        word v = X[w];
        while (v) {
            int b = __builtin_ctzll(v);
            v &= v - 1;
            uint32_t s = (uint32_t)(w * 64 + b);
            uint32_t zeros = ~s & FULL;
            for (uint32_t ones = s; ones; ones &= ones - 1) t->nonred[__builtin_ctz(ones)] |= zeros;
            int k = n - 1 - __builtin_popcount(s);
            for (uint32_t z = zeros; z; z &= z - 1) {
                int j = __builtin_ctz(z);
                if (has(X, s | 1u << j)) {
                    t->T[k] |= 1u << j;
                    t->s0[k][j] |= zeros & ~(1u << j);
                    t->s1[k][j] |= s;
                }
            }
        }
    }
}

static inline uint32_t img(const Tok *t, int k, int i, int j) {
    uint32_t r = 0;
    if (((t->s0[k][i] >> j) | (t->s0[k][j] >> i)) & 1) r |= 1u << j;
    if (((t->s1[k][i] >> j) | (t->s1[k][j] >> i)) & 1) r |= 1u << i;
    return r;
}

/* least image size over matchings B of the free channels (non-redundant comparators only) */
static int best_img(const Tok *t, int k, uint32_t used, int c) {
    while (c < n && (used >> c & 1)) c++;
    if (c == n) return 0;
    int best = (int)(t->T[k] >> c & 1) + best_img(t, k, used | 1u << c, c + 1);
    for (int j = c + 1; j < n; j++) {
        if ((used >> j & 1) || !(t->nonred[c] >> j & 1)) continue;
        int v = __builtin_popcount(img(t, k, c, j)) + best_img(t, k, used | 1u << c | 1u << j, c + 1);
        if (v < best) best = v;
    }
    return best;
}

/* largest matching of one-sided pairs inside T (both ends hold tokens, image of size 1) */
static int best_nu(const Tok *t, int k, uint32_t used, int c) {
    uint32_t T = t->T[k];
    while (c < n && ((used >> c & 1) || !(T >> c & 1))) c++;
    if (c == n) return 0;
    int best = best_nu(t, k, used | 1u << c, c + 1);
    for (int j = c + 1; j < n; j++) {
        if ((used >> j & 1) || !(T >> j & 1)) continue;
        if (__builtin_popcount(img(t, k, c, j)) != 1) continue;
        int v = 1 + best_nu(t, k, used | 1u << c | 1u << j, c + 1);
        if (v > best) best = v;
    }
    return best;
}

/* least direct |T(k)| after layer B, over non-redundant B, pruning by the image bound */
static int bestdir, bestimg, bestmax;
static Layer bestB;
static int wsum(const uint32_t *U) { int s = 0; for (int k = 0; k < n; k++) if (W >> k & 1) s += __builtin_popcount(U[k]); return s; }
static void rec_dir(const word *X, const Tok *t, Layer *L, uint32_t used, int c, const uint32_t *U) {
    while (c < n && (used >> c & 1)) c++;
    int ps = wsum(U);
    if (c == n) {
        if (ps < bestimg) bestimg = ps;
        if (ps >= bestdir) return;
        word Y[1024];
        apply_layer(X, Y, L);
        Tok t2;
        tokens(Y, &t2);
        int v = wsum(t2.T);
        if (v < bestdir) { bestdir = v; bestB = *L; }
        int mx = 0;
        for (int k = 0; k < n; k++) if ((W >> k & 1) && __builtin_popcount(t2.T[k]) > mx) mx = __builtin_popcount(t2.T[k]);
        if (mx < bestmax) bestmax = mx;
        return;
    }
    uint32_t V[MAXN];
    for (int k = 0; k < n; k++) V[k] = U[k] | (t->T[k] & 1u << c);
    rec_dir(X, t, L, used | 1u << c, c + 1, V);
    for (int j = c + 1; j < n; j++) {
        if ((used >> j & 1) || !(t->nonred[c] >> j & 1)) continue;
        for (int k = 0; k < n; k++) V[k] = U[k] | img(t, k, c, j);
        L->a[L->m] = c;
        L->b[L->m] = j;
        L->m++;
        rec_dir(X, t, L, used | 1u << c | 1u << j, c + 1, V);
        L->m--;
    }
}

static long long hist[3][10];
static int mins[4];
static long long nA;

static void rec_A(const word *X, const Tok *t, Layer *A, uint32_t used, int c) {
    while (c < n && (used >> c & 1)) c++;
    if (c == n) {
        word Y[1024];
        apply_layer(X, Y, A);
        Tok t1;
        tokens(Y, &t1);
        int a = wsum(t1.T);
        bestdir = bestimg = bestmax = 999;
        Layer B;
        B.m = 0;
        uint32_t U0[MAXN] = {0};
        rec_dir(Y, &t1, &B, 0, 0, U0);
        int b = bestimg, e = bestdir, f = bestmax;
        if (getenv("TOKWIN_VERBOSE")) {
            printf("A");
            for (int c = 0; c < A->m; c++) printf(" %d-%d", A->a[c], A->b[c]);
            printf(" | S4 %d S5min %d | B", a, e);
            for (int c = 0; c < bestB.m; c++) printf(" %d-%d", bestB.a[c], bestB.b[c]);
            printf("\n");
        }
        nA++;
        if (a < mins[0]) mins[0] = a;
        if (b < mins[1]) mins[1] = b;
        if (e < mins[2]) mins[2] = e;
        if (f < mins[3]) mins[3] = f;
        (void)b;
        return;
    }
    rec_A(X, t, A, used | 1u << c, c + 1);
    for (int j = c + 1; j < n; j++) {
        if ((used >> j & 1) || !(t->nonred[c] >> j & 1)) continue;
        A->a[A->m] = c;
        A->b[A->m] = j;
        A->m++;
        rec_A(X, t, A, used | 1u << c | 1u << j, c + 1);
        A->m--;
    }
}

int main(int argc, char **argv) {
    W = (uint32_t)strtoul(argv[1], 0, 16);
    K = 0;
    int P;
    if (scanf("%d %d %d", &n, &D, &P) != 3) return 1;
    NW = (1 << n) / 64;
    if (NW < 1) NW = 1;
    FULL = (1u << n) - 1;
    for (int idx = 0; idx < P; idx++) {
        int p;
        if (scanf("%d", &p) != 1) return 1;
        word X[1024];
        memset(X, 0, sizeof X);
        for (uint32_t s = 0; s < (1u << n); s++) X[s >> 6] |= 1ull << (s & 63);
        for (int l = 0; l < p; l++) {
            Layer L;
            if (scanf("%d", &L.m) != 1) return 1;
            for (int c = 0; c < L.m; c++)
                if (scanf("%d %d", &L.a[c], &L.b[c]) != 2) return 1;
            word Y[1024];
            apply_layer(X, Y, &L);
            memcpy(X, Y, NW * sizeof(word));
        }
        Tok t;
        tokens(X, &t);
        Layer A;
        A.m = 0;
        nA = 0;
        mins[0] = mins[1] = mins[2] = mins[3] = 99;
        rec_A(X, &t, &A, 0, 0);
        printf("%d %lld %d %d %d %d\n", idx, nA, mins[0], mins[1], mins[2], mins[3]);
        fflush(stdout);
    }

    return 0;
}
