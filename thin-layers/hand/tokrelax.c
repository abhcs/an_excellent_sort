/* tokrelax.c -- the token cone test with rank intervals instead of reachable sets.
 * Channel c holds a token of output k after layer t iff lo_t(c) <= k <= hi_t(c), where lo (hi) is the
 * least (greatest) rank the element at c can have.  A comparator (i, j), min to i, max to j, gives
 *   min end: lo' = min(lo_i, lo_j),  hi' >= hi_i + hi_j - n      (minimal term sizes add at most)
 *   max end: hi' = max(hi_i, hi_j),  lo' <= lo_i + lo_j + 1      (minimal clause sizes add at most)
 * Taking the bounds as equalities ("independent" calculus) narrows every interval, so the counts
 * #{c : lo(c) <= k <= hi(c)} are lower bounds on |T(k)|.  This searches all later layers (all
 * comparators, no state information) for one that passes the cone bounds of tokcore.c.
 * Start intervals: MODE 0 = exact after the prefix (from the reachable set), 1 = the calculus from
 * the start.  input as tokcore.c; usage: tokrelax MODE [OUTMASK]
 * output per prefix: idx nodes_{p+1} ... nodes_D */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define MAXN 16
#define MAXD 16
typedef uint64_t word;
static int n, D, NW, MODE;
static uint32_t OUTMASK = 0xffffffffu;
static long long nodes[MAXD + 1];
static int bound[MAXD + 1];
static int lop[MAXD + 1][MAXN], hip[MAXD + 1][MAXN];   /* allowed channel window per (layer, output) */

static void search(int t, const int *lo, const int *hi);

static int ok_partial(int lev, const int *nlo, const int *nhi, uint32_t done) {
    for (int k = 0; k < n; k++) {
        if (!(OUTMASK >> k & 1)) continue;
        int cnt = 0;
        for (uint32_t d = done; d; d &= d - 1) {
            int c = __builtin_ctz(d);
            if (nlo[c] <= k && k <= nhi[c]) {
                cnt++;
                if (c < lop[lev][k] || c > hip[lev][k]) return 0;
            }
        }
        if (cnt > bound[lev]) return 0;
    }
    return 1;
}

static void rec(int t, const int *lo, const int *hi, int *nlo, int *nhi, uint32_t used) {
    int c = 0;
    while (c < n && (used >> c & 1)) c++;
    int lev = t + 1;
    if (c == n) {
        nodes[lev]++;
        if (lev < D) search(lev, nlo, nhi);
        return;
    }
    nlo[c] = lo[c]; nhi[c] = hi[c];
    if (ok_partial(lev, nlo, nhi, used | 1u << c)) rec(t, lo, hi, nlo, nhi, used | 1u << c);
    for (int j = c + 1; j < n; j++) {
        if (used >> j & 1) continue;
        nlo[c] = lo[c] < lo[j] ? lo[c] : lo[j];
        nhi[c] = hi[c] + hi[j] - n; if (nhi[c] < 0) nhi[c] = 0;
        nhi[j] = hi[c] > hi[j] ? hi[c] : hi[j];
        nlo[j] = lo[c] + lo[j] + 1; if (nlo[j] > n - 1) nlo[j] = n - 1;
        if (ok_partial(lev, nlo, nhi, used | 1u << c | 1u << j)) rec(t, lo, hi, nlo, nhi, used | 1u << c | 1u << j);
    }
}

static void search(int t, const int *lo, const int *hi) {
    int nlo[MAXN], nhi[MAXN];
    rec(t, lo, hi, nlo, nhi, 0);
}

int main(int argc, char **argv) {
    MODE = atoi(argv[1]);
    if (argc > 2) OUTMASK = (uint32_t)strtoul(argv[2], 0, 16);
    int P;
    if (scanf("%d %d %d", &n, &D, &P) != 3) return 1;
    NW = (1 << n) / 64; if (NW < 1) NW = 1;
    for (int t = 0; t <= D; t++) {
        int r = D - t;
        bound[t] = r >= 5 ? n : (1 << r); if (bound[t] > n) bound[t] = n;
        int w = r == 0 ? 0 : r == 1 ? 1 : r == 2 ? 4 : n;
        for (int k = 0; k < n; k++) { lop[t][k] = k - w; hip[t][k] = k + w; }
    }
    static word X[1024], Y[1024];
    for (int idx = 0; idx < P; idx++) {
        int p; if (scanf("%d", &p) != 1) return 1;
        int lo[MAXN], hi[MAXN];
        for (int c = 0; c < n; c++) { lo[c] = 0; hi[c] = n - 1; }
        memset(X, 0, sizeof X);
        for (uint32_t s = 0; s < (1u << n); s++) X[s >> 6] |= 1ull << (s & 63);
        for (int l = 0; l < p; l++) {
            int m; if (scanf("%d", &m) != 1) return 1;
            int a[MAXN], b[MAXN];
            for (int c = 0; c < m; c++) if (scanf("%d %d", &a[c], &b[c]) != 2) return 1;
            /* relaxed calculus through the prefix */
            for (int c = 0; c < m; c++) {
                int i = a[c], j = b[c];
                int li = lo[i], hi_ = hi[i], lj = lo[j], hj = hi[j];
                lo[i] = li < lj ? li : lj; hi[i] = hi_ + hj - n; if (hi[i] < 0) hi[i] = 0;
                hi[j] = hi_ > hj ? hi_ : hj; lo[j] = li + lj + 1; if (lo[j] > n - 1) lo[j] = n - 1;
            }
            memset(Y, 0, NW * sizeof(word));
            for (int w = 0; w < NW; w++) { word v = X[w]; while (v) { int bb = __builtin_ctzll(v); v &= v - 1;
                uint32_t s = (uint32_t)(w * 64 + bb);
                for (int c = 0; c < m; c++) if ((s >> a[c] & 1) && !(s >> b[c] & 1)) s ^= (1u << a[c]) | (1u << b[c]);
                Y[s >> 6] |= 1ull << (s & 63); } }
            memcpy(X, Y, NW * sizeof(word));
        }
        if (MODE == 0) {   /* exact intervals from the reachable set */
            for (int c = 0; c < n; c++) { lo[c] = n; hi[c] = -1; }
            for (int w = 0; w < NW; w++) { word v = X[w]; while (v) { int bb = __builtin_ctzll(v); v &= v - 1;
                uint32_t s = (uint32_t)(w * 64 + bb);
                int k = n - 1 - __builtin_popcount(s);
                for (int c = 0; c < n; c++) if (!(s >> c & 1)) { uint32_t s2 = s | 1u << c;
                    if (X[s2 >> 6] >> (s2 & 63) & 1) { if (k < lo[c]) lo[c] = k; if (k > hi[c]) hi[c] = k; } } } }
        }
        memset(nodes, 0, sizeof nodes);
        search(p, lo, hi);
        printf("%d", idx);
        for (int t = p + 1; t <= D; t++) printf(" %lld", nodes[t]);
        printf("\n"); fflush(stdout);
    }
    return 0;
}
